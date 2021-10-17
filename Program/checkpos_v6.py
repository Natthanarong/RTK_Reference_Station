# Base position finding (BSF) >> Define the base position from RTK and PPP Solution

# Set python 3.7 as default >> update-alternatives --install /usr/bin/python python /usr/bin/python3.
# From https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux
# Improve numpy problem https://github.com/numpy/numpy/issues/14772

import glob, re, math, utm
import numpy as np
from haversine import haversine, Unit
import time, os, csv

# Define the RTK and PPP Solution filename
name=['/home/pi/Desktop/Program/Solution/b_rtk.pos','/home/pi/Desktop/Program/Solution/b_ppp.pos','/home/pi/Desktop/Program/Solution/b_single.pos']

# Define the given time 
maxt=240 # 5 minutes

# Define the window size of statistical processing
wins=50 # 50 seconds cumulate 

# Base RTK Monitoring configuration file
conffile='/home/pi/Desktop/Program/b_rtk_mon.conf'
 
# Spec for RTK
rtk_qf=1
rtk_sdenu=0.001
rtk_output=list()
rtk_flag=0
rtk_count=0
rtk_messege=""
ppp_messege=""

# Spec for PPP
ppp_qf=6
ppp_sdenu=0.1
ppp_output=list()
ppp_flag=0
ppp_count=0

# Read each solution
rtk_loop=0
ppp_loop=0

# Read data 
def getdata(name):
    f=open(name,"r")
    log=f.readlines()
    data=[log[i] for i in range(len(log)) if log[i][0]!='%']
    data2=[re.sub(r"\s+", ",", data[i], flags=re.UNICODE).split(',') for i in range(len(data))]
    line=len(data2)
    #read_loop=read_loop+1
    return data2, line

def sod(hms):
    store=hms.split(':')
    sec=float(store[0])*3600+float(store[1])*60+round(store[2],1)
    return sec
  
# Calculate the position innovation
def rtk_process(data,line,sdb,count,output,flag,wins):
    messege=""
    #flag=0
    # If data is not empty >> Check data
    if line!=0:
        # Check Q
        if data[5]=='1':
            print("RTK Fix = ",data[5])
            inp=data #[:-1]
            messege="Fix"
            print("inp [7][8][9]",inp[7],", ",inp[8],", ",inp[9])
            sdenu=round(math.hypot(float(inp[7]),float(inp[8])),3)
            if sdenu <= sdb:
                if count<wins:
                    output.append(inp[2:5])
                    count=count+1
                elif count==wins:
                    flag=1
                print("RTK sdenu<=bound, count = ",count)
            elif sdenu > sdb:
                print("RTK sdenu>bound, count = ",count)
                count=0
                flag=0
                output.clear()
        elif data[5]=='2':
            messege="Float"
            print("RTK Float = ",data[5])
        elif data[5]=='5':
            messege="Single"
            print("RTK Single = ",data[5])
    else:
        messege="No RTK Solution"
    return output,messege,flag,count

def ppp_process(data,line,sdb,count,output,flag,wins):
    messege=""
    #flag=0
    # If data is not empty >> Check data
    if line!=0:
        # Check Q
        if data[5]=='6':
            inp=data #[:-1]
            messege="PPP"
            sdenu=round(math.hypot(float(inp[7]),float(inp[8])),3) # round(math.hypot(float(inp[7]),float(inp[8]),float(inp[9])),3)
            if sdenu <= sdb:
                if count<wins:
                    output.append(inp[2:5])
                    count=count+1
                    print("PPP sdenu<bound, count = ",count)
                elif count==wins:
                    flag=1
            elif sdenu > sdb:
                count=0
                flag=0
                output.clear()
        elif data[5]=='5':
            messege="Single"
    else:
        messege="No PPP Solution"
    return output,messege,flag,count

def calculatepos(inp): # Use position std to decide
    posmat=np.asarray(inp).astype(np.float) # >> float size [Nx3]
    utmset=[utm.from_latlon(posmat[i][0], posmat[i][1]) for i in range(len(posmat))]
    xyset=[[utmset[i][0]-utmset[0][0],utmset[i][1]-utmset[0][1]] for i in range(len(posmat))]
    xyset=np.asarray(xyset).astype(np.float)
    mx,my=np.mean(xyset, axis = 0)
    mh=np.mean(posmat[:,2], axis = 0)
    utmbase=np.array([[utmset[0][0]],[utmset[0][1]]])+np.array([[mx],[my]]).tolist()
    basepos=utm.to_latlon(utmbase[0][0], utmbase[1][0], utmset[0][2],utmset[0][3])
    basepos=[str(round(basepos[0],9)),str(round(basepos[1],9)),str(round(mh,4))]
    return basepos

def warning():
    return

def sendout(data):
    print("create data to send via bluetooth interface")
    return

def writebase(basepos):
    f=open("basepos.txt","w+")
    pos=str(basepos[0])+","+str(basepos[1])+","+str(basepos[2])
    f.write(pos)
    f.close()
    return

def writeNTRIP(basepos):
    f=open(r'/home/pi/Desktop/Program/ntrip.sh','w+') #r'home/pi/Program/ntrip.sh'
    str_sentences="/home/pi/Desktop/Program/str2str -in tcpcli://127.0.0.1:2103#ubx -out tcpsvr://:2109 -out ntrips://:strB1d@27.254.207.85:12101/ANDA:#rtcm3 -msg 1005,1006,1007,1008,1019,1020,1032,1033,1042,1043,1044,1045,1046,1060,1066,1074,1077,1084,1087,1094,1097,1107,1117,1124,1127,1230 -sta 1 -p " 
    basepos_sentence=basepos[0]+" "+basepos[1]+" "+basepos[2]
    f.write(str_sentences+basepos_sentence+" &")
    print("ntrip.sh hase edited done!!")
    f.close()
    return

