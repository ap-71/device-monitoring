import datetime
import os
import sys
import json
import logging
import time

from constants import DICT_NETWORK_DEV, DEV_DIR

'''BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")'''


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

    def _make_folders(self):
        if not os.path.exists(DEV_DIR):
            os.makedirs(DEV_DIR)

    def __init__(self):
        self._log = logging.getLogger(__name__)
        # self._make_folders()

    def get_all_devices(self, dev_dir=DEV_DIR):
        devices = []
        for dev in [dev for dev in os.listdir(dev_dir) if dev.endswith(".json")]:
            try:
                with open(os.path.join(dev_dir, dev)) as device:
                    devices.append(json.loads(device.read()))
            except Exception as e:
                self._log.error("Cannot read device %s: %s" % (dev, str(e)))
        return sorted(devices, key=lambda entity: entity.get("index", sys.maxsize))

    def update_device(self, device, dev_dir=DEV_DIR):
        path = os.path.join(dev_dir, device.get("name") + ".json")
        if os.path.exists(path):
            with open(path, "w") as f:
                return f.write(json.dumps(device, indent=4))

    def add_device(self, devices, dev_dir=DEV_DIR) -> bool:
        path = os.path.join(dev_dir, devices.get('name') + '.json')
        try:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write(json.dumps(devices, indent=4))
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
                } if str(type_dev) in DICT_NETWORK_DEV['NETWORK'] else {
                    'name': '',
                    'rx_signal': '',
                    'tx_signal': '',
                    'distance': '',
                    'ccq': ''
                }
            ),

            'index': int(datetime.datetime.now().timestamp())}

    def get_dev_skeleton(self) -> dict:
        dev_skeleton = self._dev_skeleton
        self._dev_skeleton = None
        return dev_skeleton
