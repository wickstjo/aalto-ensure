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

kubeadm join 192.168.1.231:6443 \
    --token 8csriz.vfpofjzk0bm0pz4m \
    --discovery-token-ca-cert-hash sha256:efb8baf979138b1ccf5ebbf914b522c13ba28aba5ebded364aedb86966f9a66f \
    --cri-socket=unix:///var/run/cri-dockerd.sock

# --cri-socket=unix:///var/run/cri-dockerd.sock


# RENAME THE WORKER NODE ON MASTER
# kubectl get pods -A -w
# kubectl label nodes worker1 kubernetes.io/role=worker
# kubectl get nodes -w
