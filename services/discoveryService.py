import logging
import os
from queue import Queue
from services.discoveryWorker import DiscoveryWorker
from services.deviceRegistryService import DeviceRegistryService
from services.statusService import StatusService
from services.devDiscoveryRegistryService import DevDiscoveryRegistryService


class DiscoveryService(object):
    _instance = None
    _deviceRegistryService = None
    _devDiscoveryRegService = None
    _discoveryWorkerPool = None
    _statusService = None
    _state = None
    _log = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def __init__(self, status_service: StatusService = StatusService.get_instance()):
        self._statusService = status_service
        self._log = logging.getLogger(__name__)
        self._deviceRegistryService = DeviceRegistryService.get_instance()
        self._devDiscoveryRegService = DevDiscoveryRegistryService.get_instance()
        self._discoveryWorkerPool = int(os.environ.get("DISCOVERY_WORKER_POOL", 10))

    def discover_devices(self):
        self.worker(self._discoveryWorkerPool, self._deviceRegistryService.get_all_devices())

    def search_device(self, devices: list):
        self.worker(20500, devices, True)

    def worker(self, pool: int,  devices: list, search: bool = False):
        if self._statusService.get_discovery_service() or search:
            queue = Queue()

            for _ in range(len(devices) if len(devices) < pool else pool):
                # (очередь устройств; поиск устройств?; статус сервиса - не работает если идет поиск устройств)
                t = DiscoveryWorker(queue, search, self._statusService)
                t.setDaemon(True)
                t.start()

            for device in devices:
                if device.get("monitoring", "enable") == "enable":
                    queue.put(device)

            queue.join()

    def start_service(self, state_discovery_service=True, state_discovery_worker=True):
        self._statusService.set_discovery_service(state_discovery_service)
        self._statusService.set_discovery_worker(state_discovery_worker)

    def stop_service(self, state_discovery_service=True, state_discovery_worker=True):
        self._statusService.set_discovery_service(not state_discovery_service)
        self._statusService.set_discovery_worker(not state_discovery_worker)

    def status_service(self) -> dict:
        status = {
            'ds': self._statusService.get_discovery_service(),
            'dw': self._statusService.get_discovery_worker()
        }
        return status
