from confluent_kafka.schema_registry import SchemaRegistryClient, avro
from confluent_kafka import Producer, DeserializingConsumer
from confluent_kafka.serialization import SerializationContext, MessageField
from utils import misc

#################################################################################################
#################################################################################################

class producer:
    def __init__(self, config: dict, topics: str):

        # STITCH TOGETHER URIS
        self.broker_uris = ','.join(config['kafka']['brokers'])
        self.registry_uri = 'http://' + config['kafka']['schema_registry']

        # VALIDATE & SAVE RELEVANT WORKER PARAMS IN STATE
        target = config['workers']['producers']
        self.validate_config(target)
        self.poll_duration = target['poll_duration']
        self.async_ack = target['async_ack']

        # CREATE KAFKA CLIENT & SERIALIZERS
        self.kafka_client = self.create_client()
        self.serializers = self.create_serializers(topics)

        # TRACK METRICS
        self.state = misc.metric_state({
            'push_error': 0,
            'ack_success': 0,
            'ack_error': 0,
        })

        # CREATE LOGGER
        self.logger = misc.logger()

    # DESTRUCTOR -- DUMP FINAL STATE
    def __del__(self):
        print('\nPRODUCER STATE', self.state, flush=True)

    # VALIDATE CONSUMER CONFIG PARAMS
    def validate_config(self, config: dict):
        assert config['async_ack'] in [True, False], 'MALFORMED ACK SYNC'
        assert config['poll_duration'] > 0, 'POLL DURATION MUST BE >1'

    # CREATE KAFKA CLIENT
    def create_client(self):
        return Producer({ 
            'bootstrap.servers': self.broker_uris, 
        })

    # PREPARE SERIALIZERS
    def create_serializers(self, topics: list):
        schema_registry = SchemaRegistryClient({ 'url': self.registry_uri })
        container = {}

        # LOOP THROUGH TOPICS
        for topic in topics:
        
            # FETCH SERIALIZER FROM REGISTRY & SAVE IT IN STATE
            schema_string = schema_registry.get_latest_version(topic).schema.schema_str
            serializer = avro.AvroSerializer(schema_registry, schema_string)
            context = SerializationContext(topic, MessageField.VALUE)

            # PUSH PAIR TO CONTAINER
            container[topic] = [serializer, context]

        return container
    
    # PUSH SINGLE MESSAGE TO KAFKA TOPIC
    def push_message(self, topic: str, message: dict, post_commit=None):
        try:
            # SERIALIZE THE MESSAGE WITH PREPARED FUNC
            serializer, context = self.serializers[topic]
            encoded = serializer(message, context)

            # PUSH MESSAGE
            self.kafka_client.produce(
                topic, 
                value=encoded,
                on_delivery=self.ack_callback,
            )

            # AWAIT ACKNOWLEDGE FROM BROKER
            if self.async_ack:
                self.kafka_client.poll(self.poll_duration)
            else:
                self.kafka_client.flush()

            # RUN CALLBACK WHEN ONE WAS PROVIDED
            if post_commit: post_commit()
        
        except Exception as error:
            self.logger.error('PUSH ERROR', error)
            self.state.increment('push_error')

    # AUTO CALLBACK FOR MESSAGE ACKNOWLEDGEMENT
    def ack_callback(self, error, message):
        if error:
            self.state.increment('ack_error')
            return self.logger.warning('ACK ERROR', error)
            
        self.state.increment('ack_success')
        self.logger.success('MESSAGE PUSHED')

#################################################################################################
#################################################################################################

