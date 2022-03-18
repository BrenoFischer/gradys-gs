from flask import Blueprint, render_template
from copter_factory import get_copter_instance
from args_manager import get_args

position_blueprint = Blueprint("position_blueprint", __name__, template_folder="../templates")

@position_blueprint.route('/position')
def flask_position():
    copter = get_copter_instance()
    args = get_args()
    targetpos = copter.mav.location(relative_alt=True)
    json_tmp = '{"id": ' + str(args.uav_sysid) + ', "lat":' + str(targetpos.lat) + ', "lng": ' + str(targetpos.lng) + ', "high": ' + str(targetpos.alt) + '}'
    return render_template('return.html', name=json_tmp)   

@position_blueprint.route('/position_relative_json')
def flask_position_json():
    copter = get_copter_instance()
    args = get_args()
    targetpos = copter.mav.location(relative_alt=True)
    json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'
    print(json_tmp)
    return json_tmp


@position_blueprint.route('/position_absolute_json')
def flask_position_relative_json():
    copter = get_copter_instance()
    args = get_args()
    targetpos = copter.mav.location(relative_alt=False)
    json_tmp = '{"id": ' + str(args.uav_sysid) + ',"lat": ' + str(targetpos.lat) + ',"lng": ' + str(targetpos.lng) + ',"alt":' + str(targetpos.alt) + '}'
    print(json_tmp)
    return json_tmp