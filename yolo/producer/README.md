# ENSURE-workload-processing

This repository contains scripts for reading datasets into Kafka.

Everything can be run locally after installing dependencies.

Additionally, all scripts that consume data from Kafka can also run
in Docker containers and therefore supports Kubernetes.

## Datasets

Datasets can be downloaded from:

https://drive.google.com/drive/folders/1enssuS5C0C16GDhqxFDPoWaGKS3o2Rov?usp=sharing

## Changelog

Tags in docker hub (and preferably also git):

https://hub.docker.com/repository/docker/debnera/ensure-dataset-feeder/general

- V0.3:
  - Migrate day-night cycle to dataset reader from the dataset generator.
  - Add more args (--help for more information).
  - Add "--max_vehicles" arg.
  - Add more reasonable default argument values to docker-compose.
- V0.2-test: 
  - Add more args.
  - Add compatibility for V0.2-test data consumers.
- V0.1: Initial test setup where all data is fed to a single yolo model.

## A) Running standalone executables

Some python scripts are compiled into a standalone executable. 
They should work without installing any dependencies.
The `dist`folder should contain executables from the latest tagged commit.

Example: 

`./dist/dataset_reader --help`

## B) Running with Docker:

With docker, all you need is to navigate to the desired folder and run:

`docker-compose up`

## C) Running without Docker:

Recommended way is to either create a new virtualenv or conda env.
Conda is especially useful for more complex setups, 
such adding cuda-support to PyTorch.

Conda:

`conda env create --no-default-packages -f conda.yaml`

`conda activate ensure-workload-feeder`

Virtualenv:

`virtualenv -p python3.8 venv`

`source venv/bin/activate`

Finally, install requirements with pip:

`pip install -r requirements.txt`

And run the program:

`python dataset_reader.py --help`


## Pushing images to docker

Build with a new tag:

`docker build . -t debnera/ensure-yolo-inference:0.1`

Push tag to Docker hub:

`docker push debnera/ensure-yolo-inference:0.1`


## Creating standalone executables from Python scripts:

You can create standalone executables with PyInstaller.
Before running, you need to install all necessary dependencies
and the PyInstaller (`pip install pyinstaller`).

`pyinstaller -F --clean program.py`

The `-F` flag packs all files to a single executable file.
The `--clean` flag should clean up temporary files.
