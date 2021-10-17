#!/bin/bash

set -x

sudo killall -9 str2str

nohup /home/pi/Desktop/Program/str2str -in serial://ttyF9P:115200:8:n:1:off#ubx -out tcpsvr://:2101 -out tcpsvr://:2102 -out tcpsvr://:2103 &

# serial://ttyF9P:115200:8:n:1:off

#Wait for str2str already run
sleep 5

# Run RTK and PPP process
rm -rf /home/pi/Desktop/Program/Solution/*.pos 
nohup /home/pi/Desktop/Program/rtkrcv -s -o b_rtk.conf > rtk.log 2>&1 &
nohup /home/pi/Desktop/Program/rtkrcv -s -o b_ppp.conf > ppp.log 2>&1 &
nohup /home/pi/Desktop/Program/rtkrcv -s -o b_single.conf > single.log 2>&1 &

sleep 3
nohup python /home/pi/Desktop/Program/checkpos_v6.py > process.log 2>&1 &

#nohup sh /home/pi/Program/ntrip.sh > sta_ntrip.log 2>&1 &
