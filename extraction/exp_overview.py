import os, json, hashlib, time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from threading import Thread, Semaphore
from matplotlib.offsetbox import AnchoredText

def hash_dict(data_dict):
    json_str = json.dumps(data_dict, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

def load_json(path):
    with open(path) as json_data:
        file_contents = json_data.read()
        payload = json.loads(file_contents)
        json_data.close()
        return payload

def find_statics(experiment_id, metric_name):

    # CONTAINERS
    metrics = {}
    values = {}
    
    # FETCH ALL METRICS DIR NAMES, IN ALPHABETICAL ORDER
    metric_path = f'snapshots/{experiment_id}/{metric_name}'
    json_batches = os.listdir(metric_path)
    json_batches.sort()
    
    # LOOP THROUGH BATCH FILES
    for batch in json_batches:
        json_file = load_json(f'{metric_path}/{batch}')
        
        for item in json_file['data']['result']:
            hash_id = hash_dict(item['metric'])
            values_dict = dict(item['values'])

            if hash_id not in metrics:
                metrics[hash_id] = item['metric']

            if hash_id not in values:
                values[hash_id] = values_dict
            else:
                values[hash_id].update(values_dict)

    # CREATE DATAFRAME FROM VALUES DICT
    values_df = pd.DataFrame(values)
    
    return metrics, values_df

def metric_overview(df, metric_name, base_path):
    container = []
    n_rows = len(df)
    cols = df.columns.to_list()

    # COMPUTE THE SIMILARITY PERCENTAGE; 0=GOOD, 1=BAD
    for col in cols:
        values_count = len(df[col].value_counts().to_list())
        percent = round((n_rows - values_count) / n_rows, 2)
        container.append((col, percent))

    # SORT THE CONTAINER BASED ON THE PERCENTAGE VALUE
    sorted_cont = sorted(container, key=lambda x: x[1])

    # CREATE SUBPLOTS
    size_factor = 0.6
    
    fig = plt.figure(figsize=(16*size_factor, 4*size_factor))
    gs = fig.add_gridspec(1, 1)
    
    # CREATE THE NEW AXIS
    axis = fig.add_subplot(gs[0, 0])
    
    # EXTRACT LABELS AND VALUES FROM DF
    #labels = [x[0] for x in sorted_cont]
    labels = [x for x in range(len(sorted_cont))]
    values = [x[1] for x in sorted_cont]

    # PLOT DATA & SET TITLE
    axis.plot(labels, values)
    axis.set_title(f'METRIC: {metric_name}', fontsize=8)

    # COMPUTE THE AVERAGE PERCENTAGE
    avg_pct = 0

    if len(values) > 0:
        avg_pct = round(sum(values) / len(values), 2)

    # STATS DICT FOR TEXTBOX
    info_dict = {
        'n_metrics': len(cols),
        'n_rows': n_rows,
        'avg_pct': avg_pct,
    }

    # ADD TEXTBOX WITH STATISTICS
    text_box = AnchoredText(json.dumps(info_dict, indent=4), frameon=True, loc=4, pad=0.5, prop=dict(fontsize=7))
    plt.setp(text_box.patch, facecolor='wheat', alpha=0.5)
    axis.add_artist(text_box)
    
    # CONFIG EACH AXIS
    for ax in fig.axes:
        ax.margins(x=0)
        ax.grid(alpha=0.3)
        ax.set_facecolor("#F7F7F7")
        ax.tick_params(axis='both', which='major', labelsize=8)
    
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    plt.tight_layout()

    if str(avg_pct) == '0':
        padded_pct = 'EMPTY'
    else:
        padded_pct = str(int(avg_pct * 100)).zfill(3)
    
    fig.savefig(f'{base_path}/{padded_pct}-{metric_name}.png', format="png", bbox_inches='tight')

    # WAIT & SAVE
    plt.close(fig)

def create_overviews(exp_ts):
    metrics = os.listdir(f'snapshots/{exp_ts}')
    n_metrics = len(metrics)

    img_dir = f'snapshots/screenshots/{exp_ts}'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    thread_lock = Semaphore(10)
    threads = []

    def foo(exp_ts, metric, thread_lock):
        metrics, df = find_statics(exp_ts, metric)
        metric_overview(df, metric, img_dir)
        
        print(f'{nth}/{n_metrics} {metric}', flush=True)
        thread_lock.release()
    
    for nth, metric in enumerate(metrics):
        thread_lock.acquire()
        thread = Thread(target=foo, args=(exp_ts, metric, thread_lock))
        threads.append(thread)
        thread.start()
    
    # WAIT FOR THREADS TO FINISH
    [thread.join() for thread in threads]

#create_overviews(1706192253)
create_overviews(1706275648)