import threading
import configparser
import requests

from flask_uav_global_variables import get_args, get_copter_instance, get_logger, get_flask_port

# Lock to control access to variable
data_lock = threading.Lock()

# Thread handler
drone_thread = threading.Thread()

# Simple sequential int to check package loss
seq = 0
SEND_LOCATION_INTERVAL = 1 #Seconds
flask_port = None
copter = None
logger = None

# Reading the config.ini file 
config_from_django = configparser.ConfigParser()
config_from_django.read('../config.ini')


def interrupt():
    global drone_thread
    drone_thread.cancel()

def send_location():
    # Create a POST request with the information of the Copter instance (it needs to be already instantiated)
    # and from the args from flask_uav.py (it needs to be already registred).
    global drone_thread
    global seq
    global config_from_django
    with data_lock:
        global copter
        global flask_port
        global logger
        args = get_args()
        flask_port = get_flask_port()
        copter = get_copter_instance()
        logger = get_logger()

        # The groundstation address this uav will send information 
        path_to_post = config_from_django['post']['ip'] + config_from_django['post']['path_receive_info']
        targetpos = copter.mav.location(relative_alt=True)
        uav_id = int(args.uav_sysid)
        
        # The real time coordinates of the UAV
        json_tmp = {"id": uav_id, "lat": str(targetpos.lat), "lng": str(targetpos.lng), "alt": str(targetpos.alt)}
        # The device type
        json_tmp['device'] = 'uav'
        # The type of message, in this case it represents location info message
        json_tmp['type'] = config_from_django["internal-protocol"]["position_command"] 
        # The sequential number to check package loss
        json_tmp['seq'] = seq
        seq += 1

        if (args.uav_ip is None):
            # In case there wasn't provided the UAV IP, the thread will stop and the instructions will show on terminal. 
            logger.log_info(f'Drone {args.uav_sysid}', f'There wasnt informed the IP from this UAV...\nVerify the command execution inside /uav_simulator/run_uav.py, the following parameter define the UAV IP: --uav_ip IP')
            print('\nNão foi informado o IP desse UAV...\nVerifique a execução do comando em /uav_simulator/run_uav.py:')
            print('--uav_ip http://IP')
            print('\nPressione CTRL+C para encerrar.')
        else:
            # This UAV address, so the GS can register and send specific commands back
            json_tmp['ip'] = str(args.uav_ip) + ':' + flask_port + '/'

            try:
                logger.log_info(f'Drone {args.uav_sysid}', f'Sending POST request with location to the groundstation on {path_to_post}: {json_tmp}')
                r = requests.post(path_to_post, data=json_tmp)
                logger.log_info(f'Drone {args.uav_sysid}', f'Response from the groundstation: {r}')
            except:
                print('Error sending location to groundstation. Logging...')
                logger.log_except()

            # Set the next thread to happen
            drone_thread = threading.Timer(SEND_LOCATION_INTERVAL, send_location, ())
            drone_thread.start()

def send_location_start():
    global drone_thread

    drone_thread = threading.Timer(SEND_LOCATION_INTERVAL, send_location, ())
    drone_thread.start()