# CREATE INSTALL FILE (COPY THIS CONTENT INTO IT)
# sudo nano create_helm.sh && sudo chmod +x create_helm.sh && sudo ./create_helm.sh

curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh && ./get_helm.sh

# ADD KEPLER REPO TO HELM
helm repo add kepler https://sustainable-computing-io.github.io/kepler-helm-chart
helm search repo kepler

# INSTALL KEPLER VIA HELM
# helm install kepler kepler/kepler --namespace kepler --create-namespace
helm install kepler kepler/kepler --values values.yaml --namespace kepler --create-namespace

kubectl get pods -A -w

# # COMMENT OUT CRI DISABLE ???
# sudo nano /etc/containerd/config.toml
# sudo systemctl restart containerd
# sudo systemctl restart kubelet



# kubectl describe pod kepler-5n8hg -n kepler