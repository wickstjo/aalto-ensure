# ENSURE-workload-processing

This repository contains scripts that can consume datasets from Kafka.

Everything can be run locally after installing dependencies.

Additionally, all scripts can also run
in Docker containers and therefore supports Kubernetes.

## Changelog

Tags in docker hub (and preferably also git):

Yolo-inference:
https://hub.docker.com/repository/docker/debnera/ensure-yolo-inference/general

Dispatcher:
https://hub.docker.com/repository/docker/debnera/ensure-sensor-data-service/general

- V0.3:
  - Add smaller custom yolo models for reduced computational load.
  - Dispatcher now chooses yolo models based on decaying running 
  average processing time of each yolo model. 
  - Dispatcher --qos flag can be used to set target processing time in ms.
- V0.2-test: 
  - Add a draft for sensor data service, 
  that randomly forwards data to multiple different yolo models.
  - "Test"-appendix indicates that this is work-in-progress and 
  might contain unfinished features
- V0.1: Initial test setup where all data is fed to a single yolo model

## A) Running with Docker:

With docker, all you need is to navigate to the desired folder and run:

`docker-compose up`

## B) Running without Docker:

Recommended way is to either create a new virtualenv or conda env.
Conda is especially useful for more complex setups, 
such adding cuda-support to PyTorch.

Conda:

`conda env create --no-default-packages -f conda.yaml`

`conda activate ensure-workload-processing`

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
