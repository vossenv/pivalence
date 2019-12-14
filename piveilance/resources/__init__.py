import os
import sys
from os.path import dirname, realpath, join

__name__ = dirname(__file__).split(os.sep)[-1]


def get_resource_dir():
    if getattr(sys, 'frozen', False):
        return join(sys._MEIPASS, __name__)
    else:
        return dirname(realpath(__file__))


def get_resource(name):
    return join(get_resource_dir(), name)
def get_image(name):
    return join(get_resource_dir(), "image",  name)