#!/bin/bash

set -x

nohup /home/pi/Desktop/Program/str2str -in serial://ttyF9P:115200:8:n:1:off -out tcpsvr://:2103 -out file:///home/pi/Desktop/Program/Binary/ref_anda_%Y%m%d_%h%M%S.ubx &
