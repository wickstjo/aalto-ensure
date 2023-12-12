# DEPLOY IT VIA MANIFESTS
kubectl apply --server-side -f /setup
kubectl wait --for condition=Established --all CustomResourceDefinition --namespace=monitoring
kubectl apply -f .