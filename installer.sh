# VERIFY NETWORK CONNECTION
ping www.google.com -c 5

# DISABLE SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld

# ENABLE BRIDGE TRAFFIC
lsmod | grep br_netfilter
sudo modprobe br_netfilter

# APPEND TO NETWORK CONFIG
echo "br_netfilter" | cat >> /etc/modules-load.d/k8s.conf
echo "net.bridge.bridge-nf-call-ip6tables = 1" | cat >> /etc/sysctl.d/k8s.conf
echo "net.bridge.bridge-nf-call-iptables = 1" | cat >> /etc/sysctl.d/k8s.conf
sudo sysctl --system

#####################################################################
#####################################################################

# INSTALL YUM?
# INSTALL DOCKER

#####################################################################
#####################################################################

# SETUP DOCKER DAEMON
sudo mkdir /etc/docker
echo "
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
" | cat >> /etc/docker/daemon.json

# RESTART DOCKER SERVICES
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl enable docker
sudo systemctl status docker

# INSTALL KUBEADM, KUBECTL, KUBELET
echo "
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum...\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum... https://packages.cloud.google.com/yum...
exclude=kubelet kubeadm kubectl
" | cat >> /etc/yum.repos.d/kubernetes.repo

# EFFECTIVELY DISABLE SE-LINUX
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
sudo systemctl enable --now kubelet

# SET MACHINE IN KUBE MASTER MODE
kubeadm init --pod-network-cidr=10.10.0.0/16 --apiserver-advertise-address=master_nodeIP # SET MASTER NODE IP

#####################################################################
#####################################################################

# RUN IF REGULAR USER
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# RUN IF ROOT
export KUBECONFIG=/etc/kubernetes/admin.conf

#####################################################################
#####################################################################

# SETUP POD NETWORK -- https://kubernetes.io/docs/concepts/cluster-administration/addons/
kubectl apply -f [podnetwork].yaml
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s... version | base64 | tr -d '\n')"

# JOIN FOLLOWER AS ROOT
kubeadm join 192.168.74.10:6443 --token l431j0.0tz0bbuu7hj64lw5 --discovery-token-ca-cert-hash sha256:1743115f18a7b8761105ff5465cd1aeed74a2e8a3f326405da61681d07fdb0e0

#####################################################################
#####################################################################

# PUSH A TEST POD
kubectl run vsparkz --image nginx