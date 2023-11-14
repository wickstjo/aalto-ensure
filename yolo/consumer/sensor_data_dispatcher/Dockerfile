FROM python:3.8.18 as base
LABEL authors="anton"
ADD requirements.txt .
RUN pip install -r requirements.txt

FROM base
ADD kafka_helpers.py .
ADD main.py .
ADD qos_tracker.py .
ADD sensor_headers.py .
ENTRYPOINT ["python", "./main.py"]