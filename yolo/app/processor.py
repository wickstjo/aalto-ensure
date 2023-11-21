from utilz.args_utils import consumer_args
from utilz.kafka_utils import create_consumer, create_producer
from utilz.misc import custom_serializer, resource_exists, log, create_lock
from PIL import Image
from numpy import asarray
import io, torch
from threading import Thread

def run():

    # PARSE THE PYTHON ARGS
    args = consumer_args()

    # MAKE SURE THE MODEL FILE EXISTS
    if not resource_exists(f'./models/{args.model}.pt'):
        return

    # PROPERLY LOAD THE YOLO MODEL
    yolo = torch.hub.load('ultralytics/yolov5', "custom", path=f'./models/{args.model}.pt', trust_repo=True, force_reload=True)
    device = yolo.parameters().__next__().device
    log(f"LOADED MODEL ({args.model}) ON DEVICE ({device})")

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer(args.kafka, 'yolo_input')
    kafka_producer = create_producer(args.kafka)

    # CONSUMER THREAD STUFF
    thread_pool = int(args.threads)
    thread_lock = create_lock()
    threads = []

    # WHAT THE THREAD DOES WITH POLLED EVENTS
    def process_event(img_bytes):

        # CONVERT INPUT BYTES TO IMAGE & GIVE IT TO YOLO
        img = Image.open(io.BytesIO(img_bytes))
        results = yolo.forward(asarray(img))

        # PUSH RESULTS INTO VALIDATION TOPIC
        kafka_producer.push_msg('yolo_output', custom_serializer({
            'timestamps': {
                'pre': results.t[0],
                'inf': results.t[1],
                'post': results.t[2],
            },
            'model': args.model,
            'dimensions': results.s
        }))

    # CREATE & START WORKER THREADS
    try:
        log(f'STARTING CONSUMER THREAD POOL OF SIZE: {thread_pool}')

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