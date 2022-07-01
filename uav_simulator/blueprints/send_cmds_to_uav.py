import os

from pymavlink import mavutil
from flask import Blueprint, render_template, current_app, request, make_response
from werkzeug.utils import secure_filename

from flask_uav_global_variables import get_copter_instance, get_args, get_logger

send_cmds_to_uav = Blueprint("send_cmds_to_uav", __name__, template_folder="../templates")

@send_cmds_to_uav.route('/')
def hello_world():
    return render_template('return.html', name='Hello, World! (index page)')


@send_cmds_to_uav.route('/hello/')
@send_cmds_to_uav.route('/hello/<name>')
def hello(name=None):
    return render_template('return.html', name=name) 


@send_cmds_to_uav.route('/connect')
def flask_connect():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()
    # Assume that we are connecting to SITL on udp 14550
    logger.log_info(f'Drone {args.uav_sysid}', f'Route /connect reached from drone {args.uav_sysid}')
    logger.log_info(f'Drone {args.uav_sysid}', f"Trying to connect with connection string: {str(args['master']['connection_string'])}")
    copter.connect(connection_string=str(args['master']['connection_string']))
    logger.log_info(f'Drone {args.uav_sysid}', f"Connected with connection string: {str(args['master']['connection_string'])}")
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /connect route')
    return render_template('return.html', name='connected')


@send_cmds_to_uav.route('/arm')
def flask_arm():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /arm reached from drone {args.uav_sysid}')
    copter.change_mode("GUIDED")
    copter.wait_ready_to_arm()

    if not copter.armed():
        logger.log_info(f'Drone {args.uav_sysid}', f'Copter not armed prepared to arm')
        copter.arm_vehicle()
    if copter.armed():
        logger.log_info(f'Drone {args.uav_sysid}', f'Copter armed')
        logger.log_info(f'Drone {args.uav_sysid}', f'End of /arm route')
        return render_template('return.html', name='Vehicle armed')    
    else:
        logger.log_info(f'Drone {args.uav_sysid}', f'Copter not armed')
        logger.log_info(f'Drone {args.uav_sysid}', f'End of /arm route')
        return render_template('return.html', name='Vehicle ARMED armed') 


@send_cmds_to_uav.route('/takeoff')
@send_cmds_to_uav.route('/takeoff/<altitute>')
def flask_takeoff(altitute=10):
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /takeoff reached from drone {args.uav_sysid}')
    logger.log_info(f'Drone {args.uav_sysid}', f'Taking off with altitude {altitude}')
    copter.user_takeoff(int(altitute))
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /takeoff route')
    return render_template('return.html', name='Ordered to takeoff to ' + str(altitute))


@send_cmds_to_uav.route('/rtl')
def flask_rtl():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()
    
    logger.log_info(f'Drone {args.uav_sysid}', f'Route /rtl reached from drone {args.uav_sysid}')
    logger.log_info(f'Drone {args.uav_sysid}', f'Ordering to takeoff to RTL')
    copter.do_RTL()
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /rtl route')
    return render_template('return.html', name='Ordered to takeoff to RTL') 


@send_cmds_to_uav.route('/upload_file', methods=['GET', 'POST'])
def flask_upload_file():
    UPLOAD_FOLDER = './uploads'
    logger = get_logger()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /upload_file reached from drone {args.uav_sysid}')

    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    logger.log_info(f'Drone {args.uav_sysid}', f'Starting uploading file')
    if request.method == 'POST':
        if 'file' not in request.files:
            logger.log_info(f'Drone {args.uav_sysid}', f'Something went wrong with the request, his is not a file request')
            print('Not a file request')
            return ''
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            logger.log_info(f'Drone {args.uav_sysid}', f'Something went wrong, there was no file selected')
            print('No selected file')
            return render_template('return.html', name='No file selected')

        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        logger.log_info(f'Drone {args.uav_sysid}', f'File uploaded on {UPLOAD_FOLDER + filename}')
        logger.log_info(f'Drone {args.uav_sysid}', f'End of /upload_file route')
    return render_template('return.html', name='File uploaded')


