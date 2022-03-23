from pymavlink import mavutil
from flask import Blueprint, render_template

from copter_connection import get_copter_instance

experiments_blueprint = Blueprint("experiments_blueprint", __name__, template_folder="../templates")

@experiments_blueprint.route('/sample')
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
