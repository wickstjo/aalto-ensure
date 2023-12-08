# DEPLOY IT VIA MANIFESTS
kubectl apply --server-side -f /setup
kubectl wait --for condition=Established --all CustomResourceDefinition --namespace=monitoring
kubectl apply -f .

echo -e "\n#####################################\n"

# WATCH THEM FINISH
kubectl get pods -A -w