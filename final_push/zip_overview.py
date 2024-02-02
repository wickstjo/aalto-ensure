import zipfile, hashlib, json
import pandas as pd
from IPython.display import clear_output
import argparse, os

def full_overview(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:

        # GENERATE A LIST OF ALL CONTAINED FILES
        # AND CONSTRUCT THE FILE PREFIX FOR THE METRIC FILES
        dirs = zip_ref.namelist()
        path_prefix_len = len(dirs[0])

        # FIND JUST THE METRIC DIRS
        valid_dirs = [x for x in dirs[1:] if not x.endswith('.json')]
        valid_dirs.sort()
        n_dirs = len(valid_dirs)

        # UNIVERSAL METRIC COLLECTION
        overview = []

        # DEBUGGING FLUFF
        progress = []
        line_limit = 10

        for nth, current_dir in enumerate(valid_dirs):

            # PRINT PROGRESS REPORT
            #clear_output(wait=True)
            os.system('cls')
            progress.append(f'({nth}/{n_dirs}) {current_dir}')
            print(json.dumps(progress[-line_limit:], indent=4))

            # EXTRACT JUST THE METRIC NAME FOR LATER
            metric_name = current_dir[path_prefix_len:-1]

            # EXTRACT THE RELEVANT JSON FILES
            # SORT THEM IN CHRONOLOGICAL ORDER
            json_files = [x for x in dirs[1:] if x.startswith(current_dir) and x.endswith('.json')]
            json_files.sort()

            # TEMP CONTAINERS
            values_container = {}
    
            # LOOP THROUGH THE JSON FILES
            for path in json_files:
                with zip_ref.open(path) as json_file:
                    json_data = json.load(json_file)
    
                    # LOOP THROUGH EACH SUB-METRIC
                    for item in json_data['data']['result']:
                        stringified_props = json.dumps(item['metric']) 
                        values = dict(item['values'])
    
                        # ADD HEADER KEY IF IT DOESNT EXIST
                        if stringified_props not in values_container:
                            values_container[stringified_props] = {}
    
                        # OTHERWISE, MERGE OLD AND NEW DICTS
                        values_container[stringified_props].update(values)
    
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

                # PUSH THE RESULT TO THE OVERVIEW COLLECTION
                overview.append({
                    'metric_name': metric_name,
                    'metric_props': metric,
                    'static%': static_percent,
                    'nan%': nan_percent
                })

        # CONVERT TO DF & SAVE AS CSV
        overview_df = pd.DataFrame(overview) #.transpose()
        csv_filename = f'{zip_file[0:-4]}.csv'
        overview_df.to_csv(csv_filename, index=False)

        print(f'\nOVERVIEW CREATED ({csv_filename})')

# PARSE PYTHON ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--zip_file",
    type=str,
    default='foo',
    help="Zipfile to analyze",
)

#################################################################################################################
#################################################################################################################

py_args = parser.parse_args()
full_overview(py_args.zip_file)