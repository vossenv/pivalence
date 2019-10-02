from collections import UserDict, Mapping
from copy import deepcopy
import yaml


class Config(UserDict):

    def __init__(self, *args):
        super(Config, self).__init__(*args)

    def get_config(self, name):
        return Config(self.get(name, {}))

    def get_type(self, name, default=None, as_type=None):
        return as_type(self.get(name, default))

    def merge(self, update):
        self.merge_dict(self.data, update)

    @classmethod
    def from_yaml(self, props_file):
        with open(props_file, 'r') as props:
            return Config(yaml.safe_load(props))

    @staticmethod
    def merge_dict(d1, d2, immutable=True):
        """
        # Combine dictionaries recursively
        # preserving the originals
        # assumes d1 and d2 dictionaries!!
        :param d1: original dictionary
        :param d2: update dictionary
        :return:
        """

        if not d1:
            return {} if not d2 else d2
        elif not d2:
            return {} if not d1 else d1        

        _d1 = deepcopy(d1) if immutable else d1

        for k in d2:

            # if _d1 and d2 have dict for k, then recurse
            # else assign the new value to _d1[k]
            if (k in _d1 and isinstance(_d1[k], Mapping)
                    and isinstance(d2[k], Mapping)):
                Config.merge_dict(_d1[k], d2[k], False)
            else:
                _d1[k] = d2[k]
        return _d1


