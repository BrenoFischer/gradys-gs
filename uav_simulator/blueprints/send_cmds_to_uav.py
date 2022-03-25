import os

from pymavlink import mavutil
from flask import Blueprint, render_template, current_app, request
from werkzeug.utils import secure_filename

from copter_connection import get_copter_instance

send_cmds_to_uav = Blueprint("send_cmds_to_uav", __name__, template_folder="../templates")

@send_cmds_to_uav.route('/upload_file', methods=['GET', 'POST'])
def flask_upload_file():
    UPLOAD_FOLDER = '/uav_simulator/uploads'
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    print('HEREEEEEEE')

    if request.method == 'POST':
        if 'file' not in request.files:
            print('Not a file request')
            return render_template('return.html', name='Not file request')
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
