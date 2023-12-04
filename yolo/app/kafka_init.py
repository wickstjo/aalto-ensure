from confluent_kafka.admin import AdminClient, NewPartitions, NewTopic
from confluent_kafka import TopicPartition
import json, time

from utilz.kafka_utils import create_producer, create_consumer
from utilz.misc import create_lock
from threading import Thread

admin_client = AdminClient({
    'bootstrap.servers': ','.join(['130.233.193.117:' + str(x) for x in [10001, 10002, 10003]]),
})

# CHECK WHAT TOPICS EXIST
def query_topics():
    container = {}
    
    for name, parts in admin_client.list_topics().topics.items():
        container[name] = len(parts.partitions)
    
    #print(json.dumps(container, indent=4))
    return container

# CREATE TOPICS WITH N PARTITIONS
def create_topic(name, partitions, replication):
    
    # CHECK CURRENT TOPICS
    topic_data = query_topics()
    
    # STOP IF TOPIC ALREADY EXISTS
    if name in topic_data:
        raise Exception(f'ERROR: TOPIC ({name}) ALREADY EXISTS')
    
    # OTHERWISE, CREATE IT
    admin_client.create_topics(
        new_topics=[NewTopic(
            topic=name,
            num_partitions=partitions,
            replication_factor=replication
        )]
    )
    
    return True

###########################################################################################
###########################################################################################

try:
    # CREATE YOLO INPUT TOPIC WITH 34 PARTITIONS
    create_topic(
        name='yolo_input',
        partitions=34,
        replication=1
    )

    # CREATE VALIDATION TOPIC
    create_topic(
        name='yolo_output',
        partitions=1,
        replication=1
    )

except Exception as err:
    print(err)

# PRINT CURRENT KAFKA TOPIC STATE
time.sleep(1)
print(json.dumps(query_topics(), indent=4))

###################################################################################
###################################################################################

# PRODUCE AND CONSUME ONE MESSAGE FROM THE INPUT TOPIC

def test_topic(topic_name):
    thread_lock = create_lock()

    def cons(lock):
        kafka_client = create_consumer(topic_name)

        while lock.is_active():
            kafka_client.poll_next(1, lock, lambda x, y: lock.kill())

    consumer_thread = Thread(target=cons, args=(thread_lock,))
    consumer_thread.start()

    time.sleep(2)

    kafka_client = create_producer()
    kafka_client.push_msg(topic_name, b'foo')

    consumer_thread.join()

test_topic('yolo_input')
test_topic('yolo_output')