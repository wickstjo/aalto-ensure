# LOGIN TO DOCKER HUB IF NECESSARY
docker login

# BUILD THE DOCKER IMAGE
docker build --no-cache -t workload_consumer -f consumer.Dockerfile .
# docker run workload_consumer

# TAG & UPLOAD THE IMAGE TO DOCKER HUB REGISTRY
docker tag workload_consumer:latest wickstjo/workload_consumer:latest
docker push wickstjo/workload_consumer:latest