#!/bin/bash

apt-get update && apt-get upgrade -y && apt-get update --fix-missing

# installing packages and dependencies.
DEBIAN_FRONTEND='noninteractive' apt-get -y install python3-pip git unzip wget

# creating a temporary installation directory
TMP_INSTALL_DIR="/tmp/install_tools"
mkdir -p $TMP_INSTALL_DIR


# installing httpx.
wget https://github.com/projectdiscovery/httpx/releases/download/v1.2.6/httpx_1.2.6_linux_amd64.zip -O $TMP_INSTALL_DIR/httpx.zip
unzip $TMP_INSTALL_DIR/httpx.zip -d $TMP_INSTALL_DIR/httpx
mv $TMP_INSTALL_DIR/httpx/httpx /usr/bin/
chmod +x /usr/bin/httpx

# installing gobuster.
wget https://github.com/OJ/gobuster/releases/download/v3.4.0/gobuster_3.4.0_Linux_x86_64.tar.gz -O $TMP_INSTALL_DIR/gobuster.tar.gz
tar -xzvf $TMP_INSTALL_DIR/gobuster.tar.gz -C $TMP_INSTALL_DIR/
mv $TMP_INSTALL_DIR/gobuster /usr/bin/
chmod +x /usr/bin/gobuster

# installing subfinder.
wget https://github.com/projectdiscovery/subfinder/releases/download/v2.5.5/subfinder_2.5.5_linux_amd64.zip -O $TMP_INSTALL_DIR/subfinder.zip
unzip $TMP_INSTALL_DIR/subfinder.zip -d $TMP_INSTALL_DIR/subfinder
mv $TMP_INSTALL_DIR/subfinder/subfinder /usr/bin/
chmod +x /usr/bin/subfinder

# installing amass.
wget https://github.com/owasp-amass/amass/releases/download/v3.21.2/amass_linux_amd64.zip -O $TMP_INSTALL_DIR/amass.zip
unzip $TMP_INSTALL_DIR/amass.zip -d $TMP_INSTALL_DIR/amass
mv $TMP_INSTALL_DIR/amass/amass_linux_amd64/amass /usr/bin/
chmod +x /usr/bin/amass/

# installing dnsx.
wget https://github.com/projectdiscovery/dnsx/releases/download/v1.1.1/dnsx_1.1.1_linux_amd64.zip -O $TMP_INSTALL_DIR/dnsx.zip
unzip $TMP_INSTALL_DIR/dnsx.zip -d $TMP_INSTALL_DIR/dnsx
mv $TMP_INSTALL_DIR/dnsx/dnsx /usr/bin/
chmod +x /usr/bin/dnsx



# installing Sublist3r.
git clone https://github.com/aboul3la/Sublist3r.git ./etc/github-tools/Sublist3r


pip3 install -r requirements.txt --break-system-packages


printf "\nInstallation Done.\n\n"
