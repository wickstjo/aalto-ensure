sudo swapoff -a
systemctl stop firewalld
sudo systemctl disable firewalld

sudo swapoff -a && systemctl stop firewalld && sudo systemctl disable firewalld

sudo kubeadm init --cri-socket=unix:///var/run/cri-dockerd.sock --pod-network-cidr=10.0.0.0/8

# ADD THE FOLLOWING PROPS TO THE KUBE CONFIG
sudo nano /etc/kubernetes/admin.conf

# echo "authentication:" | cat >> /etc/kubernetes/admin.conf

authentication:
  webhook: true
authorization:
  mode: Webhook

# RESTART KUBELET TO MAKE CHANGES TAKE PLACE
# sudo systemctl restart kubelet


# mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config && kubectl get pods -A --watch
# curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O && kubectl apply -f calico.yaml && kubectl get pods -A --watch


mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O
kubectl apply -f calico.yaml
kubectl get pods -A --watch

kubeadm token create --print-join-command