from utilz.args_utils import producer_args
from utilz.dataset_utils import parse_dataset
from utilz.misc import generate_cooldown, resource_exists
from utilz.kafka_utils import create_producer
from multiprocessing import Queue
from queue import Empty
from threading import Thread
import time

def run():

    # PARSE THE PYTHON ARGS
    args = producer_args()

    # START LOADING DATASET INTO QUEUE BUFFER
    queue = Queue(maxsize=args.buffer)

    # MAKE SURE THE HDF5 DATASET EXISTS
    if not resource_exists(f'./datasets/{args.dataset}.hdf5'):
        return

    # IT DOES: GRADUALLY LOAD THE DATASET INTO THE BUFFER
    parse_dataset(args, queue)

    # CREATE KAFKA PRODUCER
    kafka_producer = create_producer(args.kafka)

    def container(item):

        # PROCESS EACH FRAME'S IMG MATRIX
        for _, frame in item.data.items():

            # PUSH IT TO KAFKA
            kafka_producer.push_msg('yolo_input', frame.data.tobytes())

        # GENERATE COOLDOWN BASED ON TIMESTAMP & SINEWAVE, THEN WAIT
        # cooldown = generate_cooldown()
        # time.sleep(cooldown)

        time.sleep(0.2)

    # START ITERATING THROUGH BUFFER CONTENT
    while queue._notempty:
        try:
            # SELECT NEXT BUFFER ITEM
            item = queue.get(block=True, timeout=5)

            thread = Thread(target=container, args=(item,))
            thread.start()

        # TERMINATE MANUALLY
        except KeyboardInterrupt:
            queue.cancel_join_thread()
            print('FEEDER MANUALLY KILLED..')
            break

        # DIE PEACEFULLY WHEN QUEUE IS EMPTY
        except Empty:
            print('QUEUE WAS EMPTY FOR 5+ SECONDS, DYING..')
            break

        # SILENTLY DEAL WITH OTHER ERRORS
        except Exception as error:
            queue.cancel_join_thread()
            print('FEEDER ERROR', error)
            break

run()