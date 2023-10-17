# TURN OFF LINUX SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld
# sudo swapoff -a && systemctl stop firewalld && sudo systemctl disable firewalld

echo "##########################################################################################"
echo "##########################################################################################"
echo ""
echo ""

# SETUP CLUSTER CONTROL PLANE
sudo kubeadm init \
    --pod-network-cidr=192.168.0.0/16 \
    --cri-socket=unix:///var/run/cri-dockerd.sock

# sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --cri-socket=unix:///var/run/cri-dockerd.sock

# clear && kubectl get nodes --watch
# kubectl label nodes worker2 kubernetes.io/role=worker

echo ""
echo ""
echo "##########################################################################################"
echo "##########################################################################################"

# LAUNCH THE CLUSTER THROUGH BOILERPLATE CODE
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# CHECK THAT ALL KUBE SERVICES ARE RUNNING
# CORE DNS SHOULD STILL BE PENDING
kubectl get pods -A

# SETUP CALICO POD NETWORKING (CORE DNS)
# https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises
curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O
kubectl apply -f calico.yaml

# TRACK CALICOS PROGRESS
kubectl get pods -A --watch


# https://www.youtube.com/watch?v=o6bxo0Oeg6o&ab_channel=davidhwang


#####################################################################################################################
#####################################################################################################################

# sudo kubeadm init --apiserver-advertise-address=192.168.1.230
# kubeadm init --pod-network-cidr=10.10.0.0/16 --apiserver-advertise-address=master_nodeIP

# THE COMMAND GENERATES A JOIN STRING
# kubeadm join 192.168.1.230:6443 \
#     --token c50a2z.i3iiqcd7fayt4qg8 \
# 	--discovery-token-ca-cert-hash sha256:70e24a4d99b20e19722bf7cfaaf059077ece71768227f6f0a0d90b3e20eb8498 


# # To start using your cluster, you need to run the following as a regular user:

# mkdir -p $HOME/.kube
# sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
# sudo chown $(id -u):$(id -g) $HOME/.kube/config

# # Alternatively, if you are the root user, you can run:

# export KUBECONFIG=/etc/kubernetes/admin.conf


#####################################################################################################################
#####################################################################################################################

# OPEN IN ANOTHER TAB
# kubectl proxy --port=8080


# You should now deploy a pod network to the cluster.
# Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
#   https://kubernetes.io/docs/concepts/cluster-administration/addons/
