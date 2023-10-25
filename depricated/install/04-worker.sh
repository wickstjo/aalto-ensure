# RENAME THE HOST MACHINE
# ip addr | grep 192
# sudo hostnamectl set-hostname worker1 && sudo reboot

# CREATE INSTALL FILE (COPY THIS CONTENT INTO IT)
# sudo nano create_worker.sh && sudo chmod +x create_worker.sh && sudo ./create_worker.sh

# TURN OFF LINUX SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld

echo -e "\n##########################################################################################\n"

kubeadm join 192.168.1.128:6443 \
    --token yahpih.06jqo9c8ii0xijzx \
    --discovery-token-ca-cert-hash sha256:c4ce418eca97403c3128d5aea9353c7e53d2acded135b292e71fc5ebd69da13f \
    --cri-socket=unix:///var/run/cri-dockerd.sock

# --cri-socket=unix:///var/run/cri-dockerd.sock


# RENAME THE WORKER NODE ON MASTER
# kubectl get pods -A -w
# kubectl label nodes worker1 kubernetes.io/role=worker
# kubectl get nodes -w
