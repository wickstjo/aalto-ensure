# CREATE INSTALL FILE (COPY THIS CONTENT INTO IT)
# sudo nano reset_node.sh && sudo chmod +x reset_node.sh && sudo ./reset_node.sh

# RESET THE NODES KUBEADM SETUP & NUKE ALL OLD KUBERNETES FILES
sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock
sudo rm -rf /home/wickstjo/.kube

# TURN OFF LINUX SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld

# JOIN THE MASTER NODES' CLUSTER
sudo kubeadm join 130.233.193.117:6443 \
    --token 69fqem.ylsqhzvsuvgh6g24 \
    --discovery-token-ca-cert-hash sha256:69e1195cc31d8d224ddd0767eb72619f916c2169238549a7b444c4997788be68 \
    --cri-socket=unix:///var/run/cri-dockerd.sock