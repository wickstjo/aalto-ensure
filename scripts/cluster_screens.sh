CLOUD_GATEWAY=$1
MASTER_IP=$2

# TUNNELS TO CLOUD MACHINE
screen -S grafana_tunnel ssh -R 3000:130.233.193.117:3000 $CLOUD_GATEWAY
screen -S prometheus_tunnel ssh -R 9090:130.233.193.117:9090 $CLOUD_GATEWAY

# KUBERNETES SERVICE PORT FORWARDS
screen -S grafana_pf kubectl -n monitoring port-forward svc/grafana 3000 --address=$MASTER_IP
screen -S prometheus_pf kubectl -n monitoring port-forward svc/prometheus-k8s 9090 --address=$MASTER_IP

screen -ls
