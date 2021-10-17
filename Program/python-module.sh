#!/bin/bash
set -x
sudo apt-get install -y ntpdate &&
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1 &&
sudo apt install -y matchbox-keyboard &&
pip3 install utm 
pip3 install haversine 
pip3 install nvector 
pip3 install matplotlib 
pip3 install pigpio 
pip3 install numpy 
pip3 install paho-mqtt 
pip3 install mysql-connector-python 
pip3 install playsound 
pip3 install csv 
pip3 install pillow
sudo apt-get install -y mariadb-server