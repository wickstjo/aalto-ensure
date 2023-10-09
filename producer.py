import json
from confluent_kafka import Producer

###############################################################################################
###############################################################################################

# GOOD DOCS FOR PRODUCER/CONSUMER API
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
    def push_msg(self, topic_name, json_data):

        # SERIALIZE JSON INPUT TO BYTES
        serialized_msg = json.dumps(json_data).encode('UTF-8')

        # PUSH MESSAGE TO KAFKA TOPIC
        self.kafka_client.produce(
            topic_name, 
            value=serialized_msg,
            on_delivery=self.ack_callback,
        )

        # ASYNCRONOUSLY AWAIT CONSUMER ACK BEFORE SENDING NEXT MSG
        self.kafka_client.poll(1)

###############################################################################################
###############################################################################################

# CREATE NEW KAFKA PRODUCER & SPECIFY TARGET TOPIC
kafka_producer = create_producer()
topic_name = 'yolo_input'

# LOOP N TIMES
for nth in range(5):

    # PUSH MESSAGE TO TOPIC
    kafka_producer.push_msg(topic_name, {
        'foo': nth
    })