from kafka_clients import create_consumer
from misc import custom_deserializer
import json, time

###############################################################################################
###############################################################################################

# SPECIFY TARGET TOPIC & START CONSUMING EVENTS FROM IT
topic_name = 'yolo_output'
kafka_consumer = create_consumer(topic_name)

# ON EVENT, DO...
def process_event(raw_bytes):
    deserialized_data = custom_deserializer(raw_bytes)
    print(deserialized_data)

# START WORKLOOP
kafka_consumer.start_consuming(process_event)