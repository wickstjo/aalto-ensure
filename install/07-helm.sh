curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

helm repo add kepler https://sustainable-computing-io.github.io/kepler-helm-chart
helm search repo kepler

helm install kepler kepler/kepler --namespace kepler --create-namespace
helm install kepler kepler/kepler --values values.yaml --namespace kepler --create-namespace'


# # COMMENT OUT CRI DISABLE ???
# sudo nano /etc/containerd/config.toml
# sudo systemctl restart containerd
# sudo systemctl restart kubelet