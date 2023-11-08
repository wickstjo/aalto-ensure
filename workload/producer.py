from misc import generate_cooldown, custom_serializer 
from kafka_clients import create_producer
import time

###############################################################################################
###############################################################################################

# CREATE NEW KAFKA PRODUCER & SPECIFY TARGET TOPIC
kafka_producer = create_producer()
topic_name = 'yolo_input'

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