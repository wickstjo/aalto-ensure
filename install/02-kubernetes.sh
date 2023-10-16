# sudo nano 02-kubernetes.sh
# sudo chmod +x 02-kubernetes.sh

# OVERWRITE KUBE CONFIG FILE
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.28/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

# INSTALL KUBE COMPONENTS & START KUBELET 
sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
sudo systemctl enable --now kubelet

echo "###############################################################################"
echo ""
echo ""

# CHECK THAT EVERYTHING IS OK
kubelet --version
kubeadm version
kubectl version

echo ""
echo ""
echo "###############################################################################"

##############################################################################################################
##############################################################################################################

# # CONFIGURE KUBERNETES NETWORK THING
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

# RELEASE="$(curl -sSL https://dl.k8s.io/release/stable.txt)"
# ARCH="amd64"
# cd $DOWNLOAD_DIR
# sudo curl -L --remote-name-all https://dl.k8s.io/release/${RELEASE}/bin/linux/${ARCH}/{kubeadm,kubelet}
# sudo chmod +x {kubeadm,kubelet}

# RELEASE_VERSION="v0.16.2"
# curl -sSL "https://raw.githubusercontent.com/kubernetes/release/${RELEASE_VERSION}/cmd/krel/templates/latest/kubelet/kubelet.service" | sed "s:/usr/bin:${DOWNLOAD_DIR}:g" | sudo tee /etc/systemd/system/kubelet.service
# sudo mkdir -p /etc/systemd/system/kubelet.service.d
# curl -sSL "https://raw.githubusercontent.com/kubernetes/release/${RELEASE_VERSION}/cmd/krel/templates/latest/kubeadm/10-kubeadm.conf" | sed "s:/usr/bin:${DOWNLOAD_DIR}:g" | sudo tee /etc/systemd/system/kubelet.service.d/10-kubeadm.conf

# START THE KUBELET PROCESS
# systemctl enable --now kubelet