#!/usr/bin/env python

"""
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
    Pymavlink example usage with ArduPilot Copter SITL.
    This expect that the SITL is launch with default parameters.
    You can launch SITL from ArduPilot directory with :
    sim_vehicle.py -v ArduCopter -w --console --map
    Then from pymavlink/examples directory, launch this script :
    python mavexample.py

    The script will example :
    - how to connect to the drone
    - Wait for the drone to be ready
    - Change some incomming message rate
    - Get and change parameters
    - Create and upload an auto mission
    - Get back the mission in the drone
    - Run and monitor an auto mission
    - Make a takeoff in Guided mode
    - Wait some target altitude
    - Send some Position target in Guided mode
    - Monitor the drone position
    - Trigger a RTL and monitor the progress

    Those are heavily based on the work done on ArduPilot Autotest framework : https://ardupilot.org/dev/docs/the-ardupilot-autotest-framework.html
"""

import sys
import argparse


from pymavlink import mavutil

import configparser
import threading
import atexit
import requests

# Import from inside project
from utils.logger import Logger
from copter import Copter


from flask import Flask
from flask import render_template
from flask import jsonify #returns a json from a dict
from flask import json
#app = Flask(__name__)

#######

# Global Stuff
copter = 0


# arguments
parser = argparse.ArgumentParser(
    description='Copy Common Files as needed, stripping out non-relevant wiki content',  
)
parser.add_argument(
    '--uav_sysid',
    dest='uav_sysid',
    default=-1,
    help="Value for uav SYSID to connect through mavlink",  
)
parser.add_argument(
    '--uav_udp_port',
    dest='uav_udp_port',
    default=-1,
    help="Value for uav UAV on localhost",  
)
parser.add_argument(
    '--uav_ip',
    dest='uav_ip',
    help="IP to run the flask server",  
)

args = parser.parse_args()

__license__ = "GPLv3}"

##########################

#----------------------------------------------------------------------
# Threading for flask 
#
POOL_TIME = 1 #Seconds

# variables that are accessible from anywhere
#commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
yourThread = threading.Thread()
# simple sequential int to check package loss
seq = 0

