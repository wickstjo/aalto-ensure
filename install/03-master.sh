# TURN OFF LINUX SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld
# sudo swapoff -a && systemctl stop firewalld && sudo systemctl disable firewalld

# COMMENT OUT: disabled_plugins = ["cri"]
# sudo nano /etc/containerd/config.toml 

# UPDATE IP TABLE THING FROM 0 => 1
echo "1" | cat >> /proc/sys/net/bridge/bridge-nf-call-iptables

# SETUP CLUSTER CONTROL PLANE (SET MACHINE IN KUBE MASTER MODE) ?
sudo kubeadm init --apiserver-advertise-address=192.168.1.230
# kubeadm init --pod-network-cidr=10.10.0.0/16 --apiserver-advertise-address=master_nodeIP

# THE COMMAND GENERATES A JOIN STRING
# kubeadm join 192.168.1.230:6443 \
#     --token c50a2z.i3iiqcd7fayt4qg8 \
# 	--discovery-token-ca-cert-hash sha256:70e24a4d99b20e19722bf7cfaaf059077ece71768227f6f0a0d90b3e20eb8498 


#####################################################################################################################
#####################################################################################################################


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
