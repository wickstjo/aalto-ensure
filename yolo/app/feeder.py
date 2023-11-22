from utilz.dataset_utils import parse_dataset
from utilz.misc import resource_exists, log, create_lock
from utilz.kafka_utils import create_producer
from multiprocessing import Queue
from queue import Empty
from threading import Thread
import time

def run():

    # DYNAMIC ARGUMENTS
    args = {
        'dataset': {
            'name': 'mini',
            'max_frames': -1,
            'max_vehicles': -1,
            'fps': 5,
            'repeat': 1,
        },
        'thread_pool': 3,
        'queue_buffer': 1000,
        'frame_cooldown': 0.2,
    }

    ########################################################################################
    ########################################################################################

    # MAKE SURE THE HDF5 DATASET EXISTS
    if not resource_exists(f'./datasets/{args["dataset"]["name"]}.hdf5'):
        return

    # START GRADUALLY LOADING DATASET INTO A QUEUE BUFFER
    queue = Queue(maxsize=args['queue_buffer'])
    parse_dataset(args['dataset'], queue)

    # CREATE KAFKA PRODUCER
    kafka_producer = create_producer()
    thread_lock = create_lock()
    threads = []

    # PRODUCER THREAD WORK LOOP
    def thread_work(nth_thread, lock):
        while queue._notempty and lock.is_active():

            # SELECT NEXT BUFFER ITEM
            item = queue.get(block=True, timeout=5)

            # PROCESS EACH FRAME'S IMG MATRIX
            for _, frame in item.data.items():
                if lock.is_active():

                    # PUSH IT TO KAFKA
                    kafka_producer.push_msg('yolo_input', frame.data.tobytes())
                    time.sleep(args['frame_cooldown'])

    # CREATE & START WORKER THREADS
    try:
        log(f'STARTING PRODUCER THREAD POOL ({args["thread_pool"]})')

        for nth in range(args['thread_pool']):
            thread = Thread(target=thread_work, args=(nth+1, thread_lock))
            threads.append(thread)
            thread.start()

        # WAIT FOR EVERY THREAD TO FINISH (MUST BE MANUALLY BY CANCELING LOCK)
        [[thread.join() for thread in threads]]

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        thread_lock.kill()
        queue.cancel_join_thread()
        log('WORKER & THREADS MANUALLY KILLED..', True)

run()