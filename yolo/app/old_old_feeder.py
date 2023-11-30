  GNU nano 6.2                                                                                                             feeder.py *                                                                                                                    
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
            #'name': 'v1_50_cars_4800_steps',
            'name': 'mini',
            'max_frames': -1,
            'max_vehicles': -1,
            'fps': 5,
            'repeat': 1,
        },
        'thread_pool': 4,
        'queue_buffer': 300,
        'frame_cooldown': 0.3,
    }

'    ########################################################################################
    ########################################################################################

    # MAKE SURE THE HDF5 DATASET EXISTS
    if not resource_exists(f'./datasets/{args["dataset"]["name"]}.hdf5'):
        return

    # INSTANTIATE THREAD PARAMS
    thread_lock = create_lock()
    threads = []
    kafka_producers = []

    # CREATE KAFKA PRODUCERS FOR EACH THREAD
    for _ in range(args['thread_pool']):
        kafka_producer = create_producer()
        kafka_producers.append(kafka_producer)

    # MAKE SURE KAFKA CONNECTION IS OK
    if not kafka_producers[0].connected():
        return

    # START GRADUALLY LOADING DATASET INTO A QUEUE BUFFER
    queue = Queue(maxsize=args['queue_buffer'])

    # START PARSING DATASET INTO BUFFER -- IN ANOTHER THREAD
    thread = Thread(target=parse_dataset, args=(args['dataset'], queue, thread_lock))
    threads.append(thread)
    thread.start()

    # WAIT FOR THQ BUFFER TO FILL ABIT
    log('LOADING BUFFER..')
    time.sleep(2)

    # PRODUCER THREAD WORK LOOP
    def thread_work(nth_thread, lock):
        while queue._notempty and lock.is_active():
            try:
                # SELECT NEXT BUFFER ITEM
                item = queue.get(block=True, timeout=5)

                # PROCESS EACH FRAME'S IMG MATRIX
                for _, frame in item.data.items():
                    if lock.is_active():
                        print(len(frame.data.tobytes()))

                        # PUSH IT TO KAFKA
                        kafka_producers[nth_thread - 1].push_msg('yolo_input', frame.data.tobytes())

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
        queue.cancel_join_thread()

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        thread_lock.kill()
        queue.cancel_join_thread()
        log('WORKER & THREADS MANUALLY KILLED..', True)

run()


