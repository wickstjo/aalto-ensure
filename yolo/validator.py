from utilz.kafka_utils import create_consumer
from utilz.misc import custom_deserializer

def run():

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer('localhost:10001,localhost:10002,localhost:10003', 'yolo_output')

    # ON EVENT, DO..
    def process_event(raw_bytes):
        yolo_results = custom_deserializer(raw_bytes)
        print(yolo_results)

    # FINALLY, START CONSUMING EVENTS
    kafka_consumer.start_consuming(process_event)

run()