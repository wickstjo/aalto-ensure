# sudo nano master.sh && sudo chmod +x master.sh && sudo ./master.sh

# SET HOSTNAME FOR SSH CLARITY
# sudo hostnamectl set-hostname master

# TURN OFF LINUX SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld
# sudo swapoff -a && systemctl stop firewalld && sudo systemctl disable firewalld

echo -e "\n##########################################################################################\n"

# TO START CLUSTER AFTER REBOOT
# systemctl enable kubelet

# SETUP CLUSTER CONTROL PLANE
sudo kubeadm init \
    --cri-socket=unix:///var/run/cri-dockerd.sock \
    --pod-network-cidr=10.0.0.0/8
    # --pod-network-cidr=192.168.0.0/16 \

# CIDR NETWORK FIX
# https://stackoverflow.com/questions/56135923/kube-state-metrics-error-failed-to-create-client-i-o-timeout

echo -e "\n##########################################################################################\n"

# ADD THE FOLLOWING PROPS TO THE KUBE CONFIG
# sudo nano /etc/kubernetes/admin.conf

# authentication:
#   webhook: true
# authorization:
#   mode: Webhook

# LAUNCH THE CLUSTER THROUGH BOILERPLATE CODE
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config && kubectl get pods -A --watch

echo -e "\n##########################################################################################\n"

# SETUP CALICO POD NETWORKING (CORE DNS)
# https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises
curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O
kubectl apply -f calico.yaml

# TRACK CALICOS PROGRESS
clear && kubectl get pods -A --watch

# curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O && kubectl apply -f calico.yaml && kubectl get pods -A --watch

# POST INSTALL STUFF
echo -e "\n##########################################################################################\n"

# GENERATE JOIN STRING
kubeadm token create --print-join-command

echo -e "\n##########################################################################################\n"

kubectl get nodes --watch

# WATCH CLUSTER
# clear && kubectl get nodes --watch

# RENAME WORKER NODES
# kubectl label nodes worker1 kubernetes.io/role=worker