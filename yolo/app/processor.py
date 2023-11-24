from utilz.kafka_utils import create_consumer, create_producer
from utilz.misc import custom_serializer, resource_exists, log, create_lock
from PIL import Image
from numpy import asarray
import io, torch
from threading import Thread
import socket

def run():

    # DYNAMIC ARGUMENTS FOR YOLO PROCESSING
    args = {
        'model': 'custom-750k',
        'worker_threads': 3,
        'kafka': {
            'input_topic': 'yolo_input',
            'output_topic': 'yolo_output',
        }
    }

    ########################################################################################
    ########################################################################################

    # MAKE SURE THE MODEL FILE EXISTS
    if not resource_exists(f'./models/{args["model"]}.pt'):
        return

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer(args['kafka']['input_topic'])
    kafka_producer = create_producer()

    # MAKE SURE KAFKA CONNECTIONS ARE OK
    if not kafka_producer.connected() or not kafka_consumer.connected():
        return

    # PROPERLY LOAD THE YOLO MODEL
    # TODO: LOAD A MODEL FOR EACH THREAD
    yolo = torch.hub.load('ultralytics/yolov5', 'custom', path=f'./models/{args["model"]}.pt', trust_repo=True, force_reload=True)
    device = yolo.parameters().__next__().device
    log(f'LOADED MODEL ({args["model"]}) ON DEVICE ({device})')

    # CONSUMER THREAD STUFF
    thread_pool = args['worker_threads']
    thread_lock = create_lock()
    threads = []

    # TRACK WHICH MACHINE IS DOING THE PROCESSING
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)

    # WHAT THE THREAD DOES WITH POLLED EVENTS
    def process_event(img_bytes):

        # CONVERT INPUT BYTES TO IMAGE & GIVE IT TO YOLO
        img = Image.open(io.BytesIO(img_bytes))
        results = yolo.forward(asarray(img))

        # PUSH RESULTS INTO VALIDATION TOPIC
        kafka_producer.push_msg(args['kafka']['output_topic'], custom_serializer({
            'timestamps': {
                'pre': results.t[0],
                'inf': results.t[1],
                'post': results.t[2],
            },
            'source': ip_addr,
            'model': args['model'],
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