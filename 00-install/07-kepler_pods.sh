# CREATE INSTALL FILE (COPY THIS CONTENT INTO IT)
# sudo nano create_kepler.sh && sudo chmod +x create_kepler.sh && sudo ./create_kepler.sh

# git clone --depth 1 git@github.com:sustainable-computing-io/kepler.git
git clone --depth 1 https://github.com/sustainable-computing-io/kepler
cd kepler

# COMPILE & DEPLOY KEPLER MANIFESTS
make tools
make build-manifest OPTS="PROMETHEUS_DEPLOY HIGH_GRANULARITY ESTIMATOR_SIDECAR_DEPLOY"
kubectl apply -f _output/generated-manifest/deployment.yaml
kubectl get pods -A -w

# PORT FORWARD GRAFANA/PROMETHEUS
# kubectl -n monitoring port-forward svc/grafana 3000 & kubectl -n monitoring port-forward svc/prometheus-k8s 9090
# kubectl -n monitoring port-forward svc/grafana 3000 --address=192.168.1.152
# kubectl -n monitoring port-forward svc/prometheus-k8s 9090 --address=192.168.1.152