FROM python:3.8.18 as base
LABEL authors="anton"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
ADD requirements.txt .
RUN pip install -r requirements.txt

FROM base
ADD yolo_inference.py .
ADD models models
ENTRYPOINT ["python", "./yolo_inference.py"]