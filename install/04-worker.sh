# sudo nano worker.sh && sudo chmod +x worker.sh && sudo ./worker.sh

# SET HOSTNAME FOR SSH CLARITY
# sudo hostnamectl set-hostname worker1

# TURN OFF LINUX SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld

echo -e "\n##########################################################################################\n"


# sudo swapoff -a && systemctl stop firewalld && sudo systemctl disable firewalld

kubeadm join 192.168.1.120:6443 --token lxl5v6.aldzthzvq3861w95 --discovery-token-ca-cert-hash sha256:f35a08d8302f4a0e9c4e1e1fd502a8e2661d2038d8fb0dcbf404be491b88089f --cri-socket=unix:///var/run/cri-dockerd.sock

# --cri-socket=unix:///var/run/cri-dockerd.sock

# kubeadm join 192.168.1.7:6443 \
#     --token vddjj0.j7mxwxbym1plzo5d \
#     --discovery-token-ca-cert-hash sha256:5c8a41fec2cebd2ecae8c9447e02cd426ae3f199c4fa9872a6216ecfa7ffe904 \
#     --cri-socket=unix:///var/run/cri-dockerd.sock

# clear && kubectl get nodes --watch
# kubectl label nodes worker2 kubernetes.io/role=worker