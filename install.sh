# INSTALL NECESSARY CERT STUFF
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

# CREATE THE KEYRING DIR IF IT DOESNT EXIT
sudo mkdir -m 755 /etc/apt/keyrings

# ADD PACKAGE REPOS
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# UPDATE APT AND INSTALL KUBE COMPONENTS
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# DISABLE SWAP & FIREWALL
sudo swapoff -a
sudo systemctl stop firewalld
sudo systemctl disable firewalld

# INSTALL DOCKER RUNTIME FOR KUBE

# Note: Docker Engine does not implement the CRI which is a requirement for a container runtime to work with Kubernetes. 
# For that reason, an additional service cri-dockerd has to be installed. cri-dockerd is a project based on the legacy built-in Docker Engine support that was removed from the kubelet in version 1.24.




###########################################################################
###########################################################################



# # INSTALL CNI POD NETWORK PLUGINS
# CNI_PLUGINS_VERSION="v1.3.0"
# ARCH="amd64"
# DEST="/opt/cni/bin"
# sudo mkdir -p "$DEST"
# curl -L "https://github.com/containernetworking/plugins/releases/download/${CNI_PLUGINS_VERSION}/cni-plugins-linux-${ARCH}-${CNI_PLUGINS_VERSION}.tgz" | sudo tar -C "$DEST" -xz

# DOWNLOAD_DIR="/usr/local/bin"
# sudo mkdir -p "$DOWNLOAD_DIR"

# CRICTL_VERSION="v1.28.0"
# ARCH="amd64"
# curl -L "https://github.com/kubernetes-sigs/cri-tools/releases/download/${CRICTL_VERSION}/crictl-${CRICTL_VERSION}-linux-${ARCH}.tar.gz" | sudo tar -C $DOWNLOAD_DIR -xz