def create_app():
    global app
    app = Flask(__name__)


    ##########################################################################
    # Flask drone API

    @app.route('/')
    def hello_world():
        return render_template('return.html', name='Hello, World! (index page)')    


    @app.route('/hello/')
    @app.route('/hello/<name>')
    def hello(name=None):
        return render_template('return.html', name=name)    

    @app.route('/connect')
    def flask_connect():
        global copter
        copter = Copter(sysid=int(config['master']['sysid']))
        # Assume that we are connecting to SITL on udp 14550
        copter.connect(connection_string=str(config['master']['connection_string']))
        return render_template('return.html', name='connected')  

    @app.route('/arm')
    def flask_arm():
        global copter
        copter.change_mode("GUIDED")
        copter.wait_ready_to_arm()

        if not copter.armed():
            copter.arm_vehicle()
        if copter.armed():
            return render_template('return.html', name='Vehicle armed')    
        else:
            return render_template('return.html', name='Vehicle ARMED armed')    

    @app.route('/takeoff')
    @app.route('/takeoff/<altitute>')
    def flask_takeoff(altitute=10):
        global copter
        copter.user_takeoff(int(altitute))
        return render_template('return.html', name='Ordered to takeoff to ' + str(altitute))    


    @app.route('/rtl')
    def flask_rtl():
        global copter
        copter.do_RTL()
        return render_template('return.html', name='Ordered to takeoff to RTL')    

    @app.route('/auto')
    def flask_auto():
        # Mudar para sample
        # Criar uma nova /auto
        # Criar uma nova /experiment
        global copter
        print("Let's wait ready to arm")
        # We wait that can pass all arming check
        copter.wait_ready_to_arm()

        print("Let's create and write a mission")
        # We will write manually a mission by defining some waypoint
        # We start by initialising mavwp helper library
        copter.init_wp()
        # We get the home position to serve as reference for the mission and as waypoint 0.
        last_home = copter.home_position_as_mav_location()
        # On Copter, we need a takeoff ... for takeoff !
        copter.add_wp_takeoff(last_home.lat, last_home.lng, 10)
        copter.add_waypoint(last_home.lat + 0.005, last_home.lng + 0.005, 20)
        copter.add_waypoint(last_home.lat - 0.005, last_home.lng + 0.005, 30)
        copter.add_waypoint(last_home.lat - 0.005, last_home.lng - 0.005, 20)
        copter.add_waypoint(last_home.lat + 0.005, last_home.lng - 0.005, 15)
        # We add a RTL at the end.
        copter.add_wp_rtl()
        # We send everything to the drone
        copter.send_all_waypoints()

        print("Let's get the mission written")
        # We get the number of mission waypoint in the drone and print the mission
        wp_count = copter.get_all_waypoints()

        print("Let's execute the mission")
        # On ArduPilot, with copter < 4.1 we need to arm before going into Auto mode.
        # We use GUIDED mode as the requirement are closed to AUTO one's
        copter.change_mode("GUIDED")
        # We wait that can pass all arming check
        copter.wait_ready_to_arm()
        copter.arm_vehicle()
        # When armed, we change mode to AUTO
        copter.change_mode("AUTO")
        # As we don't have RC radio here, we trigger mission start with MAVLink.
        copter.send_cmd(mavutil.mavlink.MAV_CMD_MISSION_START,
                        1,  # ARM
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                        target_sysid=copter.target_system,
                        target_compid=copter.target_system,
                        )
        # We use the convenient function to track the mission progression
        copter.wait_waypoint(0, wp_count - 1, timeout=500)
        copter.wait_landed_and_disarmed(min_alt=2)

        return render_template('return.html', name='Ordered to do a full auto mission.')    

    @app.route('/position')
    def flask_position():
        global copter
        targetpos = copter.mav.location(relative_alt=True)
        json_tmp = '{"id": ' + str(args.uav_sysid) + ', "lat":' + str(targetpos.lat) + ', "lng": ' + str(targetpos.lng) + ', "high": ' + str(targetpos.alt) + '}'
        return render_template('return.html', name=json_tmp)    


    @app.route('/position_relative_json')
    def flask_position_json():
        global copter
        targetpos = copter.mav.location(relative_alt=True)
        json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'
        #return json.dumps(json_tmp)
        #print(json_tmp)
        #print(json
        return json_tmp


    @app.route('/position_absolute_json')
    def flask_position_relative_json():
        global copter
        targetpos = copter.mav.location(relative_alt=False)
        json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'
        #return json.dumps(json_tmp)
        print(json_tmp)
        #print(json
        return json_tmp
    ##########################################################################


    def interrupt():
        global yourThread
        yourThread.cancel()

    def sendLocation():
        global yourThread
        global seq
        global config_from_django
        with dataLock:
            #sample print('Safe print regardless race condition...')
            global copter

            # The groundstation address this uav will send information 
            path_to_post = config_from_django['post']['ip'] + config_from_django['post']['path_receive_info']
            targetpos = copter.mav.location(relative_alt=True)
            uav_id = int(args.uav_sysid)
            
            # The real time coordinates of the UAV
            json_tmp = {"id": uav_id, "lat": str(targetpos.lat), "lng": str(targetpos.lng), "alt": str(targetpos.alt)}
            # The device type
            json_tmp['device'] = 'uav'
            # The type of message, in this case it represents location info message
            json_tmp['type'] = config_from_django["internal-protocol"]["location_command"] 
            # The sequential number to check package loss
            json_tmp['seq'] = seq
            seq += 1

            if (args.uav_ip is None):
                # In case there wasn't provided the UAV IP, the thread will stop and the instructions will show on terminal. 
                print('\nNão foi informado o IP desse UAV...\nVerifique a execução do comando em /uav_simulator/run_uav.py:')
                print('--uav_ip http://IP')
                print('\nPressione CTRL+C para encerrar.')
            else:
                # This UAV address, so the GS can register and send specific commands back
                json_tmp['ip'] = str(args.uav_ip) + ':' + flask_port + '/'

                try:
                    r = requests.post(path_to_post, data=json_tmp)
                    print(r.status_code, r.reason)
                    logger.log_info(r, f'uav-sim{uav_id}')
                except:
                    print('Erro ao enviar a informação. Logging...')
                    logger.log_except()

                # Set the next thread to happen
                yourThread = threading.Timer(POOL_TIME, sendLocation, ())
                yourThread.start()


    def sendLocationStart():
        # Do initialisation stuff here
        print('Creating intermediary scheduler...')
        global yourThread
        # Create your thread
        yourThread = threading.Timer(POOL_TIME, sendLocation, ())
        yourThread.start()

    # Initiate
    sendLocationStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app

#----------------------------------------------------------------------

#if __name__ == '__main__':

if (args.uav_sysid == -1) or (args.uav_udp_port == -1):
    print("Bad parameters. Check uav_sysid and uav_udp_port")
    sys.exit(1)

logger = Logger()
# Reading the config file 
config_from_django = configparser.ConfigParser()
config_from_django.read('../config.ini')

print("Running MAIN!!!")
copter = Copter(sysid=int(args.uav_sysid))
copter.connect(connection_string=str("udpin:127.0.0.1:" + str(args.uav_udp_port)))


# to enable a task for pooling GS with its position
app = create_app()  

# run flask for any client and use port from parameters
flask_port = str(5000 + int(str(args.uav_udp_port)[-2:]))
app.run(host="0.0.0.0", port=flask_port)