import os
import re
from collections import UserDict

import yaml


class Config(UserDict):

    def __init__(self, *args):
        super(Config, self).__init__(*args)

    def set(self, name, value):
        self.data[name] = value

    def update_or_add(self, key, data):
        if self.get(key):
            self.get(key).update(data)
        else:
            self.set(key, data)

    def get_config(self, name):
        return Config(self.get(name, {}))

    def get_type(self, name, default=None, as_type=None):
        val = self.get(name, default)
        return as_type(val) if as_type else val

    def get_bool(self, name, default=False):
        val = self.get_type(name, default)
        return str(val).lower() == 'true'

    def get_int(self, name, default=None):
        return int(self.get_type(name, default))

    def get_float(self, name, default=None):
        return float(self.get_type(name, default))

    def get_list(self, name, default=None):
        return list(self.get_type(name, default))

    def get_dict(self, name, default=None):
        return dict(self.get_type(name, default))

    def get_path(self, name, default=None):
        raw = self.get_type(name, default)
        if not raw:
            return None
        raw = re.split('[/\\\\]+', raw)
        return os.sep.join(raw)

    @classmethod
    def from_yaml(self, props_file):
        with open(props_file, 'r') as props:
            return self(yaml.safe_load(props))
