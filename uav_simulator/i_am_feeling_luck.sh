#!/bin/bash


echo Running a UAV....
xterm -e ../../sitl_sim/Tools/autotest/sim_vehicle.py -v ArduCopter -I 21 --sysid 21 -N --out 192.168.0.50:55555 --speedup 1 -L AbraDF --out 127.0.0.1:17171 & 
sleep 1s


echo Running a UAV controller...
python3 flask_uav.py --uav_sysid 21 --uav_udp_port 17171 & 
sleep 1s



echo Sending a commando for the UAV...
sleep 5s
wget http://127.0.0.1:5071/auto




echo Press any key to terminate everything....
read varname

./terminator.sh