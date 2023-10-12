# FIX CENTOS NETWORK SETTINGS
echo "DNS1=8.8.8.8" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3
echo "DNS2=8.8.4.4" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3
echo "ONBOOT=yes" | cat >> /etc/sysconfig/network-scripts/ifcfg-enp0s3

ping www.google.com -c 5

################################################################
################################################################

# INSTALL EDITOR SO WE CAN AVOID USING VIM
sudo yum install -y nano
sudo yum -y install openssh-server openssh-clients

# FIND MACHINES IP ADDRESS
ip addr | grep 192

# ssh IP ADDR
# CHANGE MACHINE