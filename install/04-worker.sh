# CHANGE HOSTNAME
# sudo nano /etc/hostname
# sudo reboot

# TURN OFF LINUX SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld
# sudo swapoff -a && systemctl stop firewalld && sudo systemctl disable firewalld

echo "##########################################################################################"
echo "##########################################################################################"
echo ""
echo ""

# JOIN THE KUBE CLUSTER
sudo kubeadm join 192.168.1.193:6443 \
    --token 6i4sfh.3wtuyebwnvv2xrzq \
    --discovery-token-ca-cert-hash sha256:7f2ad98e9171d827309d7ef6b6b84feb17416f0e64f837672ac1b2571d74e08a \
    --cri-socket=unix:///var/run/cri-dockerd.sock

# sudo kubeadm join 192.168.1.193:6443 --token 6i4sfh.3wtuyebwnvv2xrzq --discovery-token-ca-cert-hash sha256:7f2ad98e9171d827309d7ef6b6b84feb17416f0e64f837672ac1b2571d74e08a --cri-socket=unix:///var/run/cri-dockerd.sock
# clear && kubectl get nodes --watch
# kubectl label nodes worker2 kubernetes.io/role=worker

echo ""
echo ""
echo "##########################################################################################"
echo "##########################################################################################"

# SETUP CALICO POD NETWORKING (CORE DNS)
# https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises
curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O
kubectl apply -f calico.yaml

# TRACK CALICOS PROGRESS
kubectl get pods -A --watch