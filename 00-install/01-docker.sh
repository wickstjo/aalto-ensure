# DOWNLOAD & INSTALL DOCKER
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh test-docker.sh

# SETUP DOCKER PERMISSIONS FOR LINUX & START THE PROCESS
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

echo -e "\n#####################################\n"

# MAKE SURE DOCKER WORKS
docker version
sudo docker run hello-world