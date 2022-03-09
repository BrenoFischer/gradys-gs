import os
import socket
import time

import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

delay = 0.5

# Make setup DISPLAY runable here


# Run xterm (quantity of xterm/uavs obtained in .ini)
uav_qt = int(config['uav-simulator']['uav_quantity'])
for i in range(uav_qt):
    cmd_line = f'xterm -e ~/ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter -I 2{i+1} --sysid 2{i+1} -N --speedup 5 -L AbraDF --out 127.0.0.1:1717{i+1} &'
    os.system(cmd_line)
    time.sleep(0.5)


# Get uav ip with ifconfig (inet) and insert on the param inide the command to run flask_uav
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("8.8.8.8", 80))
# ip = s.getsockname()[0]

# Run uav flask servers 
# for i in range(uav_qt):
#     cmd_line = f'python3 flask_uav.py --uav_sysid 2{i+1} --uav_udp_port 1717{i+1} --uav_ip http://{ip}'
#     os.system(cmd_line)
#     time.sleep(0.5)


# Atrelar com flask_uav