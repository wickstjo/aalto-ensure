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
        return False

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

def fetch_metric(base_path, prometheus_port, query, start_time, end_time):

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

    # CREATE SUB DIR FOR QUERY
    dir_path = f'{base_path}/{query}'
    os.mkdir(dir_path)

    metrics_created = False
    
    # LOOP THROUGH EACH SEGMENT, COMBINING THEIR QUERY OUTPUT
    for nth_chunk, (t1, t2) in enumerate(segments):
        
        # MAKE GET REQUEST
        URL = f'http://130.233.193.117:{prometheus_port}/api/v1/query_range?query={query}&start={t1}&end={t2}&step=1s'
        results = requests.get(URL).json()['data']['result']

        # PREP THE VALUES DATAFRAME
        cols = [x for x in range(len(results))]
        rows = [x for x in range(int(t1), int(t2))]
        dataframe = pandas.DataFrame(columns=cols, index=rows)

        # PREP METRICS CONTAINER
        metrics_container = []
                
        for nth_metric, item in enumerate(results):
    
            # ZIP TUPLE LIST INTO DICT
            # EXTRACT ELEMENTS FROM KV LIST
            timestamps = [x[0] for x in item['values']]
            values = [x[1] for x in item['values']]
            as_dict = dict(zip(timestamps, values))

            # EVERYTHING PASSED, TO PUSH IN VALUES TO CONTAINER
            metrics_container.append(item['metric'])
            dataframe[nth_metric] = as_dict

        # CREATE CHUNK PREFIX
        chunk_prefix = str(nth_chunk).zfill(3)

        # SAVE THE METRICS OBJECTS AS JSON LIST
        if not metrics_created:
            json_save(f'{dir_path}/000-metrics.json', metrics_container)
            metrics_created = True

        # SAVE THE DATAFRAME AS A CSV
        dataframe.to_csv(f'{dir_path}/{chunk_prefix}-values.csv')

def create_snapshot(start_time, end_time):

    # GENERATE UNIQUE SNAPSHOT PATH
    now = str(int(time.time()))
    snapshot_path = f'snapshots/{now}'

    # CREATE THE MAIN DIR
    os.mkdir(snapshot_path)
    nth = 0
    total = 1728

    names = get_names(9090)
    if names == False:
        return
    
    # FETCH KUBERNETES DATA FROM SERVER 1
    for query in names:
        fetch_metric(snapshot_path, 9090, query, start_time, end_time)

        nth += 1
        percent = round((nth/total) * 100, 4)
        print(f'{nth}/{total} ({percent}%)\t\t {query}')

    # FETCH KAFKA DATA FROM SERVER 2
    for query in get_names(9091, 'kafka'):
        fetch_metric(snapshot_path, 9091, query, start_time, end_time)

        nth += 1
        percent = round((nth/total) * 100, 4)
        print(f'{nth}/{total} ({percent}%)\t\t {query}')

create_snapshot('2023-12-15 01:25:30', '2023-12-15 05:25:30')