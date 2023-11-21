from confluent_kafka import Consumer, Producer
import time
import random
from threading import Thread
from datetime import datetime

from utilz.misc import log, create_lock

class create_consumer:

    # ON LOAD, CREATE KAFKA CONSUMER CLIENT
    def __init__(self, kafka_topic):

        # SET STATIC CONSUMPTION CONFIGS
        self.kafka_topic = kafka_topic

        # CREATE THE CONSUMER CLIENT
        self.kafka_client = Consumer({
            # 'bootstrap.servers': '130.233.193.117:9092',
            'bootstrap.servers': 'localhost:10001,localhost:10002,localhost:10003',
            'group.id': kafka_topic + '.consumers',
            'enable.auto.commit': False,
            'on_commit': self.ack_callback,
            'auto.offset.reset': 'latest' # earliest latest
        })

        # CREATE KAFKA CONSUMER & SUBSCRIBE TO TOPIC FEED
        self.kafka_client.subscribe([self.kafka_topic])
        log('SUBSCRIPTION STARTED..')

    # AUTO CALLBACK WHEN CONSUMER COMMITS MESSAGE
    def ack_callback(self, error, partitions):
        if error:
            return print('ACK ERROR', error)

    # START CONSUMING TOPIC EVENTS
    def poll_next(self, nth_thread, thread_lock, on_message):
        log(f'THREAD {nth_thread}: NOW POLLING')
        
        while thread_lock.is_active():
            try:
                # POLL NEXT MESSAGE
                msg = self.kafka_client.poll(1)

                # NULL MESSAGE -- SKIP
                if msg is None:
                    continue

                # CATCH ERRORS
                if msg.error():
                    print('FAULTY EVENT RECEIVED', msg.error())
                    continue

                # COMMIT THE EVENT TO PREVENT OTHERS FROM TAKING IT
                self.kafka_client.commit(msg, asynchronous=True)

                # HANDLE THE EVENT VIA CALLBACK FUNC
                log(f'THREAD {nth_thread}: EVENT RECEIVED')
                on_message(msg.value())
                log(f'THREAD {nth_thread}: EVENT HANDLED')

            # SILENTLY DEAL WITH OTHER ERRORS
            except Exception as error:
                print('CONSUMER ERROR', error)
                continue
            
        # LOCK WAS KILLED, THEREFORE THREAD LOOP ENDS
        log(f'THREAD {nth_thread}: MANUALLY KILLED')

def run():

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer('yolo_input')

    # CONSUMER THREAD STUFF
    thread_pool = 3
    thread_lock = create_lock()
    threads = []

    log(f'STARTING CONSUMER THREAD POOL OF SIZE: {thread_pool}')

    # ON EVENT, DO..
    def process_event(img_bytes):
        time.sleep(random.uniform(1, 3))

    # START WORKER THREADS
    try:
        for nth in range(thread_pool):
            thread = Thread(target=kafka_consumer.poll_next, args=(nth+1, thread_lock, process_event,))
            threads.append(thread)
            thread.start()

        # WAIT FOR EVERY THREAD TO FINISH (MUST BE MANUALLY BY CANCELING LOCK)
        [[thread.join() for thread in threads]]

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        thread_lock.kill()
        log('WORKER MANUALLY KILLED..', True)

run()