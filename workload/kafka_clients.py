from confluent_kafka import Consumer, Producer

# GOOD DOCS FOR CONSUMER API
    # https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#consumer
    # https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#producer

###################################################################################################
###################################################################################################

class create_producer:

    # ON LOAD, CREATE KAFKA PRODUCER
    def __init__(self):
        self.kafka_client = Producer({
            'bootstrap.servers': '130.233.193.117:9092',
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
        self.kafka_client.poll(1)
        # self.kafka_client.flush()

###################################################################################################
###################################################################################################

class create_consumer:

    # ON LOAD, CREATE KAFKA CONSUMER CLIENT
    def __init__(self, kafka_topic):

        # SET STATIC CONSUMPTION CONFIGS
        self.kafka_topic = kafka_topic
        self.delivery_guarantee = 'at_most_once' # OR at_least_once

        # CREATE THE CONSUMER CLIENT
        self.kafka_client = Consumer({
            # 'bootstrap.servers': '192.168.1.231:9092', #,192.168.1.231:10002,192.168.1.231:10003', 192.168.1.152:9092
            'bootstrap.servers': '130.233.193.117:9092',
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
            print('CONSUMER STARTED..')

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
                    print('MESSAGE RECEIVED')
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