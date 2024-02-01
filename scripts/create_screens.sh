# CREATE PORT FORWARDS TO CLOUD TUNNEL
screen -dmS grafana_pf ssh -R 3000:130.233.193.117:3000 ansure@ansurevm.northeurope.cloudapp.azure.com
screen -dmS prometheus_pf ssh -R 9090:130.233.193.117:9090 ansure@ansurevm.northeurope.cloudapp.azure.com
screen -dmS notebook_pf ssh -R 8888:130.233.193.117:8888 ansure@ansurevm.northeurope.cloudapp.azure.com

# KUBERNETES SERVICE PORT FORWARDS
screen -dmS grafana_pf kubectl -n monitoring port-forward svc/grafana 3000 --address=130.233.193.117
screen -dmS prometheus_pf kubectl -n monitoring port-forward svc/prometheus-k8s 9090 --address=130.233.193.117

screen -ls