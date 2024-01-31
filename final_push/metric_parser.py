import zipfile
import pandas as pd

def parse_metric(zip_file, metric_name):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:

        # GENERATE A LIST OF ALL CONTAINED FILES
        # AND CONSTRUCT THE FILE PREFIX FOR THE METRIC FILES
        items = zip_ref.namelist()
        prefix = items[0] + metric_name

        # FILTER ONLY THE JSON FILES THAT ARE RELEVANT TO THE METRIC
        # AND SORT THEM IN CHRONOLOGICAL ORDER
        json_files = [x for x in items if x.startswith(prefix) and x.endswith('.json')]
        json_files.sort()

        # TEMP CONTAINERS
        values_container = {}
        stats_container = {}

        # LOOP THROUGH THE JSON FILES
        for path in json_files:
            with zip_ref.open(path) as json_file:
                json_data = json.load(json_file)

                # LOOP THROUGH EACH SUB-METRIC
                for item in json_data['data']['result']:
                    header = json.dumps(item['metric']) 
                    values = dict(item['values'])

                    # ADD HEADER KEY IF IT DOESNT EXIST
                    if header not in values_container:
                        values_container[header] = {}

                    # OTHERWISE, MERGE OLD AND NEW DICTS
                    values_container[header].update(values)

        # CONVERT VALUES DICT TO DATAFRAME
        values_df = pd.DataFrame(values_container)

        # GATHER SOME STATISTICS OF THE DF
        for metric in values_df.columns:
            n_rows = len(values_df[metric])
        
            # FIND HOW STATIC (%) THE VECTOR IS
            n_unique_values = len(values_df[metric].value_counts())
            static_percent = round(((n_rows - n_unique_values) / n_rows * 100), 2)
        
            # FIND THE PERCENTAGE OF NAN VALUES
            n_nans = values_df[metric].isna().sum()
            nan_percent = round((n_nans / n_rows) * 100, 2)
            
            stats_container[metric] = {
                'static%': static_percent,
                'nan%': nan_percent
            }

        # CONVERT THE STATS DICT TO A DF, THEN TRANSPOSE IT
        stats_df = pd.DataFrame(stats_container).transpose()
        
        return values_df, stats_df

################################################################ 
     
values, stats = parse_metric(
    zip_file='1706275648-8H-5s-KEPLER-SAMPLING.zip', 
    metric_name='apiserver_flowcontrol_current_inqueue_requests'
)