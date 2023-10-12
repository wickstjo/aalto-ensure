# FIX CENTOS NETWORK SETTINGS
echo "DNS1=8.8.8.8" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3
echo "DNS2=8.8.4.4" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3
echo "ONBOOT=yes" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3

# REBOOT

################################################################
################################################################

# INSTALL EDITOR SO WE CAN AVOID USING VIM
sudo yum install -y nano
sudo yum -y install openssh-server openssh-clients

# FIND MACHINES IP ADDRESS
ip addr | grep 192

# ssh IP ADDR
# CHANGE MACHINE

################################################################
################################################################

# INSTALL PACKAGE MANAGER UTILS
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# INSTALL DOCKER
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# SETUP DOCKER PERMISSIONS FOR LINUX & START THE PROCESS
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl start docker
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

################################################################
################################################################

# This overwrites any existing configuration in /etc/yum.repos.d/kubernetes.repo
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

# INSTALL KUBERNETES & START THE PROCESS
sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
sudo systemctl enable --now kubelet