from os.path import dirname, realpath, join
import os

__name__ = dirname(__file__).split(os.sep)[-1]
resource_dir = dirname(realpath(__file__))


def get_resource(name):
    return join(resource_dir, name)
