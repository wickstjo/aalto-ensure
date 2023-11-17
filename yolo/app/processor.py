from utilz.args_utils import consumer_args
from utilz.kafka_utils import create_consumer, create_producer
from utilz.misc import custom_serializer, resource_exists
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
    print(f"LOADED MODEL ({args.model}) ON DEVICE ({device})")

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer(args.kafka, 'yolo_input')
    kafka_producer = create_producer(args.kafka)

    # HANDLE EVENT WITH THREAD
    def container(img_bytes):

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

    # ON EVENT, DO..
    def process_event(img_bytes):
        thread = Thread(target=container, args=(img_bytes,))
        thread.start()

    # FINALLY, START CONSUMING EVENTS
    kafka_consumer.start_consuming(process_event)

run()