import time
import logging
import threading
from constants import *
from queue import Queue
from services.executorService import ExecutorService
from services.notificationService import NotificationService
from services.deviceRegistryService import DeviceRegistryService
from services.impl.snmpExService import SnmpExService
from services.statusService import StatusService
from services.devDiscoveryRegistryService import DevDiscoveryRegistryService


class DiscoveryWorker(threading.Thread):
    _queue = None
    _log = None
    _ns = None
    _deviceRegistryService = None
    _devDiscoveryRegService = None
    _executorService = None
    _statusService = None
    _search = None

    def __init__(self, queue: Queue, search=False, status_service: StatusService = StatusService.get_instance()):
        threading.Thread.__init__(self)
        self._statusService = status_service
        self._queue = queue
        self._log = logging.getLogger(__name__)
        self._ns = NotificationService.get_instance()
        self._deviceRegistryService = DeviceRegistryService.get_instance()
        self._devDiscoveryRegService = DevDiscoveryRegistryService.get_instance()
        self._executorService = ExecutorService.get_instance()
        self._snmpExService = SnmpExService()
        self._stop_event = threading.Event()
        self._search = search

    def run(self):
        if not self._search:
            while self._statusService.get_discovery_worker():
                self._discovery_device(self._queue.get())
                self._queue.task_done()
        elif self._search:
            while True:
                self._discovery_device(self._queue.get())
                self._queue.task_done()

    def _discovery_device(self, device_dto):
        self._log.debug("Start discovery device %s with ip: %s" % (device_dto.get("name"), device_dto.get("ip")))
        ping_response = self._executorService.exec_ping(device_dto.get("ip"), count=1, timeout=5)

        if not ping_response and not self._search:
            time.sleep(2)
            ping_response = self._executorService.exec_ping(device_dto.get("ip"), count=3, timeout=15)

        if not ping_response and not self._search:
            if device_dto.get("status", OFFLINE_STATE) == ONLINE_STATE:
                device_dto["status"] = OFFLINE_STATE
                if device_dto.get("notification", "enable") == "enable":
                    self._ns.notify("%s is offline!" % device_dto.get("name"))
        elif not self._search:
            device_dto["last_online"] = int(time.time())
            if device_dto.get("status", OFFLINE_STATE) == OFFLINE_STATE:
                device_dto["status"] = ONLINE_STATE
                if device_dto.get("notification", "enable") == "enable":
                    self._ns.notify("%s is online!" % device_dto.get("name"))
        device_dto["last_discovery"] = int(time.time())

        self._get_data_via_snmp(device_dto)

        if not self._search:
            self._deviceRegistryService.update_device(device_dto)
        else:
            if ping_response:
                self._devDiscoveryRegService.add_device(device_dto)
            self._search = False

    def _get_data_via_snmp(self, device_dto):
        try:
            if device_dto.get("monitoring_snmp") == "enable" and device_dto.get("status", OFFLINE_STATE) == ONLINE_STATE:
                self._log.debug(
                    "Start get data via SNMP device %s with ip: %s" % (device_dto.get("name"), device_dto.get("ip")))
                if device_dto.get("type") == 'router':
                    _oid = {
                        'name': '1.3.6.1.2.1.1.5.0'
                    }
                    snmp_response = self._snmpExService.exec_snmp(device_dto.get("ip"), 161, "public", _oid.get('name'))
                    device_dto["snmp"]["name"] = str(
                        (snmp_response if len(snmp_response if snmp_response is not None else 'None') > 0 else 'None'))
                elif device_dto.get("type") == 'ap' or device_dto.get("type") == 'station':
                    _oid = {
                        'name': '1.3.6.1.2.1.1.5',
                        'rx_signal': '1.3.6.1.4.1.41112.1.4.7.1.3',
                        'tx_signal': '1.3.6.1.4.1.41112.1.4.7.1.4',
                        'distance': '1.3.6.1.4.1.41112.1.4.7.1.5',
                        'ccq': '1.3.6.1.4.1.41112.1.4.7.1.6',
                        'ap': '.1.3.6.1.4.1.41112.1.4.7.1.2',
                        'ap-ip': '1.3.6.1.4.1.41112.1.4.7.1.10',
                        'lan0': '1.3.6.1.2.1.2.2.1.8.2',
                        'lan1': '1.3.6.1.2.1.2.2.1.8.3'
                        }
                    for key, oid in _oid.items():
                        if key in ['lan0', 'lan1']:
                            snmp_response = self._snmpExService.exec_snmp(device_dto.get("ip"), 161, "public", oid)
                        else:
                            snmp_response = self._snmpExService.exec_snmp(device_dto.get("ip"), 161, "public", oid, True)
                        if key == 'distance':
                            snmp_response = str(f'{float((snmp_response if snmp_response is not None else 0))/1000}km')
                        device_dto["snmp"][key] = str(
                            (snmp_response if len(snmp_response if snmp_response is not None else 'None') > 0 else 'None'))
        except Exception as e:
            self._log.debug(f"Ошибка работы SNMP: {e}")

