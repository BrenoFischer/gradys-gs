
UAV simulator for tests with the Ground Station - PRE-ALFA VERSION!

pre-reqs:

1) Clone Ardupilot repository
2) Make sure that SITL is running well
3) Only tested in Ubuntu 20.04 LTS on WSL2

Randy to debug: Mission planner accepting UDP connections on UDP 55555

----------------------------------------------------------------------------------

Drafts:

1) Setup:
mkdir ~/.config/ardupilot
echo "AbraDF=-15.840081,-47.926642,1042,30" >> ~/.config/ardupilot/locations.txt

2) Running:

runnning-UAV:
xterm -e ../../sitl_sim/Tools/autotest/sim_vehicle.py -v ArduCopter -I 21 --sysid 21 -N --out 192.168.0.50:55555 --speedup 1 -L AbraDF --out 127.0.0.1:17171 & 

runnning-Flask API:
python3 flask_uav.py --uav_sysid 21 --uav_udp_port 17171

3) Stopping:
terminator.sh

----------------------------------------------------------------------------------

General notes:

1) "-I 21 --sysid 21": in the SITL creates the instance with the same "--uav_sysid" to bind the controller (flask_uav.py) and the uav (SITL)

2) "--out 127.0.0.1:17171": in the SITL creates the instance with the same "--uav_udp_port" to bind the controller (flask_uav.py) and the uav (SITL)

3) "-N": do not compile again

4) "--out 192.168.0.50:55555": The IP is for the Mission Planner machine and the port for the UDP connection.



