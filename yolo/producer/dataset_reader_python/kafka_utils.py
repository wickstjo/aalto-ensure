from confluent_kafka import Producer


class KafkaDummy:
    def __init__(self, *args):
        pass

    def send(self, *args):
        pass

    def flush(self):
        pass

class KafkaProducer:
    def __init__(self, config):
        self.kafka_client = Producer(config)

    def ack_callback(self, error, message):
        if error:
            print('ACK ERROR', error)
        else:
            # print('MESSAGE PUSHED')
            pass

    def send(self, topic_name, bytes_data):
        self.kafka_client.produce(
            topic_name,
            value=bytes_data.tobytes(),
            on_delivery=self.ack_callback,
        )

        # ASYNCRONOUSLY AWAIT CONSUMER ACK BEFORE SENDING NEXT MSG
        # self.kafka_client.poll(1)


    def flush(self):
        self.kafka_client.flush()
