import json
import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")


class StatusService(object):
    _instance = None
    _state_ds = None
    _state_dw = None
    _log = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._log = logging.getLogger(__name__)

    def set_discovery_service(self, state):
        self._log.debug('DS change state to: {}'.format(str(state)))
        self._log.info('DS change state to: {}'.format(str(state)))
        self._state_ds = 'True' if state else 'False'
        if (self._state_ds in ['True']) != self.get_discovery_service():
            self.write_status_to_file()

    def set_discovery_worker(self, state):
        self._log.debug('DW change state to: {}'.format(str(state)))
        self._log.info('DW change state to: {}'.format(str(state)))
        self._state_dw = 'True' if state else 'False'
        if (self._state_dw in ['True']) != self.get_discovery_worker():
            self.write_status_to_file()

    def get_discovery_service(self) -> bool:
        return self.read_status().get('ds') in ['True']

    def get_discovery_worker(self) -> bool:
        return self.read_status().get('dw') in ['True']

    def read_status(self) -> dict:
        try:
            with open(os.path.join(RESOURCES_DIR, 'statusService.json')) as statusService:
                return json.loads(statusService.read())
        except Exception as e:
            self._log.error("Cannot read statusService.json : %s" % (str(e)))

    def write_status_to_file(self):
        if os.path.exists(os.path.join(RESOURCES_DIR, 'statusService.json')):
            with open(os.path.join(RESOURCES_DIR, 'statusService.json'), "w") as f:
                return f.write(json.dumps({'ds': self._state_ds,
                                           'dw': self._state_dw}, indent=4))
