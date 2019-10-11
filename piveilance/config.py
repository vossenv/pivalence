import ast
import json
import os
import re
from collections import UserDict, Mapping
from copy import deepcopy
from datetime import datetime, timedelta
from io import StringIO
from json import JSONDecodeError

import yaml
from dateutil import parser
from yaml.scanner import ScannerError


class Config(UserDict):

    def __init__(self, data):
        super(Config, self).__init__(data)

    def get_config(self, name):
        return Config(self.get(name, {}))

    def get_as(self, name, default=None, required=False, as_type=None):
        val = self.get(name, default)
        if required and not val:
            raise AssertionError("Value for " + name + " required but not given")
        if val and as_type:
            val = Parser.parse_type(val, as_type)
        return val if val is not None else default

    def get_bool(self, name, default=False, required=False):
        return self.get_as(name, default, required, bool)

    def get_string(self, name, default=False, required=False, decode=False):
        val = self.get_as(name, default, required, str)
        return Parser.decode(val, True) if decode else val

    def get_int(self, name, default=False, required=False):
        return self.get_as(name, default, required, int)

    def get_float(self, name, default=False, required=False):
        return self.get_as(name, default, required, float)

    def get_list(self, name, default=False, required=False):
        return self.get_as(name, default, required, list)

    def get_dict(self, name, default=False, required=False):
        return self.get_as(name, default, required, dict)

    def merge(self, update):
        self.merge_dict(self.data, update)
        return self

    def get_path(self, name, default=None, required=False):
        raw = self.get_as(name, default, required)
        return os.sep.join(re.split('[/\\\\]+', raw)) if raw else None

    def load_data_for_keys(self, parent, dir=''):
        for r, path in parent.items():
            if path.split('.')[-1].lower() in ['yml', 'yaml']:
                parent[r] = self.load_yaml(os.path.join(dir, path))
            else:
                parent[r] = os.path.join(dir, path)

    @classmethod
    def from_yaml(cls, props_file):
        return Config(cls.load_yaml(props_file))

    @staticmethod
    def load_yaml(yaml_file):
        with open(yaml_file, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def make_dict(keylist, value):
        tree_dict = {}
        for i, key in enumerate(reversed(keylist)):
            val = value if i == 0 else tree_dict
            tree_dict = {
                key: val}
        return tree_dict

    @staticmethod
    def merge_dict(d1, d2, immutable=False):
        """
        # Combine dictionaries recursively
        # preserving the originals
        # assumes d1 and d2 dictionaries!!
        :param d1: original dictionary
        :param d2: update dictionary
        :return:
        """

        d1 = {} if d1 is None else d1
        d2 = {} if d2 is None else d2
        d1 = deepcopy(d1) if immutable else d1

        for k in d2:
            # if d1 and d2 have dict for k, then recurse
            # else assign the new value to d1[k]
            if (k in d1 and isinstance(d1[k], Mapping)
                    and isinstance(d2[k], Mapping)):
                Config.merge_dict(d1[k], d2[k])
            else:
                d1[k] = d2[k]
        return d1


class Parser():

    @staticmethod
    def parse_type(value, as_type):

        try:
            if as_type == bool:
                return Parser.parse_bool(value)
            elif as_type == list:
                return Parser.parse_list(value)
            elif as_type == dict:
                return Parser.parse_dict(value)
            elif as_type == timedelta:
                return Parser.parse_time_delta(value)
            elif as_type == datetime:
                return Parser.parse_datetime(value)
            elif as_type == "json":
                return Parser.parse_yaml_json(value, data_type="json")
            elif as_type == "yaml":
                return Parser.parse_yaml_json(value, data_type="yaml")
            else:
                return as_type(value)
        except:
            raise TypeError("Error parsing {0} as type {1}".format(value, as_type))

    @staticmethod
    def parse_datetime(date):
        if isinstance(date, datetime):
            return date
        if not isinstance(date, str):
            return TypeError("Cannot parse date '{0}' from type: {1}".
                             format(str(datetime), str(type(datetime))))
        return parser.parse(date)

    @staticmethod
    def parse_bool(value):
        if not value:
            return False
        if isinstance(value, bool):
            return value
        if value in ["1", "0", 1, 0]:
            return str(value) == "1"
        elif value.lower() in ["true", "false"]:
            return value == "true"
        raise TypeError("Cannot cast: " + str(value) + " to boolean")

    @staticmethod
    def parse_list(value):
        if isinstance(value, set):
            return list(value)
        else:
            return Parser.parse_collection(value, list)

    @staticmethod
    def parse_dict(value):
        return Parser.parse_collection(value, dict)

    @staticmethod
    def parse_collection(value, as_type=None):
        if value is None:
            return as_type()
        elif as_type and isinstance(value, as_type):
            return value
        else:
            try:
                value = value.decode()
            except:
                pass
            try:
                return json.loads(value)
            except:
                pass
            try:
                return ast.literal_eval(value)
            except:
                pass
        return as_type(value) if as_type else value

    @staticmethod
    def parse_time_delta(value):
        if isinstance(value, timedelta):
            return value
        if value is not None:
            value = str(value)
            intervals = re.split('[(days, ):]+', value)
            if len(intervals) >= 3:
                d = float(intervals[0]) if len(intervals) == 4 else 0.0
                s = float(intervals[-1])
                m = float(intervals[-2])
                h = float(intervals[-3])
                value = timedelta(hours=h, minutes=m, seconds=s, days=d)
        return value

    @staticmethod
    def parse_yaml_json(data, data_type="json"):
        if not data:
            return {}
        try:
            if data_type == 'json':
                return json.loads(data)
            elif data_type in ['yml', 'yaml']:
                return yaml.load(StringIO(data))
        except (JSONDecodeError, ScannerError, ValueError, AttributeError) as e:
            raise ConfigParsingException("Error parsing config from data: ", e)
        raise ConfigParsingException("Format not allowed: " + data_type)

    @staticmethod
    def correct_path(path):
        path = re.split('[/\\\\]+', path)
        return os.sep.join(path)

    @staticmethod
    def decode(text, lower=False):
        if not text:
            return
        try:
            text = text.decode()
        except:
            pass

        text = str(text).strip()
        return text.lower() if lower else text

    @staticmethod
    def compare_str(a, b):
        return Parser.decode(a, True) == Parser.decode(b, True)



class ConfigParsingException(Exception):
    __name__ = "ConfigParsingException"

    def __init__(self, message, error=None):
        Exception.__init__(self)
        self.args = (message,)
        self.message = message
        self.error = error
