import os
import sys
import json
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")


class GroupRegistryService(object):
    _instance = None
    _group_dir = None
    _log = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def _make_folders(self):
        if not os.path.exists(self._group_dir):
            os.makedirs(self._group_dir)

    def __init__(self):
        self._log = logging.getLogger(__name__)
        self._group_dir = os.path.join(RESOURCES_DIR, "groups")
        # self._make_folders()

    def get_all_groups(self):
        groups = []
        for group in [group for group in os.listdir(self._group_dir) if group.endswith(".json")]:
            try:
                with open(os.path.join(self._group_dir, group)) as group_read:
                    groups.append(json.loads(group_read.read()))
            except Exception as e:
                self._log.error("Cannot read group %s: %s" % (group, str(e)))
        return sorted(groups, key=lambda entity: entity.get("index", sys.maxsize))

    def update_group(self, group):
        path = os.path.join(self._group_dir, group.get("name") + ".json")
        if os.path.exists(path):
            with open(path, "w") as f:
                return f.write(json.dumps(group, indent=4))

    def add_group(self, group) -> bool:
        path = os.path.join(self._group_dir, group.get('name') + '.json')
        try:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write(json.dumps(group, indent=4))
                return True
        except Exception as e:
            return False

    def del_group(self, groups: list) -> bool:
        try:
            for name_group in groups:
                path = os.path.join(self._group_dir, str(name_group) + '.json')
                if os.path.exists(path):
                    os.remove(path)
            return True
        except Exception as e:
            self._log.debug(f"Ошибка удаления группы: {e}")
        return False
