import os

from pymavlink import mavutil
from flask import Blueprint, render_template, current_app, request, make_response
from werkzeug.utils import secure_filename

from copter_connection import get_copter_instance
from args_manager import get_args

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
    copter = get_copter_instance()
    args = get_args()
    # Assume that we are connecting to SITL on udp 14550
    copter.connect(connection_string=str(args['master']['connection_string']))
    return render_template('return.html', name='connected')


@send_cmds_to_uav.route('/arm')
def flask_arm():
    copter = get_copter_instance()
    copter.change_mode("GUIDED")
    copter.wait_ready_to_arm()

    if not copter.armed():
        copter.arm_vehicle()
    if copter.armed():
        return render_template('return.html', name='Vehicle armed')    
    else:
        return render_template('return.html', name='Vehicle ARMED armed') 


@send_cmds_to_uav.route('/takeoff')
@send_cmds_to_uav.route('/takeoff/<altitute>')
def flask_takeoff(altitute=10):
    copter = get_copter_instance()
    copter.user_takeoff(int(altitute))
    return render_template('return.html', name='Ordered to takeoff to ' + str(altitute))


@send_cmds_to_uav.route('/rtl')
def flask_rtl():
    copter = get_copter_instance()
    copter.do_RTL()
    return render_template('return.html', name='Ordered to takeoff to RTL') 


@send_cmds_to_uav.route('/upload_file', methods=['GET', 'POST'])
def flask_upload_file():
    UPLOAD_FOLDER = './uploads'
    
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if request.method == 'POST':
        if 'file' not in request.files:
            print('Not a file request')
            return ''
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return render_template('return.html', name='No file selected')

        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return render_template('return.html', name='File uploaded')


@send_cmds_to_uav.route('/sample')
def flask_sample():
    copter = get_copter_instance()
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


@send_cmds_to_uav.route('/spiral')
def flask_spiral():
    copter = get_copter_instance()
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
