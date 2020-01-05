import logging
import logging.config
import os
import re
import sys
from collections import UserDict, Mapping
from copy import deepcopy
from os import makedirs
from os.path import realpath

import yaml

from piveilance.util import parse_type, correct_path, decode, as_list, parse_exception


class Config(UserDict):

    def __init__(self, data, merge_env=False):
        super(Config, self).__init__(data)
        if merge_env:
            self.env_overrides()

    def get_sub_config(self, name):
        try:
            config = self if name else {}
            for k in as_list(name):
                config = config[k]
        except KeyError as e:
            raise ValueError("Subkey does not exist: " + str(e))
        return Config(config)

    def get_as(self, name, default=None, required=False, as_type=None):
        val = self.get(name, default)
        if required and not val:
            raise AssertionError("Value for " + name + " required but not given")
        return parse_type(val, as_type) if as_type else val

    def get_bool(self, name, default=False, required=False):
        val = self.get_as(name, default, required)
        return str(val).lower() in ['true', '1']

    def get_string(self, name, default=None, required=False):
        return self.get_as(name, default, required, str)

    def get_int(self, name, default=None, required=False):
        return self.get_as(name, default, required, int)

    def get_float(self, name, default=None, required=False):
        return self.get_as(name, default, required, float)

    def get_list(self, name, default=None, required=False):
        return self.get_as(name, default, required, list)

    def get_dict(self, name, default=None, required=False):
        return self.get_as(name, default, required, dict)

    def merge(self, update):
        self.merge_dict(self.data, update)

    def get_path(self, name, default=None, required=False):
        raw = self.get_as(name, default, required)
        return os.sep.join(re.split('[/\\\\]+', raw)) if raw else None

    def load_data_for_keys(self, parent, dir=''):
        for r, path in parent.items():
            if path.split('.')[-1].lower() in ['yml', 'yaml']:
                parent[r] = self.load_yaml(os.path.join(dir, path))
            else:
                parent[r] = os.path.join(dir, path)

    def env_overrides(self, key="cfg."):
        overrides = {}
        reduced = {decode(k, True): decode(v, True) for k, v in os.environ._data.items() if decode(k, True)}
        reduced = {k.lstrip(key): v for k, v in reduced.items() if k.startswith(key)}

        for k, v in reduced.items():
            entry = Config.make_dict(k.split("."), v)
            Config.merge_dict(overrides, entry)
        Config.merge_dict(self.data, overrides)

    @classmethod
    def from_yaml(cls, props_file, merge_env=False):
        return Config(cls.load_yaml(props_file), merge_env)

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


class ConfigLoader:

    def __init__(self, path):
        self.config = Config.from_yaml(path)

    def loadGlobalConfig(self):

        globalConfig = Config({})
        globalConfig['id'] = self.config.get('globalConfig', 'default')
        globalConfig['configurations'] = self.get_iter_as_dict('configurations', 'id', required=True)
        globalConfig['cameras'] = self.get_iter_as_dict('cameras', 'id', required=True)
        globalConfig['generators'] = self.get_iter_as_dict('generators', 'id', required=True)
        globalConfig['views'] = self.get_iter_as_dict('views', 'id', required=True)
        globalConfig['layouts'] = self.get_iter_as_dict('layouts', 'id', required=True)
        return globalConfig

    def get_iter_as_dict(self, name, keyname, default=None, required=False):

        value = self.config.get(name, default)
        if not value and required:
            raise ValueError("'{}': config cannot be empty.".format(name))

        try:
            return {i[keyname]: i for i in value}
        except KeyError:
            raise ValueError("Invalid key attribute for '{}': '{}'".format(name, keyname))


class FormattedDumper(yaml.Dumper):
    @classmethod
    def options(cls):
        return {
            'Dumper': FormattedDumper,
            'default_flow_style': False,
            'sort_keys': False
        }

    def increase_indent(self, flow=False, indentless=False):
        return super(FormattedDumper, self).increase_indent(flow, False)

    @staticmethod
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, FormattedDumper.str_presenter)


class Logging:
    level = 20

    @classmethod
    def init_logger(cls, logging_config, level=logging.INFO):
        cls.level = logging.getLevelName(level)
        with open(logging_config) as cfg:
            config = yaml.safe_load(cfg)

        log_dirs = {}
        for k, h in config['handlers'].items():
            filename = h.get('filename')
            if filename:
                filename = correct_path(filename)
                h['filename'] = filename
                log_dir = os.path.dirname(filename)
                makedirs(log_dir, exist_ok=True)
                log_dirs[k] = realpath(log_dir)
        logging.config.dictConfig(config)
        return log_dirs

    @classmethod
    def get_logger(cls, name='main'):
        current = logging.getLoggerClass()
        logging.setLoggerClass(PiLogger)
        custom = logging.getLogger(name)
        logging.setLoggerClass(current)
        custom.setLevel(cls.level)
        return custom


class PiLogger(logging.Logger):

    def __init__(self, name):
        logging.Logger.__init__(self, name)
        self.logger = super(PiLogger, self)

    def exc_detail(self, e, extra_msg='', chain=None):
        errors = []
        if chain:
            errors.extend([parse_exception(e) for e in as_list(chain)])
        errors.append(parse_exception(e, extra_msg))
        for e in errors:
            self.error("-----------------------")
            self.log_list(e, logging.ERROR)
            self.error("-----------------------")

    def log_list(self, list, level=logging.INFO):
        list = as_list(list)
        for l in list:
            super().log(level, l)

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        super()._log(level, msg, args, exc_info=None, extra=None, stack_info=False)
        sys.stdout.flush()
        for h in logging.getLogger().handlers:
            h.flush()
