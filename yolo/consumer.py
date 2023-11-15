from utilz.args_utils import consumer_args
from utilz.kafka_utils import create_consumer, create_producer
from utilz.misc import custom_serializer
import os, io, torch
from PIL import Image
from numpy import asarray

def run():

    # PARSE THE PYTHON ARGS
    args = consumer_args()
    print(args)

    # MAKE SURE THE DEFINED MODEL EXISTS
    if not os.path.exists(f'./models/{args.model}.pt'):
        print(f"MODEL NOT FOUND ({args.model})")
        return
    else:
        print(f"MODEL FOUND ({args.model})")

    # PROPERLY LOAD THE YOLO MODEL
    yolo = torch.hub.load('ultralytics/yolov5', "custom", path=f'./models/{args.model}.pt')
    device = yolo.parameters().__next__().device
    print(f"LOADED MODEL ({args.model}) ON DEVICE ({device})")

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer(args.kafka, 'yolo_input')
    kafka_producer = create_producer(args.kafka)

    # ON EVENT, DO..
    def process_event(img_bytes):

        # CONVERT INPUT BYTES TO IMAGE & GIVE IT TO YOLO
        img = Image.open(io.BytesIO(img_bytes))
        results = yolo.forward(asarray(img))

        # PUSH RESULTS INTO VALIDATION TOPIC
        kafka_producer.push_msg('yolo_output', custom_serializer({
            'timestamps': results.t,
            'dimensions': results.s
        }))

    # FINALLY, START CONSUMING EVENTS
    kafka_consumer.start_consuming(process_event)

run()