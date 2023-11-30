from confluent_kafka.admin import AdminClient, NewPartitions, NewTopic
from confluent_kafka import TopicPartition
import json, time

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

    print('CREATING TOPICS...')

except Exception as err:
    print(err)

# PRINT CURRENT KAFKA TOPIC STATE
time.sleep(1)
print(json.dumps(query_topics(), indent=4))