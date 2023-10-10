from confluent_kafka import Consumer
import json

###############################################################################################
###############################################################################################

# GOOD DOCS FOR CONSUMER API
# https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#consumer

class create_consumer:

    # ON LOAD, CREATE KAFKA CONSUMER CLIENT
    def __init__(self, kafka_topic):

        # SET STATIC CONSUMPTION CONFIGS
        self.kafka_topic = kafka_topic
        self.delivery_guarantee = 'at_most_once' # OR at_least_once

        # CREATE THE CONSUMER CLIENT
        self.kafka_client = Consumer({
            'bootstrap.servers': 'localhost:10001,localhost:10002,localhost:10003',
            'group.id': kafka_topic + '.consumers',
            'enable.auto.commit': False,
            'on_commit': self.ack_callback,
            'auto.offset.reset': 'earliest'
        })

    # AUTO CALLBACK WHEN CONSUMER COMMITS MESSAGE
    def ack_callback(self, error, partitions):
        if error:
            return print('ACK ERROR', error)

    # START CONSUMING TOPIC EVENTS
    def start_consuming(self, on_message):

            # CREATE KAFKA CONSUMER & SUBSCRIBE TO TOPIC FEED
            self.kafka_client.subscribe([self.kafka_topic])

            # EVENT LOOP
            while True:
                try:
                    # POLL NEXT MESSAGE
                    msg = self.kafka_client.poll(1)

                    # NULL MESSAGE -- SKIP
                    if msg is None: continue

                    # CATCH ERRORS
                    if msg.error():
                        print('FAULTY MESSAGE RECEIVED', msg.error())
                        continue

                    # AT MOST ONCE -- DELIVERY GUARANTEE
                    if self.delivery_guarantee == 'at_most_once':
                        self.kafka_client.commit(msg, asynchronous=True)

                    # HANDLE THE EVENT VIA CALLBACK FUNC
                    on_message(msg.value())

                    # AT LEAST ONCE -- DELIVERY GUARANTEE
                    if self.delivery_guarantee == 'at_least_once':
                        self.kafka_client.commit(msg, asynchronous=True)

                # TERMINATE MANUALLY
                except KeyboardInterrupt:
                    print('CONSUMER MANUALLY KILLED..')
                    break

                # SILENTLY DEAL WITH OTHER ERRORS
                except Exception as error:
                    print('CONSUMER ERROR', error)
                    continue

            # TERMINATE KAFKA CONSUMER
            self.kafka_client.close()

###############################################################################################
###############################################################################################

# SPECIFY TARGET TOPIC & START CONSUMING EVENTS FROM IT
topic_name = 'yolo_input'
kafka_consumer = create_consumer(topic_name)

# DESERIALIZE BYTES DATA -- INVERSE OF THE PRODUCERS SERIALIZER
def custom_deserializer(raw_bytes):
    return json.loads(raw_bytes.decode('UTF-8'))

# ON EVENT, DO...
def process_event(raw_bytes):
    deserialized_data = custom_deserializer(raw_bytes)
    print(deserialized_data)

# START WORKLOOP
kafka_consumer.start_consuming(process_event)