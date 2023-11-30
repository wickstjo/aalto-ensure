  GNU nano 6.2                                                                                                             feeder.py                                                                                                                      
from utilz.dataset_utils import load_dataset
from utilz.misc import resource_exists, log, create_lock
from utilz.kafka_utils import create_producer
from threading import Thread
from random import randrange
import time, math

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
        'thread_pool': 4,
        'queue_size': 500,
        'queue_delay': 2,

        # EVENTS PER SECOND
        'mbs_per_second': 2
    }

    ########################################################################################
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

    # LOAD THE DATASET
    dataset = load_dataset(args['dataset'])
    dataset_length = len(dataset)

    ########################################################################################
    ########################################################################################

    # COMPUTE ACTIONB COOLDOWN
    avg_dataset_item_size = math.ceil(sum([len(x) for x in dataset]) / len(dataset))
    events_per_second = (args['mbs_per_second'] * 1000000) / avg_dataset_item_size
    cooldown = (1 / (events_per_second / args['thread_pool'])) * 0.965
    adjusted_cooldown = lambda duration: max(cooldown - duration, 0)
    log(f'DEFAULT ACTION COOLDOWN ({cooldown})')

    # TIMESTAMP FOR THREADS TO SYNC TO
    experiment_start = time.time() + 3
    log(f'EXPERIMENT STARTING IN 3 SECONDS')

    ########################################################################################
    ########################################################################################

    # PRODUCER THREAD WORK LOOP
    def thread_work(nth_thread, lock):

        # RANDOMLY PICK A STARTING INDEX FROM THE DATASET
        next_index = randrange(dataset_length)

        # BUSY WAIT FOR ABIT TO SYNC THREADS
        while time.time() < experiment_start:
            pass

        log(f'THREAD {nth_thread} HAS STARTED FROM INDEX {next_index}')

        # KEEP GOING UNTIL LOCK IS MANUALLY
        while lock.is_active():

            # SELECT NEXT BUFFER ITEM
            item = dataset[next_index]
            kafka_producers[nth_thread - 1].push_msg('yolo_input', item.tobytes())
            time.sleep(adjusted_cooldown(0))

            # INCREMENT ROLLING INDEX
            next_index = (next_index+1) % dataset_length

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
        log('WORKER & THREADS MANUALLY KILLED..', True)

run()







