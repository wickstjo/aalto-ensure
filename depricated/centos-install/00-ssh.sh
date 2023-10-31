# IN VIRTUALBOX NETWORK SETTINGS
# CHANGE FROM NAT TO NETWORK BRIDGE

# MAKE SURE THE MACHINE HAS AT LEAST
    # 4096 MB OF MEMORY
    # 4 CPU CORES

# FIX CENTOS NETWORK SETTINGS
echo "DNS1=8.8.8.8" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3
echo "DNS2=8.8.4.4" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3
echo "ONBOOT=yes" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3
sudo reboot

# VERIFY INTERNET ACCESS
ping www.google.com -c 5

sudo yum install -y openssh-server openssh-clients
ip addr

################################################################
################################################################

# INSTALL NECESSARY GENERATIC TOOLS
sudo yum install -y nano git wget curl yum-utils

# FETCH MASTER IP ADDRESS
ip addr | grep 192

# REBOOT TO SAVE SETTINGS
sudo reboot

# ssh IP ADDR
# CHANGE MACHINE