def runNTRIP():
    os.system("sh /home/pi/Desktop/Program/start.sh > /home/pi/Desktop/Program/sta_binary.log 2>&1")
    os.system("sh /home/pi/Desktop/Program/ntrip.sh > /home/pi/Desktop/stat_ntrip.log 2>&1")
    return

def edit_rtkmon(conffile,basepos):
    # 1. Read configfile to conf
    f=open(conffile,"r")
    conf=f.readlines()
    f.close()
    
    # 2. Read basepos.txt
    f=open(basepos,"r")
    bp=f.readline().split(',')
    f.close()

    # 3. Grep only nmea reqiurement of DOL Base to the config
    gg=conf
    for i in range(len(gg)):
        if gg[i].startswith("inpstr2-nmeareq"):
            gg[i]="inpstr2-nmeareq"+"    =latlon"+" # (0:off,1:latlon,2:single)\n"
        elif gg[i].startswith("inpstr2-nmealat"):
            gg[i]="inpstr2-nmealat"+"    ="+bp[0]+"  # (deg)\n"
        elif gg[i].startswith("inpstr2-nmealon"):
            gg[i]="inpstr2-nmealon"+"    ="+bp[1]+"  # (deg)\n"
        elif gg[i].startswith("inpstr2-nmeahgt"):
            gg[i]="inpstr2-nmeahgt"+"    ="+bp[2]+"  # (m)\n"
    
    # 4. Replace the new config onto b_rtk_mon.conf   
    f=open(conffile,"w+")
    bp=f.writelines(gg)
    f.close()
    return

# Choose the best solution under the given time
t0=time.time()

# Read and store alll data
rtk_data, rtk_line = getdata(name[0])
ppp_data, ppp_line = getdata(name[1])


while (round(time.time())-t0<maxt) and ppp_flag==0 and rtk_flag==0:
    # Read the last linfe data
    """
    rtk_data, rtk_line = getdata(name[0])
    print("RTK Data = ",rtk_data[-1])
    rtk_output,rtk_messege,rtk_flag,rtk_count=rtk_process(rtk_data[-1],rtk_line,rtk_sdenu,rtk_count,rtk_output,rtk_flag)
    print("RTK Count",rtk_count)
    """
    try:
        rtk_data, rtk_line = getdata(name[0])
        print("RTK Data = ",rtk_data[-1])
        rtk_output,rtk_messege,rtk_flag,rtk_count=rtk_process(rtk_data[-1],rtk_line,rtk_sdenu,rtk_count,rtk_output,rtk_flag,wins)
        print("RTK Count",rtk_count)
    except IndexError:
        print("RTK no solution")
    try:
        ppp_data, ppp_line = getdata(name[1])
        print("PPP Data = ",ppp_data[-1])
        ppp_output,ppp_messege,ppp_flag,ppp_count=ppp_process(ppp_data[-1],ppp_line,ppp_sdenu,ppp_count,ppp_output,ppp_flag,wins)    
        print("PPP Count",ppp_count)
    except IndexError:
        print("PPP no solution")
    print("Processes are running")    
    print("Time to wait :",round(maxt-(time.time()-t0),1),"Seconds.")
    time.sleep(1)

if ppp_flag!=1 and rtk_flag!=1:
# find all position that which have Q=1.
    print("No fix soultion or PPP converge, Please reconfigure RTKRTCV")
    # Do calculate the initial pos from single solution
    single_output,single_line=getdata(name[-1])
    inp=[single_output[i][2:5] for i in range(single_line)]
    basepos=calculatepos(inp)
elif ppp_flag==1:
    basepos=calculatepos(ppp_output)
    print("PPP Base pos = ",basepos)
elif rtk_flag==1:
    basepos=calculatepos(rtk_output)
    print("RTK Base pos = ",basepos)
# Choose the best condition and edit run ntrip config at the rtcm position     

#os.system("sudo killall -9 rtkrcv")
os.popen("sudo killall -9 rtkrcv")
os.popen("sudo killall -9 str2str")

# Choose the best condition and edit run ntrip config at the rtcm position    
writebase(basepos) 
writeNTRIP(basepos)

time.sleep(2)
# Run ntrip.sh to dtream data into Anunda's Server
os.popen("sh /home/pi/Desktop/Program/start.sh > /home/pi/Desktop/Program/sta_binary.log 2>&1 &")
time.sleep(5)
os.popen("sh /home/pi/Desktop/Program/ntrip.sh > /home/pi/Desktop/Program/sta_ntrip.log 2>&1 &")

# Edit b_rtk_mon.conf
#edit_rtkmon("/home/pi/Desktop/Program/b_rtk_mon.conf","/home/pi/Desktop/Program/basepos.txt")

# Run ntrip_monitor.sh to monitor the base station status
#os.popen("sh /home/pi/Desktop/Program/ntrip_monitor.sh > /home/pi/Desktop/Program/sta_ntripmon.log 2>&1 &")

#print("Now, Base station is streaming data to Anunda's NTRIP!!")
#os.popen("nohup /home/pi/Program/ntrip.sh > /home/pi/Program/sta_ntrip.sh 2>&1 &")
