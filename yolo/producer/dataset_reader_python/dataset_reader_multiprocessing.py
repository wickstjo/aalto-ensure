"""

"""
import argparse
import json
import os.path
import time

from datetime import datetime
from typing import List, NamedTuple, Dict, Optional

import h5py
from multiprocessing import Queue, Process

from day_night_cycle import DayNightCycle
from kafka_utils import KafkaProducer, KafkaDummy

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--dataset",
    type=str,
    nargs="+",
    default=["./datasets_in_docker_image/draft_v0.1.hdf5"],
    help="Path to the dataset. You can give multiple paths separated by space.",
)

parser.add_argument(
    "--dry_run",
    action='store_true',
    default=False,
    help="Disables all Kafka-functionality for easier debugging.",
)

parser.add_argument(
    "--verbose",
    action='store_true',
    default=False,
    help="Enables more descriptive printing for easier debugging.",
)

parser.add_argument(
    "--server",
    type=str,
    default="localhost:10001,localhost:10002,localhost:10003",
    help="Kafka bootstrap server and port. You can list multiple in the same string.",
)

parser.add_argument(
    "--max_frames",
    type=int,
    default=-1,
    help="Stop reading data after this limit is reached. Default is unlimited.",
)

parser.add_argument(
    "--max_vehicles",
    type=int,
    default=-1,
    help="Limit maximum amount of sensors that are processed each frame. Maximum of day-night cycle is computed from"
         "this value. Default is unlimited.",
)

parser.add_argument(
    "--fps",
    type=float,
    default=5,
    help="Target dataset frames per second that will be fed to Kafka.",
)

parser.add_argument(
    "--repeat",
    type=int,
    default=1,
    help="Repeat all given datasets n times.",
)

parser.add_argument(
    "--buffer",
    type=int,
    default=1000,
    help="Size of the disk IO buffer in dataset frames.",
)

parser.add_argument(
    "--delay",
    type=int,
    default=5,
    help="Initial delay (seconds) before starting to feed data to Kafka. Useful for preloading data and delaying"
         "the start of the experiment.",
)
args = parser.parse_args()

class Frame(NamedTuple):
    frame_number: int
    max_frames: int
    total_sensors: int
    data: Dict[str, bytes]

def reader(dataset_path: str, buffer: Queue):
    """
    Read data from given dataset to given buffer.

    Reading is done frame-by-frame, where one frame contains data from multiple sensors.

    With large enough buffer, the disk-io should not be the bottleneck of the whole system.
    The buffer length can be limited to avoid issues with too high memory usage.
    """

    dataset = h5py.File(dataset_path, 'r')
    activity = dataset['is_enabled']
    sensors = dataset['sensors']
    total_sensors = len(sensors.keys())
    metadata = json.loads(dataset['metadata'][()])
    n_frames = metadata["n_frames"]
    sensor_names = list(dataset["sensors"].keys())
    sensor_data_iters = {key: iter(sensors[key]) for key in sensor_names}
    if args.max_frames > 0:
        n_frames = min(n_frames, args.max_frames)
    for frame in range(n_frames):
        frame_data = {}
        for sensor_name, data_iter in sensor_data_iters.items():
            active = activity[sensor_name][frame]
            if active:
                # Sensor has data for this frame only if it is marked as active
                sensor_data = next(data_iter)
                frame_data[sensor_name] = sensor_data
        frame_wrapper = Frame(frame_number=frame, max_frames=n_frames, data=frame_data, total_sensors=total_sensors)
        buffer.put(frame_wrapper, block=True)  # Block until there is space in the queue

    # print(f"Process {current_process().name} sent total of {num_data} images (DLs missed: {missed_deadlines})")
    dataset.close()
    # buffer.close()

def get_formatted_time():
    now = datetime.now()
    formatted_date = now.strftime("%A, %B %d, %Y %I:%M:%S %p")
    return formatted_date


