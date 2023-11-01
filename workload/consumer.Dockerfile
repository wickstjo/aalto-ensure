FROM python:3

# SET WORKDIT & CLONE OVER NECESSARI FILES
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY consumer.py /app/consumer.py

# INSTALL DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

# RUN CONSUMER
CMD ["python", "consumer.py"]

# docker build --no-cache -t workload_consumer -f consumer.Dockerfile .
# docker run workload_consumer

# docker save -o workload_consumer.tar workload_consumer:latest
# docker load -i workload_consumer.tar

# docker run -p 5000:5000 --name registry registry:2
# docker tag workload_consumer:latest 192.168.1.231:5000/workload_consumer:latest
# docker push 192.168.1.231:5000/workload_consumer:latest

# image: 192.168.1.231:5000/workload_consumer:latest