class consumer:
    def __init__(self, config: dict, topic: str):

        # STITCH TOGETHER TOPIC & CONSUMER GROUP NAMES
        self.topic = topic
        self.consumer_group = topic + '.consumers'

        # STITCH TOGETHER URIS
        self.registry_uri = 'http://' + config['kafka']['schema_registry']
        self.broker_uris = ','.join(config['kafka']['brokers'])

        # SAVE WORKER PARAMS IN STATE
        target = config['workers']['consumers']
        self.validate_config(target)
        self.read_strategy = target['reading_strategy']
        self.poll_duration = target['poll_duration']
        self.delivery_guarantee = target['delivery_guarantee']
        self.async_ack = target['async_ack']
        self.max_retries = target['max_processing_retries']

        # TRACK METRICS
        self.state = misc.metric_state({
            'consume_error': 0,
            'parser_fail': 0,
            'ack_success': 0,
            'ack_error': 0,
        })

        # CREATE KAFKA CLIENT & LOGGER
        self.kafka_client = self.create_client()
        self.logger = misc.logger()

    # DESTRUCTOR -- DUMP FINAL STATE
    def __del__(self):
        print('\nCONSUMER STATE', self.state, flush=True)

    # VALIDATE CONSUMER CONFIG PARAMS
    def validate_config(self, config: dict) -> None:
        assert config['delivery_guarantee'] in ['at_most_once', 'at_least_once'], 'MALFORMED DELIVERY GUARANTEE'
        assert config['reading_strategy'] in ['earliest', 'latest'], 'MALFORMED READING STRATEGY'
        assert config['async_ack'] in [True, False], 'MALFORMED ACK SYNC'
        assert config['max_processing_retries'] > 0, 'MAX RETRIES MUST BE >0'
        assert config['poll_duration'] > 0, 'POLL DURATION MUST BE >1'

    # CREATE KAFKA CLIENT
    def create_client(self):
        
        # CREATE KAFKA REGISTRY CLIENT
        schema_registry = SchemaRegistryClient({
            'url': self.registry_uri
        })
        
        # FETCH SCHEMA STRING FROM REGISTRY & CREATE DESERIALIZER
        schema_string = schema_registry.get_latest_version(self.topic).schema.schema_str
        deserializer = avro.AvroDeserializer(schema_registry, schema_string)

        return DeserializingConsumer({
            'bootstrap.servers': self.broker_uris,
            'group.id': self.consumer_group,
            'value.deserializer': deserializer,
            'enable.auto.commit': False,
            'on_commit': self.ack_callback,
            'auto.offset.reset': self.read_strategy,
            # 'partition.assignment.strategy': 'range', #roundrobin
            # 'statistics.interval.ms': 1000,
        })

    # AUTO CALLBACK WHEN CONSUMER COMMITS MESSAGE
    def ack_callback(self, error, partitions):
        if error:
            self.state.increment('ack_error')
            return self.logger.warning('ACK ERROR', error)
            # log(f'(T{ self.nth_thread }) RECORD COMMITTED:\t{ part.topic } (PART: { part.partition }, OFFS: { part.offset })')
        
        # OTHERWISE, PROCESS SUCCEEDED
        self.state.increment('ack_success')
        self.logger.success('MESSAGE CONSUMED')

    # START CONSUMING DATA FROM TOPIC
    def start_consuming(self, on_message, post_commit=None):

        # CREATE KAFKA CONSUMER & SUBSCRIBE TO TOPIC FEED
        self.kafka_client.subscribe([self.topic])
        self.logger.info('STARTED CONSUMING..')

        # EVENT LOOP
        while True:
            try:
                # POLL NEXT MESSAGE
                msg = self.kafka_client.poll(self.poll_duration)

                # NULL MESSAGE -- SKIP
                if msg is None: continue

                # CATCH ERRORS
                if msg.error():
                    self.logger.error('FAULTY MESSAGE RECEIVED', msg.error())
                    continue

                # AT MOST ONCE -- DELIVERY GUARANTEE
                if self.delivery_guarantee == 'at_most_once':
                    self.kafka_client.commit(msg, asynchronous=self.async_ack)
                    if post_commit: post_commit()

                # PROCESS MESSAGE THROUGH CALLBACK
                for nth_try in range(self.max_retries):
                    success = on_message(msg)

                    # BREAK LOOP ON SUCCESSFUL RESULT
                    if success: break

                    # OTHERWISE, THROW ERROE AND TRY AGAIN
                    self.logger.warning(f'MESSAGE PARSER RETURNED FALSE ({ nth_try+1 })')
                    self.state.increment('parser_fail')

                # AT LEAST ONCE -- DELIVERY GUARANTEE
                if self.delivery_guarantee == 'at_least_once':
                    self.kafka_client.commit(msg, asynchronous=self.async_ack)
                    if post_commit: post_commit()

            # TERMINATE MANUALLY
            except KeyboardInterrupt:
                print()
                self.logger.info('MANUALLY KILLED..')
                break

            # SILENTLY DEAL WITH OTHER ERRORS
            except Exception as error:
                self.logger.error('CONSUMER ERROR', error)
                self.state.increment('consume_error')
                continue

        # TERMINATE KAFKA CONSUMER
        self.kafka_client.close()

#################################################################################################
#################################################################################################