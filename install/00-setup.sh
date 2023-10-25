# BASELINE
sudo apt-get install -y openssh-server openssh-clients
sudo apt-get install -y nano git wget curl make
ip addr | grep 192

# CONNECT VIA SSH, THEN CHANGE THE HOSTNAME -- baseline_machine
sudo nano /etc/hostname && sudo nano /etc/hosts
sudo reboot