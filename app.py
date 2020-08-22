import time
import logging
import datetime
import threading
import ipaddress
from constants import *
from flask import Flask, request, flash
from jinja2 import Template
from flask import make_response, render_template
from flask import send_from_directory
from mockDataGenerator import generate_mock_data
from services.discoveryService import DiscoveryService
from services.notificationService import NotificationService
from services.deviceRegistryService import DeviceRegistryService
from services.devDiscoveryRegistryService import DevDiscoveryRegistryService
from services.groupRegistryService import GroupRegistryService
from services.snmpRegistryService import SnmpRegistryService

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
devDiscoveryRegService = DevDiscoveryRegistryService.get_instance()
snmpRegistryService = SnmpRegistryService.get_instance()
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
            notificationService.notify(f"ERROR DISCOVERY! {e}")
        time.sleep(DISCOVERY_PERIOD_SEC)


def do_search_dev(devs: list):
    try:
        discoveryService.search_device(devs)
    except Exception as e:
        notificationService.notify(f"ERROR SEARCH DEVICES! {e}")


threading.Thread(target=do_discovery, args=(), daemon=True).start()

app = Flask(__name__, template_folder=WEB_DIR, static_url_path='/static', static_folder=os.path.join(WEB_DIR, "static"))


def change_status_btn():
    try:
        if request.form['btn-service-on'] == 'True':
            discoveryService.start_service()
    except:
        pass

    try:
        if request.form['btn-service-off'] == 'True':
            discoveryService.stop_service()
    except:
        pass


@app.route('/', methods=('GET', 'POST'))
def index():
    discoveryService.start_service()
    data_dto = dict(devices=deviceRegistryService.get_all_devices())
    data_dto.update(dict(groups=groupRegistryService.get_all_groups()))
    data_dto.update(dict(type_devs=snmpRegistryService.get_all_oid()))
    for dev in data_dto.get("devices"):
        dev["last_discovery"] = pretty_datetime(dev.get("last_discovery"))
        dev["last_online"] = pretty_datetime(dev.get("last_online"))
    if request.method == 'POST':
        change_status_btn()
    status_services = discoveryService.status_service()
    type_dev_result = []
    for type_main in DICT_NETWORK_DEV.values():
        for type_dev in type_main:
            type_dev_result.append(type_dev)
    return render_template('index.html', CONST=DICT_NETWORK_DEV, filter_obj=type_dev_result, page=None,
                           sc=status_services.get('ds'),
                           **data_dto)


@app.route('/action_<url_action>_<url_type>', methods=('GET', 'POST'))
def din_url_action(url_action, url_type):
    discoveryService.stop_service()
    path = f'{url_action}/{url_type}.html'
    path_full = os.path.join(WEB_DIR, path)
    data_dto = dict(
        devices=deviceRegistryService.get_all_devices()
    ) if not url_type == 'dev-discovery' else dict(
        devices=devDiscoveryRegService.get_all_devices()
    )
    data_dto.update(dict(groups=groupRegistryService.get_all_groups()))
    data_dto.update(dict(type_devs=snmpRegistryService.get_all_oid()[0]))
    str().upper()
    if os.path.isfile(path_full):
        if request.method == 'POST':
            change_status_btn()

            if request.form.get('add_group_submit') == 'True':
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

            if request.form.get('add_dev_in_group_submit') == 'True':
                for dev_name in request.form.getlist('add_group_devices'):
                    for dev in data_dto.get("devices"):
                        if dev["name"] == dev_name:
                            dev["group"] = request.form['add_dev_in_group']
                        deviceRegistryService.update_device(dev)

            if request.form.get('add_device_submit') == 'True':
                deviceRegistryService.set_dev_skeleton(
                    name=request.form['add_dev_name'],
                    ip=request.form['add_dev_ip'],
                    type_dev=request.form['add_dev_type'],
                    monitoring=request.form.getlist('add_dev_services'),
                    monitoring_snmp=request.form.getlist('add_dev_services'),
                    group=request.form['add_dev_group']

                )
                deviceRegistryService.add_device(deviceRegistryService.get_dev_skeleton())
                # flash('Устройство добавлено' if write else 'Ошибка добавления')

            if request.form.get('del_group_submit') == 'True':
                groupRegistryService.del_group(request.form.getlist('del_group_names'))

            if request.form.get('del_device_submit') == 'True':
                deviceRegistryService.del_device(request.form.getlist('del_dev_names'))
                data_dto.update(dict(devices=deviceRegistryService.get_all_devices()))

            if request.form.get('add_dev_discovery_tmp_submit', 'False') == 'True' \
                    or request.form.get('add_dev_discovery_submit') == 'True':
                if request.form.get('add_dev_discovery_tmp_submit', 'False') == 'True':
                    _devs = []
                    ip_addr_1 = int(ipaddress.ip_address(str(request.form['ip-range-1'])))
                    ip_addr_2 = int(ipaddress.ip_address(str(request.form['ip-range-2'])))
                    for ip in range(ip_addr_1, ip_addr_2+1):
                        deviceRegistryService.set_dev_skeleton(
                            name=ipaddress.ip_address(ip),
                            ip=ipaddress.ip_address(ip),
                            type_dev='other'
                        )
                        _devs.append(deviceRegistryService.get_dev_skeleton())
                    t = threading.Thread(target=do_search_dev(_devs), args=(), daemon=True)
                    t.start()
                    t.join()
                    data_dto.update(dict(
                        devices=devDiscoveryRegService.get_all_devices()
                    ))
                elif request.form.get('add_dev_discovery_submit', 'False') == 'True':
                    for dev_name in request.form.getlist('add_dev_discovery'):
                        for dev in data_dto.get("devices"):
                            if dev["name"] == dev_name:
                                dev["type"] = request.form['add_dev_discovery_type']
                                dev["group"] = request.form['add_dev_discovery_group']
                                deviceRegistryService.add_device(dev)
                    devDiscoveryRegService.del_device(request.form.getlist('add_dev_discovery'))
                    data_dto.update(dict(
                        devices=devDiscoveryRegService.get_all_devices()
                    ))

        status_services = discoveryService.status_service()
        return render_template(path, sc=status_services.get('ds'), url_action=url_action, url_type=url_type, **data_dto)
    else:
        status_services = discoveryService.status_service()
        return render_template('404.html', sc=status_services.get('ds'), **data_dto)


@app.route('/<url>', methods=('GET', 'POST'))
def din_url(url):
    data_dto = dict(devices=deviceRegistryService.get_all_devices())
    data_dto.update(dict(groups=groupRegistryService.get_all_groups()))
    for dev in data_dto.get("devices"):
        dev["last_discovery"] = pretty_datetime(dev.get("last_discovery"))
        dev["last_online"] = pretty_datetime(dev.get("last_online"))
    if request.method == 'POST':
        change_status_btn()
    status_services = discoveryService.status_service()
    return render_template('index.html', CONST=DICT_NETWORK_DEV, filter_obj=request.args.getlist('type'),
                           sc=status_services.get('ds'), page=url, **data_dto)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
