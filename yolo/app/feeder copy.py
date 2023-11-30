from utilz.dataset_utils import load_dataset
from utilz.misc import resource_exists, log, create_lock
from utilz.kafka_utils import create_producer
from threading import Thread, Semaphore
import time, math, random

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
    
    # INSTANTIATE THREAD LOCKS
    thread_lock = create_lock()
    semaphore = Semaphore(1)

    # KEEP TRACK THREADS AND KAFKA PRODUCERS
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

    # COOLDOWN BREAKPOINTS
    # 2 MB/s = 0.09960923               MULTIPLIER = 1.03626943

    # DURATION IN SECONDS => MB/s INTERVAL
    experiment = [
        (30, 1),
        (30, 2),
        (30, 1)
    ]

    # SHARED ACTION COOLDOWN FOR WORKER THREADS
    action_cooldown = None

    # TIMESTAMP FOR THREADS TO SYNC TO
    experiment_start = time.time() + 3
    log(f'EXPERIMENT STARTING IN 3 SECONDS')

    ########################################################################################
    ########################################################################################

    def experiment_handler(lock):
        global action_cooldown

        # COMPUTE THE BYTESIZE OF THE AVERAGE DATASET ITEM
        avg_dataset_item_size = math.ceil(sum([len(x) for x in dataset]) / len(dataset))

        # STAY ACTIVE UNTIL LOCK IS MANUALLY KILLED
        while lock.is_active():

            # NO MORE BREAKPOINTS LEFT: KILL ALL THE THREADS
            if len(experiment) == 0:
                lock.kill()
                break

            # OTHERWISE, COMPUTE SELECT NEXT EXPERIMENT BREAKPOINT
            breakpoint_duration, breakpoint_interval = experiment.pop(1)
            log(f'NEXT EXPERIMENT BREAKPOINT: ({breakpoint_duration}s @ {breakpoint_interval} MB/s)')

            # COMPUTE THE NEW ACTION COOLDOWN
            events_per_second = (breakpoint_interval * 1000000) / avg_dataset_item_size
            new_cooldown = (1 / (events_per_second / args['thread_pool']))

            # SAFELY SET THE NEXT COOLDOWN
            with semaphore:
                action_cooldown = new_cooldown

            # ON THE FIRST RUN, BUSY WAIT TO SYNC THREADS
            while time.time() < experiment_start:
                pass
            
            # THEN SLEEP UNTIL THE NEXT BREAKPOINT
            time.sleep(breakpoint_duration)

    # CREATE THE EXPERIMENT HANDLER
    handler_thread = Thread(target=experiment_handler, args=(thread_lock,))
    threads.append(handler_thread)
    handler_thread.start()

    ########################################################################################
    ########################################################################################

    # PRODUCER THREAD WORK LOOP
    def thread_work(nth_thread, lock):

        # RANDOMLY PICK A STARTING INDEX FROM THE DATASET
        next_index = random.randrange(dataset_length)
        cooldown = None

        # BUSY WAIT FOR ABIT TO SYNC THREADS
        while time.time() < experiment_start:
            pass

        log(f'THREAD {nth_thread} HAS STARTED FROM INDEX {next_index}')

        # KEEP GOING UNTIL LOCK IS MANUALLY
        while lock.is_active():
            started = time.time()

            # SELECT NEXT BUFFER ITEM
            item = dataset[next_index]
            kafka_producers[nth_thread - 1].push_msg('yolo_input', item.tobytes())
            
            # FETCH THE LATEST ACTION COOLDOWN
            with semaphore:
                cooldown = action_cooldown

            # COMPUTE THE ADJUSTED ACTION COOLDOWN, THEN TAKE A NAP
            ended = time.time()
            action_duration = ended - started
            adjusted_cooldown = max(cooldown - action_duration, 0)
            time.sleep(adjusted_cooldown)

            # INCREMENT ROLLING INDEX
            next_index = (next_index+1) % dataset_length

    ########################################################################################
    ########################################################################################

    # CREATE & START WORKER THREADS
    try:
        log(f'CREATING PRODUCER THREAD POOL ({args["thread_pool"]})')

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