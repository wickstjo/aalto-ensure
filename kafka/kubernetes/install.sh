kubectl apply -f kafka/zookeeper-depl.yaml
kubectl apply -f kafka/kafka-depl.yaml
kubectl get pods -A -w