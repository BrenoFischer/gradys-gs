from flask import Blueprint, render_template
from flask_uav_global_variables import get_copter_instance, get_args, get_logger

request_data_from_uav = Blueprint("request_data_from_uav", __name__, template_folder="../templates")

@request_data_from_uav.route('/position')
def flask_position():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /position reached from drone {args.uav_sysid}')
    targetpos = copter.mav.location(relative_alt=True)

    logger.log_info(f'Drone {args.uav_sysid}', f'Preparing JSON with position')
    json_tmp = '{"id": ' + str(args.uav_sysid) + ', "lat":' + str(targetpos.lat) + ', "lng": ' + str(targetpos.lng) + ', "high": ' + str(targetpos.alt) + '}'

    logger.log_info(f'Drone {args.uav_sysid}', f'Sent {json_tmp}')
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /position route')
    return render_template('return.html', name=json_tmp)   

@request_data_from_uav.route('/position_relative_json')
def flask_position_json():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /position_relative_json reached from drone {args.uav_sysid}')
    targetpos = copter.mav.location(relative_alt=True)

    logger.log_info(f'Drone {args.uav_sysid}', f'Preparing JSON with relative position')
    json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'

    print(json_tmp)
    logger.log_info(f'Drone {args.uav_sysid}', f'Sent {json_tmp}')
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /position_relative_json route')
    return json_tmp


@request_data_from_uav.route('/position_absolute_json')
def flask_position_relative_json():
    logger = get_logger()
    copter = get_copter_instance()
    args = get_args()

    logger.log_info(f'Drone {args.uav_sysid}', f'Route /position_absolute_json reached from drone {args.uav_sysid}')
    targetpos = copter.mav.location(relative_alt=False)

    logger.log_info(f'Drone {args.uav_sysid}', f'Preparing JSON with absolute position')
    json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'

    print(json_tmp)
    logger.log_info(f'Drone {args.uav_sysid}', f'Sent {json_tmp}')
    logger.log_info(f'Drone {args.uav_sysid}', f'End of /position_absolute_json route')
    return json_tmp