from flask import Blueprint, render_template
from copter_connection import get_copter_instance
from args_manager import get_args

request_data_from_uav = Blueprint("request_data_from_uav", __name__, template_folder="../templates")

@request_data_from_uav.route('/position')
def flask_position():
    copter = get_copter_instance()
    args = get_args()
    targetpos = copter.mav.location(relative_alt=True)
    json_tmp = '{"id": ' + str(args.uav_sysid) + ', "lat":' + str(targetpos.lat) + ', "lng": ' + str(targetpos.lng) + ', "high": ' + str(targetpos.alt) + '}'
    return render_template('return.html', name=json_tmp)   

@request_data_from_uav.route('/position_relative_json')
def flask_position_json():
    copter = get_copter_instance()
    args = get_args()
    targetpos = copter.mav.location(relative_alt=True)
    json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'
    print(json_tmp)
    return json_tmp


@request_data_from_uav.route('/position_absolute_json')
def flask_position_relative_json():
    copter = get_copter_instance()
    args = get_args()
    targetpos = copter.mav.location(relative_alt=False)
    json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'
    print(json_tmp)
    return json_tmp