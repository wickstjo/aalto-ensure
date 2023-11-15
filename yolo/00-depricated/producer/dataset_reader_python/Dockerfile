FROM python:3.8.18
LABEL authors="anton"
ADD datasets_in_docker_image .
ADD dataset_reader_multiprocessing.py .
ADD day_night_cycle.py .
ADD kafka_utils.py .
ADD requirements.txt .
#RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
#RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "./dataset_reader_multiprocessing.py"]