# pip install confluent-kafka
from confluent_kafka import Producer
from cooldown import generate_cooldown
import json, time

###############################################################################################
###############################################################################################

# GOOD DOCS FOR PRODUCER API
# https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#producer

class create_producer:

    # ON LOAD, CREATE KAFKA PRODUCER
    def __init__(self):
        self.kafka_client = Producer({
            'bootstrap.servers': 'localhost:10001,localhost:10002,localhost:10003'
        })

    # ON CONSUMER CALLBACK, DO..
    def ack_callback(self, error, message):
        if error:
            print('ACK ERROR', error)
        else:
            print('MESSAGE PUSHED')

    # PUSH MESSAGE TO A KAFK TOPIC
    def push_msg(self, topic_name, bytes_data):

        # PUSH MESSAGE TO KAFKA TOPIC
        self.kafka_client.produce(
            topic_name, 
            value=bytes_data,
            on_delivery=self.ack_callback,
        )

        # ASYNCRONOUSLY AWAIT CONSUMER ACK BEFORE SENDING NEXT MSG
        # self.kafka_client.poll(1)
        self.kafka_client.flush()

###############################################################################################
###############################################################################################

# CREATE NEW KAFKA PRODUCER & SPECIFY TARGET TOPIC
kafka_producer = create_producer()
topic_name = 'yolo_input'

# CUSTOM DATA => BYTES SERIALIZED -- INVERSE OF THE CONSUMERS DESERIALIZER
def custom_serializer(data):
    return json.dumps(data).encode('UTF-8')

# LOOP N TIMES
for nth in range(500):

    # SERIALIZE MSG TO BYTES -- DOESNT NEED TO BE JSON
    serialized_data = custom_serializer({
        'foo': nth
    })

    # PUSH MESSAGE TO TOPIC
    kafka_producer.push_msg(topic_name, serialized_data)

    cooldown = generate_cooldown()
    time.sleep(cooldown)