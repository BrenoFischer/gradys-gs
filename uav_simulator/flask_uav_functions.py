import threading
import configparser
import requests

from utils.logger import Logger
from args_manager import get_args
from copter_connection import get_copter_instance

# lock to control access to variable
data_lock = threading.Lock()

# thread handler
drone_thread = threading.Thread()

# simple sequential int to check package loss
seq = 0
flask_port = 0
POOL_TIME = 1 #Seconds
copter = get_copter_instance()

logger = Logger()
# Reading the config.ini file 
config_from_django = configparser.ConfigParser()
config_from_django.read('../config.ini')


def interrupt():
    global drone_thread
    drone_thread.cancel()

def send_location():
    global drone_thread
    global seq
    global config_from_django
    with data_lock:
        #sample print('Safe print regardless race condition...')
        global copter
        global flask_port
        args = get_args()
        print(args)

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
            drone_thread = threading.Timer(POOL_TIME, send_location, ())
            drone_thread.start()

def send_location_start(f_port):
    global drone_thread
    global flask_port

    flask_port = f_port
    drone_thread = threading.Timer(POOL_TIME, send_location, ())
    drone_thread.start()