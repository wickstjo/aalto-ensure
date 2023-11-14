# A) Running with Docker:

With docker, all you need is to run:

`docker-compose up`

## B) Running without Docker:

Recommended way is to either create a new virtualenv or conda env

Conda:

`conda install -n ensure-workload-processing pip`

`conda activate ensure-workload-processing`

Virtualenv:

`virtualenv -p python3.8 venv`
`source venv/bin/activate`

Install dependencies:

`pip install -r requirements.txt`

Finally, run the application:

`python yolo_inference.py`


## Pushing images to docker

Build with a new tag:

`docker build . -t debnera/ensure-yolo-inference:0.1`

Push tag to Docker hub:

`docker push debnera/ensure-yolo-inference:0.1`


## Creating standalone executables from Python scripts:

`pyinstaller -F --clean program.py`
