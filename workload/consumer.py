from kafka_clients import create_consumer, create_producer
from misc import custom_serializer, custom_deserializer
import time

###############################################################################################
###############################################################################################

# SPECIFY TARGET TOPIC & START CONSUMING EVENTS FROM IT
in_topic = 'yolo_input'
out_topic = 'yolo_output'
kafka_consumer = create_consumer(in_topic)
kafka_producer = create_producer()
last_event = time.time()

# ON EVENT, DO...
def process_event(raw_bytes):

    global last_event
    current_event = time.time()
    
    # SERIALIZE MSG TO BYTES -- DOESNT NEED TO BE JSON
    serialized_data = custom_serializer({
        'foo': current_event - last_event
    })

    # PUSH MESSAGE TO TOPIC
    kafka_producer.push_msg(out_topic, serialized_data)

    last_event = current_event

# START WORKLOOP
kafka_consumer.start_consuming(process_event)