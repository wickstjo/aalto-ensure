# CREATE INSTALL FILE (COPY THIS CONTENT INTO IT)
# sudo nano create_monitoring.sh && sudo chmod +x create_monitoring.sh && sudo ./create_monitoring.sh

# CLONE THE PROMETHEUS+GRAFANA KUBE PACK
git clone --depth 1 https://github.com/prometheus-operator/kube-prometheus
# cd kube-prometheus

# DEPLOY IT VIA MANIFESTS
kubectl apply --server-side -f kube-prometheus/manifests/setup
kubectl wait --for condition=Established --all CustomResourceDefinition --namespace=monitoring
kubectl apply -f kube-prometheus/manifests/
# kubectl delete -f kube-prometheus/manifests/

echo -e "\n#####################################\n"

# WATCH IT FINISH
kubectl get pods -A -w


# PORT FORWARD GRAFANA/PROMETHEUS
# kubectl -n monitoring port-forward svc/grafana 3000 --address=130.233.193.117
# kubectl -n monitoring port-forward svc/prometheus-k8s 9090 --address=130.233.193.117
# kubectl -n kafka port-forward svc/kafka-service 9092 --address=130.233.193.117




# kubectl rollout restart deployment prometheus-adapter -n monitoring