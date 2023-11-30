from utilz.dataset_utils import load_dataset
from utilz.misc import resource_exists, log, create_lock, resize_array
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
        'num_threads': 4,

        # EXPERIMENT DETAILS
        'experiment': {
            'max_mbs': 4,
            'n_breakpoints': 400,
            'duration': (60*60*10), 
        }
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
    for _ in range(args['num_threads']):
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

    def experiment_handler(lock):
        global action_cooldown

        # THE DEFAULT DAYNIGHT CYCLE WORKLOAD PERCENTAGES (01 => 23)
        default_cycle = [
            0.24, 0.28, 0.32, 0.36, 0.40, 0.53, 
            0.67, 0.80, 0.73, 0.65, 0.58, 0.50, 
            0.58, 0.66, 0.74, 0.82, 0.95, 0.90, 
            0.85, 0.80, 0.65, 0.50, 0.35, 0.20
        ]

        # SCALE THE ARRAY WHILE MAINTAINING RATIOS
        real_cycle = resize_array(
            default_cycle, 
            args['experiment']['n_breakpoints']
        )

        # COMPUTE THE EQUAL TIME SLIVER
        time_sliver = args['experiment']['duration'] / args['experiment']['n_breakpoints']

        # COMPUTE THE BYTESIZE OF THE AVERAGE DATASET ITEM
        avg_dataset_item_size = math.ceil(sum([len(x) for x in dataset]) / len(dataset))

        # STAY ACTIVE UNTIL LOCK IS MANUALLY KILLED
        while lock.is_active():

            # NO MORE BREAKPOINTS LEFT: KILL ALL THE THREADS
            if len(real_cycle) == 0:
                log('LAST EXPERIMENT BREAKPOINT RAN, TERMINATING..')
                lock.kill()
                break

            # OTHERWISE, FETCH THE NEXT INTERVAL
            mbs_interval = real_cycle.pop(0) * args['experiment']['max_mbs']
            log(f'SET NEW INPUT INTERVAL: ({time_sliver}s @ {mbs_interval} MB/s)')

            # COMPUTE THE NEW ACTION COOLDOWN
            events_per_second = (mbs_interval * 1000000) / avg_dataset_item_size
            new_cooldown = (1 / (events_per_second / args['num_threads']))

            # SAFELY SET THE NEXT COOLDOWN
            with semaphore:
                action_cooldown = new_cooldown

            # ON THE FIRST RUN, BUSY WAIT TO SYNC THREADS
            while time.time() < experiment_start:
                pass
            
            # THEN SLEEP UNTIL THE NEXT BREAKPOINT
            time.sleep(time_sliver)

    ########################################################################################
    ########################################################################################

    # PRODUCER THREAD WORK LOOP
    def thread_work(nth_thread, lock):
        global action_cooldown

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

    try:
    
        # SHARED ACTION COOLDOWN FOR WORKER THREADS
        # TIMESTAMP FOR THREADS TO SYNC TO
        action_cooldown = None
        experiment_start = time.time() + 3

        # CREATE THE EXPERIMENT HANDLER
        log(f'CREATING EXPERIMENT HANDLER')
        handler_thread = Thread(target=experiment_handler, args=(thread_lock,))
        threads.append(handler_thread)
        handler_thread.start()

        log(f'CREATING PRODUCER THREAD POOL ({args["num_threads"]})')

        for nth in range(args['num_threads']):
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