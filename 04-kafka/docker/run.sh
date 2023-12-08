# NUKE OLD KUBE DEPLOYMENTS IF THEY EXIST
kubectl delete --ignore-not-found=true -f ../../yolo/yolo_depl.yaml

# CLEAN UP OLD HANGING GABARGE, THEN CREATE FRESH ENVIRONMENT
docker volume prune -f
docker compose up --force-recreate --renew-anon-volumes --remove-orphans

# NUKE OLD KUBE DEPLOYMENTS IF THEY EXIST
kubectl delete --ignore-not-found=true -f ../../yolo/yolo_depl.yaml