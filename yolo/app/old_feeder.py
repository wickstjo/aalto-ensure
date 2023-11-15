from utilz.args_utils import producer_args
from utilz.dataset_utils import parse_dataset, Frame
from utilz.kafka_utils import create_producer
from utilz.misc import DayNightCycle, get_formatted_time, resource_exists
from multiprocessing import Queue
from typing import Optional
from queue import Empty
import time

def run():

    # PARSE THE PYTHON ARGS
    args = producer_args()

    # START LOADING DATASET INTO QUUEUE BUFFER
    queue = Queue(maxsize=args.queue)

    # MAKE SURE THE HDF5 DATASET EXISTS
    if not resource_exists(f'./datasets/{args.dataset}.hdf5'):
        return

    # IT DOES: GRADUALLY LOAD THE DATASET INTO THE BUFFER
    parse_dataset(args, queue)

    # CREATE KAFKA PRODUCER
    kafka_producer = create_producer(args.kafka)

    # DETERMINE TIME PARAMS
    time_between_frames = 1 / args.fps
    missed_deadlines = 0
    prev_frame_number = -1
    day_night_cycle = DayNightCycle()
    start_time = time.time() + args.delay

    # WAIT FOR THE DELAY MARGIN TO EXPIRE BEFORE STARTING
    if time.time() < start_time:
        print(f"DELAYING LAUNCH BY {args.delay} SECONDS..")

        while time.time() < start_time:
            time.sleep(start_time - time.time())

    # START ITERATING THROUGH BUFFER CONTENT
    while queue._notempty:
        try:
                
            # GET THE NEXT FRAME FROM THE QUEUE
            try:
                dataset_frame: Optional[Frame] = queue.get_nowait()
            except:
                dataset_frame = None

            # CATCH END OF QUEUE
            if dataset_frame is None:

                if args.verbose:
                    print("WARNING: Dataset reader (disk-io) cannot keep up with requested rate!")

                try:
                    dataset_frame = queue.get(block=True, timeout=5)
                except:
                    print("Queue timed out, assume that all datasets are finished")
                    break

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
                time.sleep(1/args.fps/10)  # Short sleep to avoid consuming too much cpu

            # Check day-night cycle:
            total_sensors = min(dataset_frame.total_sensors, args.max_vehicles)
            hour = int(cur_frame_number / dataset_frame.max_frames * 24)
            traffic_percentage = day_night_cycle.evaluate(hour)
            num_sensors = int(traffic_percentage[0] * total_sensors)

            print({
                'frame': cur_frame_number,
                'hour': hour,
                'traffic_percentage': traffic_percentage,
                'max_sensors': total_sensors,
                'sending': num_sensors,
                'available': len(dataset_frame.data.keys())
            })

            # Send all sensor data for this frame
            sensors_sent = 0

            for sensor_name, data in dataset_frame.data.items():
                kafka_producer.push_msg('yolo_input', data.data.tobytes())
                sensors_sent += 1

                # Limit of sensors reached for the current day-night cycle
                if num_sensors == sensors_sent:
                    break

            if cur_frame_number == dataset_frame.max_frames - 1:
                print(f"Finished sending current dataset at {get_formatted_time()}.")

        # TERMINATE MANUALLY
        except KeyboardInterrupt:
            queue.cancel_join_thread()
            print('FEEDER MANUALLY KILLED..')
            break

        # DIE PEACEFULLY WHEN QUEUE IS EMPTY
        except Empty:
            print('QUEUE WAS EMPTY FOR 5+ SECONDS, DYING..')
            break

        # SILENTLY DEAL WITH OTHER ERRORS
        except Exception as error:
            queue.cancel_join_thread()
            print('FEEDER ERROR', error)
            print('\nIF NO ERROR, QUEUE WAS EMPTY')
            break

run()