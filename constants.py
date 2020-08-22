import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
WEB_DIR = os.path.join(RESOURCES_DIR, "web")
LOG_DIR = os.path.join(BASE_DIR, "log")
DEV_DIR = os.path.join(RESOURCES_DIR, 'devices')
DEV_NETWORK_DIR = os.path.join(DEV_DIR, 'network')
DEV_WIFI_DIR = os.path.join(DEV_DIR, 'wifi')
DEV_CAMS_DIR = os.path.join(DEV_DIR, 'cams')
DEV_OTHER_DIR = os.path.join(DEV_DIR, 'other')
DEV_DISCOVERY_DIR = os.path.join(RESOURCES_DIR, 'discovery')

OFFLINE_STATE = "offline"
ONLINE_STATE = "online"
RUN_DISCOVERY_STATE = "run"
STOP_DISCOVERY_STATE = "stop"

DISCOVERY_PERIOD_SEC = int(os.environ.get("DISCOVERY_PERIOD_SEC", default=30))

DICT_NETWORK_DEV = {
    'NETWORK': {
        'router': {
            'cols': 1,
            'dir': DEV_NETWORK_DIR
        },
        'switch': {
            'cols': 1,
            'dir': DEV_NETWORK_DIR
        }
    },
    'WIFI': {
        'ap': {
            'cols': 9,
            'dir': DEV_WIFI_DIR
        },
        'station': {
            'cols': 9,
            'dir': DEV_WIFI_DIR
        }
    },
    'CAMS': {
        'ip-cam': {
            'cols': 1,
            'dir': DEV_CAMS_DIR
        }
    },
    'OTHER': {
        'other': {
            'cols': 1,
            'dir': DEV_OTHER_DIR
        }
    }
}
