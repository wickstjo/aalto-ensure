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