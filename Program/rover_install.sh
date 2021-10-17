#!/bin/bash
set -x # Show all outputs in this script

# Upgrade and Update Raspberry Pi
sudo apt-get -y update &&
sudo apt-get -y upgrade &&

# Install GIT
sudo apt-get -y install git &&

# Install Basic Module to buils RTKLIB
sudo apt-get -y install build-essential &&
sudo apt-get -y install automake &&
sudo apt-get -y install checkinstall &&

# Download RTKLIB
git clone https://github.com/rtklibexplorer/RTKLIB.git

sleep 3
# Let's make RTKLIB
cd /home/pi/Desktop/RTKLIB/app/consapp/
sudo make

# Make Program Folder
cd /home/pi/Desktop
mkdir Program
# Copy rtkrcv, str2str and data from RTKLIB

# RTKRCV
cp /home/pi/Desktop/RTKLIB/app/consapp/rtkrcv/gcc/rtkrcv /home/pi/Desktop/Program/
cp /home/pi/Desktop/RTKLIB/app/consapp/rtkrcv/gcc/rtkstart.sh /home/pi/Desktop/Program/
cp /home/pi/Desktop/RTKLIB/app/consapp/rtkrcv/gcc/rtkshut.sh /home/pi/Desktop/Program/

# STR2STR
#cp /home/pi/Desktop/RTKLIB/app/consapp/str2str/gcc/str2str /home/pi/Desktop/Program/

# Copy cmd file into Program
cp /home/pi/Desktop/RTKLIB/data/cmd/ubx_m8t_*.cmd /home/pi/Desktop/Program/

# Change the permission
sudo chmod 755 /home/pi/Desktop/Program/*.sh
sudo chmod 755 /home/pi/Desktop/Program/rtkrcv
#sudo chmod 755 /home/pi/Desktop/Program/str2str

# Install Bluetooth Package
sudo apt-get install bluez libopenobex1 obexftp obexpushd --yes