@send_cmds_to_uav.route('/sample')
def flask_sample():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /sample reached from drone {args.uav_sysid}')
    print("Let's wait ready to arm")
    logger.log_info(f'Drone {args.uav_sysid}', f'Waiting that drone can pass all arming check')
    # We wait that can pass all arming check
    copter.wait_ready_to_arm()

    print("Let's create and write a mission")
    logger.log_info(f'Drone {args.uav_sysid}', f'Creating and writing a mission')
    # We will write manually a mission by defining some waypoint
    # We start by initialising mavwp helper library
    copter.init_wp()
    # We get the home position to serve as reference for the mission and as waypoint 0.
    logger.log_info(f'Drone {args.uav_sysid}', f'Getting home position to serve as starting reference')
    last_home = copter.home_position_as_mav_location()
    # On Copter, we need a takeoff ... for takeoff !
    logger.log_info(f'Drone {args.uav_sysid}', f'Adding waypoints to the mission')
    copter.add_wp_takeoff(last_home.lat, last_home.lng, 10)
    copter.add_waypoint(last_home.lat + 0.005, last_home.lng + 0.005, 20)
    copter.add_waypoint(last_home.lat - 0.005, last_home.lng + 0.005, 30)
    copter.add_waypoint(last_home.lat - 0.005, last_home.lng - 0.005, 20)
    copter.add_waypoint(last_home.lat + 0.005, last_home.lng - 0.005, 15)
    # We add a RTL at the end.
    logger.log_info(f'Drone {args.uav_sysid}', f'Adding RTL at the end')
    copter.add_wp_rtl()
    # We send everything to the drone
    logger.log_info(f'Drone {args.uav_sysid}', f'Send everything to drone')
    copter.send_all_waypoints()

    print("Let's get the mission written")
    # We get the number of mission waypoint in the drone and print the mission
    logger.log_info(f'Drone {args.uav_sysid}', f'Sending the mission to drone')
    wp_count = copter.get_all_waypoints()

    print("Let's execute the mission")
    # On ArduPilot, with copter < 4.1 we need to arm before going into Auto mode.
    # We use GUIDED mode as the requirement are closed to AUTO one's
    logger.log_info(f'Drone {args.uav_sysid}', f'Changing mode to GUIDED')
    copter.change_mode("GUIDED")
    # We wait that can pass all arming check
    logger.log_info(f'Drone {args.uav_sysid}', f'Waiting to pass all arming check')
    copter.wait_ready_to_arm()
    copter.arm_vehicle()
    # When armed, we change mode to AUTO
    logger.log_info(f'Drone {args.uav_sysid}', f'Changing mode to AUTO')
    copter.change_mode("AUTO")
    # As we don't have RC radio here, we trigger mission start with MAVLink.
    logger.log_info(f'Drone {args.uav_sysid}', f'Triggering mission with MAVLink')
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
    logger.log_info(f'Drone {args.uav_sysid}', f'Tracking mission progression...')
    copter.wait_waypoint(0, wp_count - 1, timeout=500)
    copter.wait_landed_and_disarmed(min_alt=2)
    logger.log_info(f'Drone {args.uav_sysid}', f'Mission completed and drone landed and disarmed')
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /sample route')
    return render_template('return.html', name='Ordered to do a full auto mission.')  


@send_cmds_to_uav.route('/spiral')
def flask_spiral():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /spiral reached from drone {args.uav_sysid}')
    print("Let's wait ready to arm")
    # We wait that can pass all arming check
    logger.log_info(f'Drone {args.uav_sysid}', f'Waiting that drone can pass all arming check')
    copter.wait_ready_to_arm()

    print("Let's create and write a mission")
    # We will write manually a mission by defining some waypoint
    # We start by initialising mavwp helper library
    copter.init_wp()
    # We get the home position to serve as reference for the mission and as waypoint 0.
    last_home = copter.home_position_as_mav_location()
    # On Copter, we need a takeoff ... for takeoff !
    logger.log_info(f'Drone {args.uav_sysid}', f'Adding waypoints to the mission')
    copter.add_wp_takeoff(last_home.lat, last_home.lng, 10)
    copter.add_waypoint(-15.84034160, -47.92689090, 15.000000)
    copter.add_waypoint(-15.84027450, -47.92749170, 20.000000)
    copter.add_waypoint(-15.83987200, -47.92759900, 25.000000)
    copter.add_waypoint(-15.83977910, -47.92700890, 30.000000)
    copter.add_waypoint(-15.84028680, -47.92690830, 35.000000)
    copter.add_waypoint(-15.84023450, -47.92746620, 40.000000)
    copter.add_waypoint(-15.83990040, -47.92755200, 45.000000)
    copter.add_waypoint(-15.83982170, -47.92705180, 50.000000)
    copter.add_waypoint(-15.84021650, -47.92697400, 55.000000)
    copter.add_waypoint(-15.84016870, -47.92741920, 60.000000)
    copter.add_waypoint(-15.83992880, -47.92749030, 50.000000)
    copter.add_waypoint(-15.83987720, -47.92710010, 40.000000)
    copter.add_waypoint(-15.84014290, -47.92704370, 50.000000)
    copter.add_waypoint(-15.84013260, -47.92738440, 40.000000)
    copter.add_waypoint(-15.83996750, -47.92742330, 30.000000)
    copter.add_waypoint(-15.83993780, -47.92714830, 20.000000)
    copter.add_waypoint(-15.84010040, -47.92711480, 20.000000)
    # We add a RTL at the end.
    logger.log_info(f'Drone {args.uav_sysid}', f'Adding RTL at the end')
    copter.add_wp_rtl()
    # We send everything to the drone
    copter.send_all_waypoints()

    print("Let's get the mission written")
    # We get the number of mission waypoint in the drone and print the mission
    logger.log_info(f'Drone {args.uav_sysid}', f'Sending the mission to drone')
    wp_count = copter.get_all_waypoints()

    print("Let's execute the mission")
    # On ArduPilot, with copter < 4.1 we need to arm before going into Auto mode.
    # We use GUIDED mode as the requirement are closed to AUTO one's
    logger.log_info(f'Drone {args.uav_sysid}', f'Changing mode to GUIDED')
    copter.change_mode("GUIDED")
    # We wait that can pass all arming check
    logger.log_info(f'Drone {args.uav_sysid}', f'Waiting to pass all arming check')
    copter.wait_ready_to_arm()
    copter.arm_vehicle()
    # When armed, we change mode to AUTO
    logger.log_info(f'Drone {args.uav_sysid}', f'Changing mode to AUTO')
    copter.change_mode("AUTO")
    # As we don't have RC radio here, we trigger mission start with MAVLink.
    logger.log_info(f'Drone {args.uav_sysid}', f'Triggering mission with MAVLink')
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
    logger.log_info(f'Drone {args.uav_sysid}', f'Tracking mission progression...')
    copter.wait_waypoint(0, wp_count - 1, timeout=500)
    copter.wait_landed_and_disarmed(min_alt=2)
    logger.log_info(f'Drone {args.uav_sysid}', f'Mission completed and drone landed and disarmed')
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /spiral route')

    return render_template('return.html', name='Ordered to do a full auto mission.')
