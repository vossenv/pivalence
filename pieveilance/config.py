import configparser
import os
import re
from copy import deepcopy


class Config:

    def __init__(self, value_dict):
        self.values = value_dict

    def set(self, name, value):
        self.values[name] = value

    def get(self, name, default=None, as_type=None):
        val = self.values.get(name) or default
        return as_type(val) if as_type else val

    def get_bool(self, name, default=False):
        val = self.get(name, default)
        return str(val).lower() == 'true'

    def get_int(self, name, default=None):
        return int(self.get(name, default))

    def get_list(self, name, default=None):
        return list(self.get(name, default))

    def get_dict(self, name, default=None):
        return dict(self.get(name, default))

    def get_path(self, name, default=None):
        raw = self.get(name, default)
        if not raw:
            return None
        raw = re.split('[/\\\\]+', raw)
        return os.sep.join(raw)


class ConfigLoader:

    def __init__(self, props_file):
        self.values = self.from_properties(props_file)

    @classmethod
    def load(cls, props_file):
        return cls(props_file)

    def get_config(self, name):
        if name in self.values:
            return Config(self.get_dict_config(name))

    def get_dict_config(self, name=None):
        if not name:
            return deepcopy(self.values)
        else:
            return deepcopy(self.values.get(name))

    def from_properties(self, props_file):
        config = {}
        parser = configparser.RawConfigParser()
        parser.read(props_file)

        for s, v in parser._sections.items():
            config[s] = v
        return config

    def set(self, section, name, value):
        if section not in self.values:
            self.values[section] = {}
        self.values[section][name] = value

    def get(self, section, name, default=None, as_type=None):
        if section not in self.values:
            val = default
        else:
            val = self.values[section].get(name) or default
        return as_type(val) if as_type else val

    def get_bool(self, section, name, default=False):
        val = self.get(section, name, default)
        return str(val).lower() == 'true'

    def get_int(self, section, name, default=None):
        return int(self.get(section, name, default))

    def get_list(self, section, name, default=None):
        return list(self.get(section, name, default))

    def get_dict(self, section, name, default=None):
        return dict(self.get(section, name, default))

    def get_path(self, section, name, default=None):
        raw = self.get(section, name, default)
        if not raw:
            return None
        raw = re.split('[/\\\\]+', raw)
        return os.sep.join(raw)
