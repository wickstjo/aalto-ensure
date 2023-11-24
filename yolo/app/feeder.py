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
        'queue_size': 1000,
        'queue_delay': 2,
        'frame_cooldown': 0.2,
    }

    ########################################################################################
    ########################################################################################

    # MAKE SURE THE HDF5 DATASET EXISTS
    if not resource_exists(f'./datasets/{args["dataset"]["name"]}.hdf5'):
        return

    # CREATE KAFKA PRODUCER
    kafka_producer = create_producer()

    # MAKE SURE KAFKA CONNECTION IS OK
    if not kafka_producer.connected():
        return
    
    # INSTANTIATE THREAD PARAMS
    thread_lock = create_lock()
    threads = []

    # START GRADUALLY LOADING DATASET INTO A QUEUE BUFFER
    queue = Queue(maxsize=args['queue_size'])

    # START PARSING DATASET INTO BUFFER -- IN ANOTHER THREAD
    thread = Thread(target=parse_dataset, args=(args['dataset'], queue, thread_lock))
    threads.append(thread)
    thread.start()

    # WAIT FOR THQ BUFFER TO FILL ABIT
    log(f'LOADING BUFFER FOR {args["queue_delay"]} SECONDS')
    time.sleep(args['queue_delay'])

    # PRODUCER THREAD WORK LOOP
    def thread_work(nth_thread, lock):
        while queue._notempty and lock.is_active():
            try:
                # SELECT NEXT BUFFER ITEM
                item = queue.get(block=True, timeout=5)

                # PROCESS EACH FRAME'S IMG MATRIX
                for _, frame in item.data.items():
                    if lock.is_active():

                        # PUSH IT TO KAFKA
                        kafka_producer.push_msg('yolo_input', frame.data.tobytes())
                        time.sleep(args['frame_cooldown'])

            # DIE PEACEFULLY WHEN QUEUE IS EMPTY
            except Empty:
                log(f'QUEUE WAS EMPTY, THREAD {nth_thread} DYING..')
                break

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