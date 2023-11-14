# from kafka import KafkaConsumer
import argparse
import random
from multiprocessing import Process, Manager

from confluent_kafka import Producer

from qos_tracker import QoSTracker
from sensor_headers import SensorHeaders
from kafka_helpers import KafkaToQueueProcessor

from collections import namedtuple
from multiprocessing import Queue  # TODO: use multiprocessing queue?

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--server",
    type=str,
    default="localhost:10001,localhost:10002,localhost:10003",
    help="Kafka bootstrap server and port",
)

parser.add_argument(
    "--qos",
    type=int,
    default=1000,
    help="Target processing time (ms) for each received image. "
         "If avg processing time increases above this value, a smaller model is chosen.",
)

ModelSpec = namedtuple("ModelSpec", "name expected_processing_time")
# available_models = [ModelSpec("yolov5n", 50),
#                     ModelSpec("yolov5s", 100),
#                     ModelSpec("yolov5m", 150)]

available_models = [ModelSpec("custom-20k", 10),
                    ModelSpec("custom-300k", 20),
                    ModelSpec("custom-750k", 40),
                    # ModelSpec("yolov5n", 50),
                    # ModelSpec("yolov5s", 100),
                    # ModelSpec("yolov5m", 150),
                    ]


args = parser.parse_args()
bootstrap_servers = args.server

class Dispatcher:
    """
    Dispatches images from input queue to available yolo-models, based on target QoS.
    """
    def __init__(self, image_input_queue: Queue, qos_running_averages: dict):
        self.image_queue = image_input_queue
        self.qos_running_averages = qos_running_averages
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def start(self):
        self.service_loop()

    def service_loop(self):
        data_id = 0
        prev_model = None
        while True:
            # Get img
            data, headers = self.image_queue.get()
            img_bytes = data

            # Choose model depending on QoS requirements
            current_model = None
            print(f"QoS data (running averages): {self.qos_running_averages}")
            for model in reversed(available_models):
                # Assume that first model in this loop is the most accurate model
                current_model = model
                if current_model.name in self.qos_running_averages:
                    # Get reading from the QoS service
                    expected_processing_time = self.qos_running_averages[current_model.name]
                else:
                    expected_processing_time = 0
                if expected_processing_time < args.qos:
                    # Choose current model as it matches our qos requirements
                    break

            # Choose random model
            # index = random.randint(0, len(available_models)-1)
            # model = available_models[index]

            # Debug prints
            if current_model is not prev_model:
                print(f"Changed model from {prev_model} to {current_model}")
            prev_model = current_model

            # Send image to chosen model
            print(f"Sending image {data_id} to {current_model.name}")
            headers = SensorHeaders(current_model.name, data_id, timestamp=None)
            self.producer.produce(topic=current_model.name, value=img_bytes,
                                  headers=headers.to_bytes())
            data_id += 1


def main():
    multiprocessing_manager = Manager()  # For shared-memory variables
    qos_running_averages = multiprocessing_manager.dict()

    image_queue = Queue()
    image_reader = KafkaToQueueProcessor("camera", image_queue, bootstrap_servers)

    results_queue = Queue()
    results_reader = KafkaToQueueProcessor("yolo_results", results_queue, bootstrap_servers)

    qos_tracker = QoSTracker(results_queue, qos_running_averages)
    dispatcher = Dispatcher(image_queue, qos_running_averages)

    processes = []
    processes.append(Process(target=image_reader.start))
    processes.append(Process(target=results_reader.start))
    processes.append(Process(target=qos_tracker.start))

    for p in processes:
        p.daemon = True  # Daemon processes are closed when parent terminates
        p.start()

    dispatcher.start()


if __name__ == "__main__":
    main()
