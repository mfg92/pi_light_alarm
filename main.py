# http://flask.pocoo.org/docs/0.10/quickstart/
# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

import shelve
# from flask.ext import shelve

from flask import Flask, jsonify
from flask import request
from flask import abort, make_response, send_from_directory
from flask import g
import threading
import light_controll
import json
import datetime

app = Flask(__name__, static_url_path='')

__db_lock = threading.RLock()


# lctrl.add_controll_event(light_controll.ControllEvent(
#     datetime.datetime.now()+datetime.timedelta(seconds=5),
#     datetime.datetime.now()+datetime.timedelta(seconds=15)
# ))


@app.before_first_request
def _run_on_start():
    print("BLA LBUB")
    app.id_to_ctrlevent = {}

    app.lctrl = light_controll.LightControll()
    app.lctrl.start()

    app.manual_ctrl_event = light_controll.ControllEvent(start_dtime=0,
                                                         end_dtime=0,
                                                         repeate_delay=None)

    # load values from db into lctrl
    db = get_db()
    for id in db['alarms']:
        alarm = db['alarms'][id]
        print(alarm)
        if alarm['enabled']:
            ctrlevent = make_ctrlevent(alarm)
            app.id_to_ctrlevent[id] = ctrlevent
            app.lctrl.add_controll_event(ctrlevent)
        else:
            print('Not added')


def get_db():
    __db_lock.acquire()
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open('shelve.db', writeback=True)
        db.setdefault('alarms', {})
    return db


@app.teardown_request
def clear_lock(exception):
    if __db_lock._is_owned():
        __db_lock.release()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/app/<path:path>')
def send_static_app(path):
    print(path)
    return send_from_directory('static/app/', path)


@app.route('/app/bower_components/<path:path>')
def send_static_bower(path):
    print(path)
    return send_from_directory('static/bower_components/', path)


@app.route('/api/v1/test/')
def test():
    return 'OK'


@app.route('/api/v1/light/', methods=['GET'])
def get_light():
    return json.dumps({'brightness': app.lctrl.brightness})


@app.route('/api/v1/light/', methods=['PUT'])
def set_light():
    brightness = float(request.json['brightness'])
    duration = float(request.json['duration'])
    try:
        app.lctrl.remove_controll_event(app.manual_ctrl_event)
    except:
        pass
    now = datetime.datetime.now()
    app.manual_ctrl_event.start_dtime = datetime.datetime(year=datetime.MINYEAR, month=1, day=1)
    app.manual_ctrl_event.end_dtime = now + datetime.timedelta(seconds=duration)
    app.manual_ctrl_event.start_brightness = app.manual_ctrl_event.end_brightness = brightness
    app.lctrl.add_controll_event(app.manual_ctrl_event)
    return "OK"


@app.route('/api/v1/alarms/', methods=['GET'])
def list_alarms():
    print("Start listing alarms")
    db = get_db()
    # return jsonify({'alarms': list(db['alarms'].values())})
    return json.dumps(list(db['alarms'].values()))


@app.route('/api/v1/alarms/', methods=['POST'])
def insert_alarm():
    id = get_free_id()
    alarm = {"alarm_hour": int(request.json['alarm_hour']),
             "alarm_min": int(request.json['alarm_min']),
             "light_offset": int(request.json['light_offset']),
             "name": request.json['name'],
             "enabled": bool(request.json['enabled']),
             "id": id}
    db = get_db()
    db['alarms'][id] = alarm

    if alarm['enabled']:
        ctrlevent = make_ctrlevent(alarm)
        app.id_to_ctrlevent[id] = ctrlevent
        app.lctrl.add_controll_event(ctrlevent)

    return json.dumps(alarm)


@app.route('/api/v1/alarms/<int:id>/', methods=['PUT'])
def update_alarm(id):
    db = get_db()
    old = db['alarms'][id]

    alarm = {"alarm_hour": int(request.json['alarm_hour']),
             "alarm_min": int(request.json['alarm_min']),
             "light_offset": int(request.json['light_offset']),
             "name": request.json['name'],
             "enabled": bool(request.json['enabled'])}
    alarm['id'] = id

    print("Old", old)
    print("New", alarm)
    if old['enabled']:
        ce = app.id_to_ctrlevent[id]
        try:
            app.lctrl.remove_controll_event(ce)
        except:
            print("The updated alarm was not running")
        del app.id_to_ctrlevent[id]

    db['alarms'][id] = alarm

    if alarm['enabled']:
        ctrlevent = make_ctrlevent(alarm)
        app.id_to_ctrlevent[id] = ctrlevent
        app.lctrl.add_controll_event(ctrlevent)

    return json.dumps(alarm)


def make_ctrlevent(alarm):
    end_time = datetime.time(alarm['alarm_hour'], alarm['alarm_min'])
    end_dtime = datetime.datetime.combine(datetime.date.today(), end_time)
    start_dtime = end_dtime - datetime.timedelta(seconds=alarm['light_offset']*60)

    if end_dtime < datetime.datetime.now():
        start_dtime += datetime.timedelta(days=1)
        end_dtime += datetime.timedelta(days=1)

    return light_controll.ControllEvent(start_dtime=start_dtime,
                                        end_dtime=end_dtime,
                                        repeate_delay=datetime.timedelta(days=1))


@app.route('/api/v1/alarms/<int:id>/', methods=['DELETE'])
def delete_alarm(id):
    db = get_db()

    if id not in db['alarms']:
        abort(404)

    old = db['alarms'][id]

    if old['enabled']:
        ce = app.id_to_ctrlevent[id]
        try:
            app.lctrl.remove_controll_event(ce)
        except:
            print("The delted alarm was not running")
        del app.id_to_ctrlevent[id]

    del db['alarms'][id]
    return ""


@app.route('/api/v1/alarms/<int:id>/')
def get_alarm(id):
    db = get_db()
    for alarm in db['alarms']:
        if alarm["id"] == id:
            return jsonify(alarm)
    abort(404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def get_free_id():
    db = get_db()
    try:
        res = db['free_alarm_id']
    except KeyError:
        res = 0
    db['free_alarm_id'] = res + 1
    return res


if __name__ == '__main__':
    # run the server, listen on all public IPs.
    app.run(host='0.0.0.0', debug=True)
