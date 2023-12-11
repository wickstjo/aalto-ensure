sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock && sudo rm -rf /home/wickstjo/.kube

sudo swapoff -a && sudo systemctl stop firewalld && sudo systemctl disable firewalld
sudo kubeadm join 130.233.193.117:6443 --token tj9hmh.rblvm7kotea0yef7 --discovery-token-ca-cert-hash sha256:af1e2d31b39b3d91a61c2398a1f3583398ae2d17c2962b3620b8e9d5aa311284 --cri-socket=unix:///var/run/cri-dockerd.sock

sudo nano disable_multithreading.sh && sudo chmod +x disable_multithreading.sh

echo 0 | sudo tee /sys/devices/system/cpu/cpu4/online
echo 0 | sudo tee /sys/devices/system/cpu/cpu5/online
echo 0 | sudo tee /sys/devices/system/cpu/cpu6/online
echo 0 | sudo tee /sys/devices/system/cpu/cpu7/online

cat /sys/devices/system/cpu/cpu4/online
cat /sys/devices/system/cpu/cpu5/online
cat /sys/devices/system/cpu/cpu6/online
cat /sys/devices/system/cpu/cpu7/online