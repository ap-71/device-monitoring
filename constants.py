import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
WEB_DIR = os.path.join(RESOURCES_DIR, "web")
LOG_DIR = os.path.join(BASE_DIR, "log")
DEV_DIR = os.path.join(RESOURCES_DIR, 'devices')
DEV_DISCOVERY_DIR = os.path.join(RESOURCES_DIR, 'discovery')

OFFLINE_STATE = "offline"
ONLINE_STATE = "online"
RUN_DISCOVERY_STATE = "run"
STOP_DISCOVERY_STATE = "stop"

DISCOVERY_PERIOD_SEC = int(os.environ.get("DISCOVERY_PERIOD_SEC", default=30))

DICT_NETWORK_DEV = {
    'NETWORK': ['router'],
    'WIFI': ['ap', 'station', 'wifi'],
    'OTHER': ['other']
}
