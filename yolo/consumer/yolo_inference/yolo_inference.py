# from kafka import KafkaConsumer
import argparse
import time

from confluent_kafka import Consumer, Producer
import io
from PIL import Image
from numpy import asarray
import torch

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--server",
    type=str,
    default="localhost:10001,localhost:10002,localhost:10003",
    help="Kafka bootstrap server and port",
)
parser.add_argument(
    "-m",
    "--model",
    type=str,
    default="yolov5n",
    help="Yolo model used for inference. Options: 'yolov5n', 'yolov5s', 'yolov5m'",
)

args = parser.parse_args()

class KafkaProducer:
    def __init__(self, config):
        self.kafka_client = Producer(config)

    def ack_callback(self, error, message):
        if error:
            print('ACK ERROR', error)
        else:
            # print('MESSAGE PUSHED')
            pass

    def send(self, topic_name, bytes_data):
        self.kafka_client.produce(
            topic_name,
            value=bytes_data,
            on_delivery=self.ack_callback,
        )

        # ASYNCRONOUSLY AWAIT CONSUMER ACK BEFORE SENDING NEXT MSG
        # self.kafka_client.poll(1)

class KafkaConsumer:
    def __init__(self, kafka_topic):
        self.kafka_topic = kafka_topic
        self.delivery_guarantee = 'at_most_once' # OR at_least_once

        # CREATE THE CONSUMER CLIENT
        self.kafka_client = Consumer({
            'bootstrap.servers': args.server,
            'group.id': kafka_topic + '.consumers',
            'enable.auto.commit': False,
            'on_commit': self.ack_callback,
            'auto.offset.reset': 'earliest'
        })

    def ack_callback(self, error, partitions):
        if error:
            return print('ACK ERROR', error)

    def start_consuming(self, on_message):
        available_topics = self.kafka_client.list_topics().topics.keys()
        while self.kafka_topic not in available_topics:
            available_topics = self.kafka_client.list_topics().topics.keys()
            print(f"Topic {self.kafka_topic} not in kafka -- waiting (topics: {available_topics}")
            time.sleep(1)
        self.kafka_client.subscribe([self.kafka_topic])
        print(f"Listening for messages on {self.kafka_topic}")
        while True:
            try:
                msg = self.kafka_client.poll(1)
                if msg is None:
                    continue

                if msg.error():
                    print('FAULTY MESSAGE RECEIVED', msg.error())
                    continue

                if self.delivery_guarantee == 'at_most_once':
                    self.kafka_client.commit(msg, asynchronous=True)

                on_message(msg.value(), msg.headers())

                if self.delivery_guarantee == 'at_least_once':
                    self.kafka_client.commit(msg, asynchronous=True)

            except KeyboardInterrupt:
                print('CONSUMER MANUALLY KILLED..')
                break

            except Exception as error:
                print('CONSUMER ERROR', error)
                continue

        self.kafka_client.close()


def main():
    print(args)
    model_name = args.model
    model_name = model_name.strip().rstrip()
    yolo = torch.hub.load(
        'ultralytics/yolov5', "custom", path=f'./models/{model_name}.pt')
    device = yolo.parameters().__next__().device
    print(f"Intialized {model_name} on device {device}")
    producer = KafkaProducer({"bootstrap.servers": args.server})

    def process_event(data, headers):
        recreated_headers = {key: value for key, value in headers}

        img = Image.open(io.BytesIO(data))
        results = yolo.forward(asarray(img))
        print(results)
        results_data = ""
        results_topic = f"yolo_results"
        producer.kafka_client.produce(topic=results_topic, value=results_data, headers=recreated_headers)

    topic_name = f'{model_name}'
    print(f"Starting to consume images with {args}")
    kafka_consumer = KafkaConsumer(topic_name)
    kafka_consumer.start_consuming(process_event)


if __name__ == "__main__":
    main()
