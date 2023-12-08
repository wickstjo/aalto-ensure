CLOUD_GATEWAY=$1

screen -S grafana_pf ssh -L 3000:localhost:3000 $CLOUD_GATEWAY
screen -S prometheus_pf ssh -L 9090:localhost:9090 $CLOUD_GATEWAY
screen -ls
