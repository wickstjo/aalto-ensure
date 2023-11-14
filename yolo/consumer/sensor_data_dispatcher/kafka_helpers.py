import time
from queue import Queue

from confluent_kafka import Producer, Consumer

class KafkaProducer:
    def __init__(self, config):
        self.kafka_client = Producer(config)

    def ack_callback(self, error, message):
        if error:
            print('ACK ERROR', error)
        else:
            # print('MESSAGE PUSHED')
            pass

    def send(self, topic_name, bytes_data, headers=None):
        if headers is None:
            headers = {}
        self.kafka_client.produce(
            topic_name,
            value=bytes_data.tobytes(),
            on_delivery=self.ack_callback,
            headers=headers,
        )

        # ASYNCRONOUSLY AWAIT CONSUMER ACK BEFORE SENDING NEXT MSG
        # self.kafka_client.poll(1)


class KafkaConsumer:
    def __init__(self, kafka_topic, bootstrap_servers):
        self.kafka_topic = kafka_topic
        self.delivery_guarantee = 'at_most_once' # OR at_least_once

        # CREATE THE CONSUMER CLIENT
        self.kafka_client = Consumer({
            'bootstrap.servers': bootstrap_servers,
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
        print(f"Listening for {self.kafka_topic}")
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


class KafkaToQueueProcessor:
    def __init__(self, kafka_topic: str, queue: Queue, bootstrap_servers: str):
        self.queue = queue
        self.topic = kafka_topic
        self.bootstrap_servers = bootstrap_servers

    def start(self):
        self.consumer = KafkaConsumer(kafka_topic=self.topic, bootstrap_servers=self.bootstrap_servers)
        self.consumer.start_consuming(self.process_event)

    def process_event(self, data, headers):
        self.queue.put((data, headers))
