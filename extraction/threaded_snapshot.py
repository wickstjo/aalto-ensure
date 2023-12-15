import requests, pandas, json, os, shutil
from datetime import datetime
import time, math
from IPython.display import clear_output
from threading import Thread, Semaphore

def get_names(port, allowed_prefix=''):
    try:
        result = requests.get(f'http://130.233.193.117:{port}/api/v1/label/__name__/values')
        container = []

        for metric in result.json()['data']:
            if metric[0:len(allowed_prefix)] == allowed_prefix:
                container.append(metric)

        return container
    
    except:
        raise(f'COULD NOT PING INSTANCES AT PORT {port}')

def json_save(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def segment_timestamps(unix_start, unix_end, batch_size=1800):

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

def fetch_metric(base_path, prometheus_port, query, start_time, end_time, semaphore, tracker):

    # RESEVE A THREAD SLOT
    semaphore.acquire()

    try:
        # CONVERT DATES TO UNIX TIMESTAMPS
        date_format = '%Y-%m-%d %H:%M:%S'
        formatted_start = int(datetime.strptime(start_time, date_format).timestamp())
        formatted_end = int(datetime.strptime(end_time, date_format).timestamp())
    
        # ADJUSTED TIMESTAMPS FOR GMT+2 TIME
        two_hours = 60*60*2
        formatted_start -= two_hours
        formatted_end -= two_hours
    
        # PROMETHEUS ONLY ALLOWS QUERIES WITH LESS THAN 11K ROWS
        # SEGMENT LARGE TIMESTAMPS INTO SMALLER PAIRS TO BYPASS THIS LIMITATION
        segments = segment_timestamps(formatted_start, formatted_end, 200)
    
        # DATA CONTAINERS
        metrics_container = []
        values_container = {}
    
        # LOOP THROUGH EACH SEGMENT, COMBINING THEIR QUERY OUTPUT
        for t1, t2 in segments:
            
            # MAKE GET REQUEST
            URL = f'http://130.233.193.117:{prometheus_port}/api/v1/query_range?query={query}&start={t1}&end={t2}&step=1s'
            #URL = f'http://130.233.193.117:{prometheus_port}/api/v1/query_range?query=kepler_node_package_joules_total&start={t1}&end={t2}&step=1s'
            results = requests.get(URL).json()['data']['result']
            
            for nth_metric, item in enumerate(results):
    
                # INITIALIZE BOTH CONTAINERS
                if nth_metric not in values_container:
                    values_container[nth_metric] = {}
        
                # ZIP TUPLE LIST INTO DICT
                # EXTRACT ELEMENTS FROM KV LIST
                timestamps = [x[0] for x in item['values']]
                values = [x[1] for x in item['values']]
                as_dict = dict(zip(timestamps, values))
    
                # ADD METRIC IF IT DOESNT ALREADY EXIST
                if item['metric'] not in metrics_container:
                    metrics_container.append(item['metric'])
                
                # COMBINE OLD AND NEW VALUES DICT
                values_container[nth_metric].update(as_dict)
    
        #print('ALL METRICS WERE UNIFORM. OK!')
    
        # CREATE SUB DIR FOR QUERY
        dir_path = f'{base_path}/{query}'
        os.mkdir(dir_path)
    
        # PREP THE DATAFRAME
        cols = [x for x in range(len(metrics_container))]
        rows = [x for x in range(int(formatted_start), int(formatted_end))]
        dataframe = pandas.DataFrame(columns=cols, index=rows)
        dataframe = dataframe.rename_axis('Timestamp')
    
        # INJECT VALUES INTO DATAFRAME
        for key, values in values_container.items():
            dataframe[key] = values
    
        # SAVE THE METRICS OBJECTS AS JSON LIST
        json_save(f'{dir_path}/metrics.json', metrics_container)
    
        # SAVE THE DATAFRAME AS A CSV
        dataframe.to_csv(f'{dir_path}/values.csv')
    except:
        print(f'SOMETHING WENT WRONG WITH QUERY: {query}')

    # INCREMENT THE TRACKER & MAKE ROOM FOR THE NEXT THREAD
    tracker.increment(query)
    semaphore.release()

class Tracker:
    def __init__(self):
        self.accumulator = Semaphore(1)
        self.value = 0
        self.total = 1728
        
    def increment(self, query):
        self.accumulator.acquire()
        self.value += 1
        percent = round((self.value/self.total) * 100, 2)
        print(f'{self.value}/{self.total} ({percent}%)\t\t{query}', flush=True)
        self.accumulator.release()

def create_snapshot(start_time, end_time):

    # GENERATE UNIQUE SNAPSHOT PATH
    now = str(int(time.time()))
    snapshot_path = f'snapshots/{now}'

    # CREATE THE MAIN DIR
    os.mkdir(snapshot_path)
    nth = 0
    
    # MAKE REQUESTS CONCURRENTLY
    semaphore = Semaphore(1)
    tracker = Tracker()
    threads = []
    
    # FETCH KUBERNETES DATA FROM SERVER 1
    for nth, query in enumerate(get_names(9090)):
        thread = Thread(target=fetch_metric, args=(snapshot_path, 9090, query, start_time, end_time, semaphore, tracker))
        threads.append(thread)

    # FETCH KAFKA DATA FROM SERVER 2
    for query in get_names(9091, 'kafka'):
        thread = Thread(target=fetch_metric, args=(snapshot_path, 9091, query, start_time, end_time, semaphore, tracker))
        threads.append(thread)

    # START THE THREADS & WAIT FOR EACH ONE TO FINISH
    [x.start() for x in threads]
    [x.join() for x in threads]

create_snapshot('2023-12-15 01:25:30', '2023-12-15 05:25:30')