import requests, pandas, json, os, shutil
from datetime import datetime
import time, math
from IPython.display import clear_output
from threading import Thread, Semaphore
import time, math, random, argparse

def get_names(port, exclude):
    try:
        result = requests.get(f'http://130.233.193.117:{port}/api/v1/label/__name__/values')
        container = []

        for metric in result.json()['data']:
            if not exclude(metric):
                container.append(metric)

        return container

    except:
        raise(f'COULD NOT PING INSTANCES AT PORT {port}')
        return False

def json_save(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def segment_timestamps(unix_start, unix_end, batch_size):

    container = []
    time_delta = unix_end - unix_start

    for _ in range(math.floor(time_delta / batch_size)):
        container.append(batch_size)
        time_delta -= batch_size

    if time_delta > 0:
        container.append(time_delta)

    last_start = unix_start
    tuples = []

    for window in container:
        tuples.append((last_start, last_start+window))
        last_start += window

    return tuples

def fetch_metric(base_path, prometheus_port, query, formatted_start, formatted_end, n_steps, semaphore, tracker):

    # CREATE SUB DIR FOR QUERY
    dir_path = f'{base_path}/{query}'
    os.mkdir(dir_path)
    df_initialized = False

    # PROMETHEUS ONLY ALLOWS QUERIES WITH LESS THAN 11K ROWS
    # SEGMENT LARGE TIMESTAMPS INTO SMALLER PAIRS TO BYPASS THIS LIMITATION
    segments = segment_timestamps(formatted_start, formatted_end, 300)
    threads = []

    def inner_loop(t1, t2, nth_segment):
        print(t1, t2)

        # MAKE GET REQUEST
        URL = f'http://130.233.193.117:{prometheus_port}/api/v1/query_range?query={query}&start={t1}&end={t2}&step={n_steps}s'
        results = requests.get(URL).json()['data']['result']

        # PREP THE BATCH DATAFRAME
        cols = [x for x in range(len(results))]
        rows = [x for x in range(t1, t2, n_steps)]
        df = pandas.DataFrame(columns=cols, index=rows)

        # START FILLING THE BATCH DF
        for nth, item in enumerate(results):

            # ZIP TUPLE LIST INTO DICT
            # EXTRACT ELEMENTS FROM KV LIST
            timestamps = [x[0] for x in item['values']]
            values = [x[1] for x in item['values']]
            as_dict = dict(zip(timestamps, values))

            # INJECT DICT AS DATAFRAME COLUMN
            df[nth] = as_dict

        # APPEND BATCH DATAFRAME TO MAIN DATAFRAME
        df.to_csv(f'{dir_path}/{nth_segment}-values.csv')

    # LOOP THROUGH EACH SEGMENT, COMBINING THEIR QUERY OUTPUT
    for nth_segment, (t1, t2) in enumerate(segments):
        semaphore.acquire()

        thread = Thread(target=inner_loop, args=(t1, t2, nth_segment))
        threads.append(thread)
        thread.start()

        semaphore.release()

    # INCREMENT THE TRACKER & MAKE ROOM FOR THE NEXT THREAD
    [thread.join() for thread in threads]
    tracker.increment(query)

class Tracker:
    def __init__(self, total):
        self.accumulator = Semaphore(1)
        self.value = 0
        self.total = total

        self.exp_start = time.time()

    def increment(self, query):
        self.accumulator.acquire()

        # COMPUTE THE DURATION BREAKPOINT
        duration = round(time.time() - self.exp_start, 2)

        if duration > 60:
            shortened = round(duration / 60, 2)
            duration = f'{shortened}m'
        else:
            duration = f'{duration}s'

        self.value += 1
        percent = round((self.value/self.total) * 100, 2)
        prefix = f'{self.value}/{self.total} ({percent}%, {duration})'
        n_spaces = ' ' * (40 - len(prefix))

        print(f'{prefix}{n_spaces}{query}', flush=True)
        self.accumulator.release()

def create_snapshot(start_time, end_time, n_steps):

    # GENERATE UNIQUE SNAPSHOT PATH
    now = str(int(time.time()))
    snapshot_path = f'snapshots/{now}'
    os.mkdir(snapshot_path)

    # CONVERT DATES TO UNIX TIMESTAMPS
    date_format = '%Y-%m-%d %H:%M:%S'
    formatted_start = int(datetime.strptime(start_time, date_format).timestamp())
    formatted_end = int(datetime.strptime(end_time, date_format).timestamp())

    # ADJUSTED TIMESTAMPS FOR GMT+2 TIME
    #two_hours = 60*60*2
    #formatted_start -= two_hours
    #formatted_end -= two_hours

    # PROMETHEUS SERVER 1
    s1_filter = lambda x: x.startswith('prometheus_') or x.startswith('grafana_') or x.startswith('alertmanager_')
    # s1_filter = lambda x: not x.startswith('kepler_node_uncore_joules_total')
    s1_metrics = get_names(9090, s1_filter)

    # PROMETHEUS SERVER 2
    s2_filter = lambda x: not x.startswith('kafka_')
    s2_metrics = get_names(9091, s2_filter)

    # SAFELY MAKE REQUESTS CONCURRENTLY WITH SEMAPHORE PROTECTION
    semaphore = Semaphore(5)
    n_metrics = len(s1_metrics) + len(s2_metrics)
    tracker = Tracker(n_metrics)

    # MAKE PROMETHEUS SERVER2 QUERIES
    for metric in s1_metrics:
        fetch_metric(snapshot_path, 9090, metric, formatted_start, formatted_end, n_steps, semaphore, tracker)

    # MAKE PROMETHEUS SERVER2 QUERIES
    for metric in s2_metrics:
        fetch_metric(snapshot_path, 9091, metric, formatted_start, formatted_end, n_steps, semaphore, tracker)

    delta_time = round(time.time() - tracker.exp_start, 2)
    print(f'\nEXTRACTION CONCLUDED IN: {delta_time} SECONDS')

############################################################################################################################
############################################################################################################################

# PARSE PYTHON ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--start",
    type=str,
    default='foo',
    help="Experiment start",
)

parser.add_argument(
    "-e",
    "--end",
    type=str,
    default='bar',
    help="Experiment end",
)

parser.add_argument(
    "-i",
    "--interval",
    type=int,
    default=1,
    help="Fetch data every n seconds",
)

# TODO: ADD BATCH SIZE AS ARGUMENT?

# GO
py_args = parser.parse_args()
create_snapshot(py_args.start, py_args.end, py_args.interval)

# clear && python3 snapshot.py --start "2023-12-21 06:18:02" --end "2023-12-21 06:29:06" --interval 3





