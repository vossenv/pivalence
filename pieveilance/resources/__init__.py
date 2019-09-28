
from os.path import dirname, realpath, join
import os
import sys

__name__ = dirname(__file__).split(os.sep)[-1]

def get_resource_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return dirname(realpath(__file__))

def get_resource(name):
    return join(get_resource_dir(), name)
