# openssl req -newkey rsa:4096 -nodes -sha256 -keyout domain.key -x509 -days 365 -out domain.crt

# GENERATE CERT & WHITELIST IP
openssl req -newkey rsa:4096 -nodes -sha256 -keyout domain.key -out domain.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=192.168.1.231" 
openssl x509 -req -days 365 -in domain.csr -signkey domain.key -out domain.crt -extfile <(echo "subjectAltName = IP:192.168.1.231")

# BUILD THE DOCKER IMAGE
docker build --no-cache -t workload_consumer -f consumer.Dockerfile .
# docker run workload_consumer

# docker save -o workload_consumer.tar workload_consumer:latest
# docker load -i workload_consumer.tar
# docker run -p 5000:5000 --name registry registry:2

# TAG & UPLOAD THE IMAGE TO REGISTRY
docker tag workload_consumer:latest 192.168.1.231:5000/workload_consumer:latest
docker push 192.168.1.231:5000/workload_consumer:latest

# docker tag workload_consumer:latest localhost:5000/workload_consumer:latest
# docker push localhost:5000/workload_consumer:latest

# image: 192.168.1.231:5000/workload_consumer:latest