def produce(start_time: float, fps: int, buffer: Queue):
    """
    Read data from buffer and send to kafka.

    Follows given FPS and other params.
    """
    if args.dry_run:
        print("WARNING: Using KafkaDummy, not actually sending or receiving from Kafka!")
        producer = KafkaDummy({"bootstrap.servers": args.server})
    else:
        producer = KafkaProducer({"bootstrap.servers": args.server})
    time_between_frames = 1 / fps
    missed_deadlines = 0
    prev_frame_number = -1

    day_night_cycle = DayNightCycle()

    # Wait until specified start time
    while time.time() < start_time:
        time.sleep(start_time - time.time())  # Sleep should be fine here, this should not be that time critical

    # Processing loop
    while True:
        # Get sensor data for this frame
        try:
            dataset_frame: Optional[Frame] = buffer.get_nowait()
        except:
            dataset_frame = None
        if dataset_frame is None:
            if args.verbose:
                print("WARNING: Dataset reader (disk-io) cannot keep up with requested rate!")
            try:
                dataset_frame = buffer.get(block=True, timeout=5)
            except:
                print("Queue timed out, assume that all datasets are finished")
                return

        # Check frame number and compute expected time for sending data
        cur_frame_number = dataset_frame.frame_number
        if cur_frame_number == 0:
            start_time = time.time()
            formatted_date = get_formatted_time()
            print(f"Starting to consume new dataset at {formatted_date}")
        if cur_frame_number % (dataset_frame.max_frames / 10) == 0:
            # print
            progress = cur_frame_number / dataset_frame.max_frames
            print(f"Progress: {progress * 100} %")

        elif cur_frame_number != (prev_frame_number + 1):
            print(f"WARNING: Current frame: {cur_frame_number}, but previous frame was: {prev_frame_number}")
        expected_time = start_time + cur_frame_number * time_between_frames
        prev_frame_number = cur_frame_number

        # Check that we are not already late on scheduler
        if time.time() > expected_time + time_between_frames:
            late_by_frames = (time.time() - expected_time) // time_between_frames
            print(f"Frame {cur_frame_number} was late by {late_by_frames} frames!")
            missed_deadlines += 1

        # Wait to match given fps
        while time.time() < expected_time:
            # NOTE: We could also busy-loop here, but our use case does not seem that time critical
            time.sleep(1/fps/10)  # Short sleep to avoid consuming too much cpu

        # Check day-night cycle:
        total_sensors = min(dataset_frame.total_sensors, args.max_vehicles)
        hour = int(cur_frame_number / dataset_frame.max_frames * 24)
        traffic_percentage = day_night_cycle.evaluate(hour)
        num_sensors = int(traffic_percentage * total_sensors)
        if args.verbose:
            print(f"frame: {cur_frame_number}, h:{hour}, traffic_percentage: {traffic_percentage}, max_sensors: {total_sensors}, "
                  f"sending: {num_sensors}, available: {len(dataset_frame.data.keys())}")

        # Send all sensor data for this frame
        sensors_sent = 0
        for sensor_name, data in dataset_frame.data.items():
            producer.send("camera", data.data)
            sensors_sent += 1
            if num_sensors == sensors_sent:
                # Limit of sensors reached for the current day-night cycle
                break

        # Flush to make sure data is actually delivered, before moving onto the next frame
        producer.flush()

        if cur_frame_number == dataset_frame.max_frames - 1:
            print(f"Finished sending current dataset at {get_formatted_time()}.")


def main(dataset_paths: List[str]):
    """
    Launches subprocesses for reading given datasets into Kafka.
    """
    buffer = Queue(maxsize=args.buffer)
    start_time = time.time() + args.delay
    fps = args.fps

    # Launch processes for feeding data to Kafka
    # NOTE: Kafka producer would support multithreading if needed
    processes = []
    processes.append(Process(target=produce, args=[start_time, fps, buffer]))
    for p in processes:
        p.start()

    # Launch processes for reading the datasets from disk
    # NOTE: Could also do this in the main process for easier control
    for i in range(args.repeat):
        for dataset_path in dataset_paths:
            print(f"Iteration: {i}, starting to read {dataset_path}...")
            p = Process(target=reader, args=[dataset_path, buffer])
            p.start()
            p.join()

    # Wait until all processes are done
    for p in processes:
        p.join()

def check_datasets(dataset_paths: List[str]):
    """
    A simple check that there is at least something in each given path.

    Useful for checking the datasets beforehand, instead of failing in the middle of an experiment.
    """
    ok = True
    for dataset in dataset_paths:
        if not os.path.exists(dataset):
            print(f"Dataset not found in {dataset}")
            ok = False
    return ok


if __name__ == "__main__":
    print(args.dataset)
    datasets = args.dataset
    if check_datasets(datasets):
        # Only run if all datasets are ok
        main(datasets)

