import datetime
import ipaddress
import os
import sys
import json
import logging
import time

from constants import DICT_NETWORK_DEV, DEV_DIR, DEV_DISCOVERY_DIR


class DeviceRegistryService(object):
    _instance = None
    _log = None
    _dev_skeleton = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._log = logging.getLogger(__name__)
        # self._make_folders()

    def _make_folders(self, path_dir=DEV_DIR):
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

    def get_all_devices(self, dev_dir=DEV_DIR):
        devices = []
        '''for dev in [dev for dev in os.listdir(dev_dir) if dev.endswith(".json")]:
            try:
                with open(os.path.join(dev_dir, dev)) as device:
                    devices.append(json.loads(device.read()))
            except Exception as e:
                self._log.error("Cannot read device %s: %s" % (dev, str(e)))'''
        # return sorted(devices, key=lambda entity: entity.get("index", sys.maxsize))
        for _dir, _dir_next, _file in os.walk(dev_dir):
            if len(_file) > 0:
                for dev in _file:
                    try:
                        with open(os.path.join(_dir, dev)) as device:
                            devices.append(json.loads(device.read()))
                    except Exception as e:
                        self._log.error("Cannot read device %s: %s" % (dev, str(e)))
        return sorted(devices, key=lambda entity: int(ipaddress.ip_address(entity.get("ip"))))

    def update_device(self, device, dev_dir=DEV_DIR) -> bool:
        dev_type = device.get('type', 'other')
        dev_name = device.get('name')
        for dev_category in DICT_NETWORK_DEV.values():
            if dev_category.get(dev_type, None) is not None:
                if dev_dir != DEV_DISCOVERY_DIR:
                    dev_dir = os.path.join(dev_category.get(dev_type).get('dir'), dev_type)
                else:
                    dev_dir = DEV_DISCOVERY_DIR
        try:
            self._make_folders(dev_dir)
            path = os.path.join(dev_dir, dev_name + ".json")
            if os.path.exists(path):
                with open(path, "w") as f:
                    return f.write(json.dumps(device, indent=4))
        except Exception as e:
            return False

    def add_device(self, device: dict, dev_dir: str = DEV_DIR) -> bool:
        dev_type = device.get('type', 'other')
        dev_name = device.get('name')
        for dev_category in DICT_NETWORK_DEV.values():
            if dev_category.get(dev_type, None) is not None:
                if dev_dir != DEV_DISCOVERY_DIR:
                    dev_dir = os.path.join(dev_category.get(dev_type).get('dir'), dev_type)
                else:
                    dev_dir = DEV_DISCOVERY_DIR
        try:
            self._make_folders(dev_dir)
            path = os.path.join(dev_dir, dev_name + '.json')
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write(json.dumps(device, indent=4))
                return True
        except Exception as e:
            return False

    def del_device(self, devices: list, dev_dir=DEV_DIR) -> bool:
        try:
            for name_dev in devices:
                path = os.path.join(dev_dir, str(name_dev) + '.json')
                if os.path.exists(path):
                    os.remove(path)
            return True
        except Exception as e:
            self._log.debug(f"Ошибка удаления устройства: {e}")
        return False

    def set_dev_skeleton(self, name, ip, type_dev, monitoring: str or list = 'enable',
                         monitoring_snmp: str or list = 'enable', group: str = 'other'):
        self._dev_skeleton = {
            'name': str(name),
            'ip': str(ip),
            'type': str(type_dev),
            'monitoring': (
                'enable' if 'ping' in monitoring or monitoring == 'enable' else 'disable'),
            'monitoring_snmp': (
                'enable' if 'snmp' in monitoring_snmp or monitoring_snmp == 'enable' else 'disable'),
            'group': str(group), 'notification': 'enable',
            'snmp': (
                {
                    'name': ''
                }
            ),


            'index': int(datetime.datetime.now().timestamp())}
        '''if str(type_dev) in DICT_NETWORK_DEV['NETWORK'].keys() else {
                                        'name': '',
                                        'rx_signal': '',
                                        'tx_signal': '',
                                        'distance': '',
                                        'ccq': ''
                                    }'''

    def get_dev_skeleton(self) -> dict:
        dev_skeleton = self._dev_skeleton
        self._dev_skeleton = None
        return dev_skeleton
