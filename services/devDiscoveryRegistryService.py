import os
import sys
import json
import logging
import time

from constants import DEV_DISCOVERY_DIR
from services.deviceRegistryService import DeviceRegistryService


'''BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")'''


class DevDiscoveryRegistryService(object):
    _instance = None
    _dev_dir = None
    _log = None
    _devRegService = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def _make_folders(self):
        if not os.path.exists(DEV_DISCOVERY_DIR):
            os.makedirs(DEV_DISCOVERY_DIR)

    def __init__(self):
        self._log = logging.getLogger(__name__)
        self._devRegService = DeviceRegistryService()
        # self._make_folders()

    def get_all_devices(self) -> dict:
        return self._devRegService.get_all_devices(DEV_DISCOVERY_DIR)

    def add_device(self, devices: dict) -> bool:
        return self._devRegService.add_device(devices, DEV_DISCOVERY_DIR)

    def del_device(self, devices: list) -> bool:
        return self._devRegService.del_device(devices, DEV_DISCOVERY_DIR)
