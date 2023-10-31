FROM python:3

# SET WORKDIT & CLONE OVER NECESSARI FILES
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY workers/consumer.py /app/consumer.py

# INSTALL DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

# RUN CONSUMER
CMD ["python", "consumer.py"]

# docker build --no-cache -t worker -f worker.Dockerfile .
# docker run worker