from copter import Copter
from utils.logger import Logger

args = None
copter = None
logger = None
flask_port = None

def get_args(content=None):
    global args
    if args is None:
        args = content
    return args
     

def get_copter_instance(args=None):
    global copter
    if copter is None:
        copter = Copter(sysid=int(args.uav_sysid))
        copter.connect(connection_string=str("udpin:127.0.0.1:" + str(args.uav_udp_port)))
    return copter


def get_logger():
    global logger
    if logger is None:
        logger = Logger()
    return logger


def get_flask_port(content=None):
    global flask_port
    if flask_port is None:
        flask_port = content
    return flask_port