# sudo nano 01-docker.sh

# DOWNLOAD & INSTALL DOCKER ENGINE
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# SETUP DOCKER PERMISSIONS FOR LINUX & START THE PROCESS
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl start docker
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

# MAKE SURE DOCKER WORKS
docker version
sudo docker run hello-world

# DOWNLOAD & INSTALL GO-LANG
wget https://go.dev/dl/go1.21.3.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
go version

# DOWNLOAD & INSTALL DOCKER CRI
# NECESSARY FOR KUBERNETES TO USE DOCKER
git clone https://github.com/Mirantis/cri-dockerd.git
cd cri-dockerd
make cri-dockerd
mkdir -p /usr/local/bin
sudo install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd
sudo install packaging/systemd/* /etc/systemd/system
sudo sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service
sudo systemctl daemon-reload
sudo systemctl enable --now cri-docker.socket