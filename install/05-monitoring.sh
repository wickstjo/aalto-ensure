# CLONE THE PROMETHEUS+GRAFANA KUBE PACK
git clone --depth 1 https://github.com/prometheus-operator/kube-prometheus
cd kube-prometheus

# DEPLOY IT VIA MANIFESTS
kubectl apply --server-side -f manifests/setup
kubectl wait --for condition=Established --all CustomResourceDefinition --namespace=monitoring
kubectl apply -f manifests/

echo -e "\n\n"##########################################################################################"\n\n"

# WATCH IT FINISH
kubectl get pods -A --watch

# PORT FORWARD GRAFANA/PROMETHEUS
kubectl -n monitoring port-forward svc/grafana 3000 --address=192.168.1.120
kubectl -n monitoring port-forward svc/prometheus-k8s 9090 --address=192.168.1.120

# kubectl rollout restart deployment prometheus-adapter -n monitoring