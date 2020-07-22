import time
import logging
import datetime
import threading
from constants import *
from flask import Flask, request, flash
from jinja2 import Template
from flask import make_response, render_template
from flask import send_from_directory
from mockDataGenerator import generate_mock_data
from services.discoveryService import DiscoveryService
from services.notificationService import NotificationService
from services.deviceRegistryService import DeviceRegistryService
from services.groupRegistryService import GroupRegistryService

if os.environ.get("LOG_MODE") == "prod":
    # logging in prod mode
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(
        format=u'%(threadName)s\t%(filename)s\t[LINE:%(lineno)d]# %(levelname)-8s\t [%(asctime)s]  %(message)s',
        level="INFO",
        handlers=[logging.FileHandler(os.path.join(LOG_DIR, "log.txt"), 'w', 'utf-8')])
else:
    # logging in dev mode
    logging.basicConfig(
        format=u'%(threadName)s\t%(filename)s\t[LINE:%(lineno)d]# %(levelname)-8s\t [%(asctime)s]  %(message)s',
        level="DEBUG")

log = logging.getLogger(__name__)

if os.environ.get("DEMO_MODE", "disable") == "enable":
    generate_mock_data()


notificationService = NotificationService.get_instance()
discoveryService = DiscoveryService.get_instance()
deviceRegistryService = DeviceRegistryService.get_instance()
groupRegistryService = GroupRegistryService.get_instance()


def pretty_datetime(data):
    try:
        return datetime.datetime.fromtimestamp(data).strftime("%d.%m.%Y %H:%M:%S")
    except Exception as e:
        log.error("Cannot format for datetime: %s" % str(e))
    return "-"


def do_discovery():
    while True:
        try:
            discoveryService.discover_devices()
        except Exception as e:
            notificationService.notify("ERROR DISCOVERY! " + str(e))
        time.sleep(DISCOVERY_PERIOD_SEC)


threading.Thread(target=do_discovery, args=(), daemon=True).start()

app = Flask(__name__, template_folder=WEB_DIR, static_url_path='/static', static_folder=os.path.join(WEB_DIR, "static"))


@app.route('/')
def index():
    data_dto = dict(devices=deviceRegistryService.get_all_devices())
    data_dto.update(dict(groups=groupRegistryService.get_all_groups()))
    for dev in data_dto.get("devices"):
        dev["last_discovery"] = pretty_datetime(dev.get("last_discovery"))
        dev["last_online"] = pretty_datetime(dev.get("last_online"))
    return render_template('index.html', **data_dto)
    '''with open(os.path.join(WEB_DIR, "index.html")) as f:
        return make_response(Template(f.read()).render(**data_dto))'''


@app.route('/action_<url_action>_<url_type>', methods=('GET', 'POST'))
def din_url_action(url_action, url_type):
    discoverys = False
    path = os.path.join(url_action, '{str_url_type}.html'.format(str_url_type=url_type))
    path_full = os.path.join(WEB_DIR, path)
    if os.path.isfile(path_full):
        data_dto = dict(devices=deviceRegistryService.get_all_devices())
        data_dto.update(dict(groups=groupRegistryService.get_all_groups()))
        if request.method == 'POST':
            try:
                if request.form['add_group_submit'] == 'True':
                    group = {
                        'name': request.form['add_group_name'],
                        'description': request.form['add_group_description']
                    }
                    groupRegistryService.add_group(group)
                    for dev_name in request.form.getlist('add_group_devices'):
                        for dev in data_dto.get("devices"):
                            if dev["name"] == dev_name:
                                dev["group"] = group['name']
                            deviceRegistryService.update_device(dev)
            except:
                pass

            try:
                if request.form['add_device_submit'] == 'True':
                    dev = {
                        'name': str(request.form['add_dev_name']),
                        'ip': str(request.form['add_dev_ip']),
                        'monitoring': (
                            'enable' if 'ping' in request.form.getlist('add_dev_services') else 'disable'),
                        'monitoring_snmp': (
                            'enable' if 'snmp' in request.form.getlist('add_dev_services') else 'disable'),
                        'group': str(request.form['add_dev_group']), 'notification': 'enable',
                        'index': int(datetime.datetime.now().timestamp())}
                    write = deviceRegistryService.add_device(dev)
                    flash('Устройство добавлено' if write else 'Ошибка добавления')

            except:
                pass

            try:
                if request.form['del_group_submit'] == 'True':
                    for name in request.form.getlist('del_group_names'):
                        group = {'name': str(name)}
                        groupRegistryService.del_group(group)

            except:
                pass

            try:
                if request.form['del_device_submit'] == 'True':
                    for name in request.form.getlist('del_dev_names'):
                        dev = {'name': str(name)}
                        deviceRegistryService.del_device(dev)

            except:
                pass

            '''for dev in data_dto.get("devices"):
            dev["last_discovery"] = pretty_datetime(dev.get("last_discovery"))
            dev["last_online"] = pretty_datetime(dev.get("last_online"))'''
        return render_template(path, url_action=url_action, url_type=url_type, **data_dto)
    else:
        return render_template('404.html')


@app.route('/<url>')
def din_url(url):
    discoverys = True
    data_dto = dict(devices=deviceRegistryService.get_all_devices())
    data_dto.update(dict(groups=groupRegistryService.get_all_groups()))
    for dev in data_dto.get("devices"):
        dev["last_discovery"] = pretty_datetime(dev.get("last_discovery"))
        dev["last_online"] = pretty_datetime(dev.get("last_online"))
    return render_template('obj.html', page=url, **data_dto)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
