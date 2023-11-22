from utilz.kafka_utils import create_consumer
from utilz.misc import custom_deserializer, log, create_lock
import json

def run():

    # DYNAMIC ARGS
    args = {
        'window_size': 20,
        'input_topic': 'yolo_output'
    }

    ########################################################################################
    ########################################################################################

    # CREATE KAFKA CLIENTS
    kafka_consumer = create_consumer(args['input_topic'])
    thread_lock = create_lock()

    # TRACK YOLO RESULTS
    history = {
        'pre': [0] * args['window_size'],
        'inf': [0] * args['window_size'],
        'nth_event': 0
    }

    # ON EVENT, DO..
    def process_event(raw_bytes):
        yolo_results = custom_deserializer(raw_bytes)
        print(json.dumps(yolo_results, indent=4))

        # SAVE VALUES
        history['pre'][history['nth_event'] % args['window_size']] = yolo_results['timestamps']['pre']
        history['inf'][history['nth_event'] % args['window_size']] = yolo_results['timestamps']['inf']
        history['nth_event'] += 1

        # WHEN A NEW WINDOW HAS BEEN FILLED, PRINT ITS STATS
        if (history['nth_event'] == args['window_size']):
            avg_inf = round(sum(history['inf']) / args['window_size'], 2)
            min_inf = round(min(history['inf']), 2)
            max_inf = round(max(history['inf']), 2)

            log(f'INF: \t {avg_inf} \t\t ({min_inf}, {max_inf})')

    # FINALLY, START CONSUMING EVENTS
    try:
        kafka_consumer.poll_next(1, thread_lock, process_event)

    # TERMINATE MAIN PROCESS AND KILL HELPER THREADS
    except KeyboardInterrupt:
        thread_lock.kill()
        log('WORKER MANUALLY KILLED..', True)

run()