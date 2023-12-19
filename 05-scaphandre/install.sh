# CLONE REPO
git clone https://github.com/hubblo-org/scaphandre
cd scaphandre

# SWITCH TO DEV BRANCH FOR FIX
git fetch
git switch dev

# CREATE NEW NAMESPACE & INSTALL SCAPHANDRE
# kubectl apply -f namespace.yaml
helm install --set serviceMonitor.namespace=monitoring --set serviceMonitor.enabled=true scaphandre helm/scaphandre