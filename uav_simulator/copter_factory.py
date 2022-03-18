from copter import Copter

copter = None

def get_copter_instance(args=None):
    global copter
    if copter is None:
        copter = Copter(sysid=int(args.uav_sysid))
        copter.connect(connection_string=str("udpin:127.0.0.1:" + str(args.uav_udp_port)))
    return copter