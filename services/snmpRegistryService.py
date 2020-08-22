import os
import sys
import json
import logging
import time

from services.statusService import StatusService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")


class SnmpRegistryService(object):
    _instance = None
    _snmp_conf = None
    _log = None
    # _statusService = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    '''def _make_folders(self):
        if not os.path.exists(self._dev_dir):
            os.makedirs(self._dev_dir)'''

    def __init__(self):
        self._log = logging.getLogger(__name__)
        self._snmp_conf = f"{RESOURCES_DIR}/snmp_conf.json"

    def get_all_oid(self):
        devtype_oid = []
        try:
            with open(self._snmp_conf) as snmp_conf:
                devtype_oid.append(json.loads(snmp_conf.read()))
        except Exception as e:
            self._log.error("Cannot read snmp configuration file %s: %s" % (self._snmp_conf, str(e)))
        return sorted(devtype_oid, key=lambda entity: entity.get("index", sys.maxsize))

    def update_snmp_conf(self, data):
        path = os.path.join(self._snmp_conf)
        if os.path.exists(path):
            with open(path, "w") as f:
                return f.write(json.dumps(data, indent=4))

    def add_type(self, data: dict) -> bool:
        path = os.path.join(self._snmp_conf)
        # try:
        read_snmp_conf = dict(self.get_all_oid()[0])
        print(read_snmp_conf)
        for _type in data.get('type').keys():
            if read_snmp_conf.get('type').get(_type, None) is None:
                read_snmp_conf['type'].update({_type: data['type'][_type]})
            else:
                print(False)
        print(path)
        print(read_snmp_conf)
        if os.path.exists(path):
            with open(path, 'w') as f:
                f.write(json.dumps(read_snmp_conf, indent=4))
            return True
        # except Exception as e:
        #     return False

    '''def del_device(self, device):
        path = os.path.join(self._dev_dir, device.get('name') + '.json')
        if os.path.exists(path):
            os.remove(path)'''
