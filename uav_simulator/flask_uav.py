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
import atexit

# Import from inside project
from flask_uav_global_variables import get_args, get_copter_instance, get_logger, get_flask_port
from blueprints.send_cmds_to_uav import send_cmds_to_uav
from blueprints.request_data_from_uav import request_data_from_uav
from flask_uav_functions import send_location_start, interrupt

from flask import Flask
from flask_cors import CORS


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

if (args.uav_sysid == -1) or (args.uav_udp_port == -1):
    print("Bad parameters. Check uav_sysid and uav_udp_port")
    sys.exit(1)

# Register args from this file to the application
get_args(args)

#__license__ = "GPLv3}"

def create_app():
    global app

    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(send_cmds_to_uav)
    app.register_blueprint(request_data_from_uav)

    return app

#----------------------------------------------------------------------

# Util to help logging
logger = get_logger()

flask_port = get_flask_port(str(5000 + int(str(args.uav_udp_port)[-2:])))

print("Running MAIN!!!")
logger.log_info(f'Drone {args.uav_sysid}', f'Starting drone {args.uav_sysid} on {args.uav_ip}:{flask_port}...')
copter = get_copter_instance(args)
logger.log_info(f'Drone {args.uav_sysid}', f'Drone {args.uav_sysid} connected on {args.uav_ip}:{flask_port}.')

# to enable a task for pooling GS with its position
app = create_app()  

# Initiate a Copter instance and send location thread
send_location_start()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)

app.run(host="0.0.0.0", port=flask_port)