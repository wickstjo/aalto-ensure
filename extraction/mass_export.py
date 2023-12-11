import requests, pandas, json, os, shutil
from datetime import datetime
import time

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

def fetch_metric(base_path, prometheus_port, query, start_time, end_time):

    # CONVERT DATES TO UNIX TIMESTAMPS
    date_format = '%Y-%m-%d %H:%M:%S'
    formatted_start = str(int(datetime.strptime(start_time, date_format).timestamp()))
    formatted_end = str(int(datetime.strptime(end_time, date_format).timestamp()))

    # MAKE GET REQUEST
    URL = f'http://130.233.193.117:{prometheus_port}/api/v1/query_range?query={query}&start={formatted_start}&end={formatted_end}&step=1s'
    results = requests.get(URL).json()['data']['result']

    # TIMESTAMP LABELS
    # timestamps = pandas.date_range(start='2023-12-11 07:31:00', end='2023-12-11 07:32:00', freq='S')

    # PREP THE DATAFRAME
    cols = [x for x in range(len(results))]
    rows = [x for x in range(int(formatted_start), int(formatted_end))]
    dataframe = pandas.DataFrame(columns=cols, index=rows)

    metrics_container = []

    # CREATE SUB DIR
    dir_path = f'{base_path}/{query}'
    os.mkdir(dir_path)
    
    for nth, item in enumerate(results):

        # ZIP TUPLE LIST INTO DICT
        # EXTRACT ELEMENTS FROM KV LIST
        timestamps = [x[0] for x in item['values']]
        values = [x[1] for x in item['values']]
        as_dict = dict(zip(timestamps, values))

        # EVERYTHING PASSED, TO PUSH IN VALUES TO CONTAINER
        metrics_container.append(item['metric'])
        dataframe[nth] = as_dict

    # SAVE THE METRICS OBJECTS AS JSON LIST
    json_save(f'{dir_path}/metrics.json', metrics_container)

    # SAVE THE DATAFRAME AS A CSV
    dataframe.to_csv(f'{dir_path}/values.csv')

def create_snapshot(start_time, end_time):

    # GENERATE UNIQUE SNAPSHOT PATH
    now = str(int(time.time()))
    snapshot_path = f'snapshots/{now}'

    # CREATE THE MAIN DIR
    os.mkdir(snapshot_path)

    # FETCH KUBERNETES DATA FROM SERVER 1
    for query in get_names(9090):
        fetch_metric(snapshot_path, 9090, query, start_time, end_time)

    # FETCH KAFKA DATA FROM SERVER 2
    for query in get_names(9091, 'kafka'):
        fetch_metric(snapshot_path, 9091, query, start_time, end_time)

create_snapshot('2023-12-11 01:44:15', '2023-12-11 03:44:15')