import ast
import json
import os
import re
from collections import Mapping
from datetime import datetime, timedelta
from io import StringIO
from traceback import TracebackException

import yaml
from dateutil import parser


class ParseException(Exception):
    __name__ = "ParseException"

    def __init__(self, message, error=None):
        Exception.__init__(self)
        self.args = (message,)
        self.message = message
        self.error = error


class ImageManip():

    @classmethod
    def crop_direction(cls, image, amount, direction='center'):
        if direction == 'right':
            return ImageManip.crop(image, 0, 0, 0, amount)
        elif direction == 'hcenter':
            return ImageManip.crop(image, 0, amount / 2, 0, amount / 2)
        elif direction == 'vcenter':
            return ImageManip.crop(image, amount / 2, 0, amount / 2, 0)
        elif direction == 'left':
            return ImageManip.crop(image, 0, 0, 0, amount)
        elif direction == 'top':
            return ImageManip.crop(image, amount, 0, 0, 0)
        elif direction == 'bottom':
            return ImageManip.crop(image, 0, 0, amount, 0)
        elif direction == 'square':
            return ImageManip.crop(image, amount / 4, amount / 4, amount / 4, amount / 4)
        raise ValueError("Invalid direction: " + direction)

    @classmethod
    def crop(cls, image, top, left, bottom, right):
        w = image.width() - left - right
        h = image.height() - top - bottom
        return image.copy(left, top, w, h)

    @classmethod
    def cropCenter(cls, image, size):
        return cls.crop(image, size, size, size, size)


def parse_type(value, as_type):
    try:
        if as_type == bool:
            return parse_bool(value)
        elif as_type == tuple:
            return parse_tuple(value)
        elif as_type == list:
            return parse_list(value)
        elif as_type == dict:
            return parse_dict(value)
        elif as_type == timedelta:
            return parse_time_delta(value)
        elif as_type == datetime:
            return parse_datetime(value)
        elif as_type in ["json", "yaml"]:
            return parse_yaml_json(value)
        else:
            if value is None:
                return
            return as_type(value)
    except:
        raise TypeError("Error parsing '{0}' as type '{1}'".format(value, as_type))

def parse_tuple(value):
    if value is None:
        return
    value = "(" + value.replace("(","").replace(")","") + ")"
    return ast.literal_eval(value)

def parse_datetime(date):
    if isinstance(date, datetime):
        return date
    if not isinstance(date, str):
        return TypeError("Cannot parse date '{0}' from type: {1}".
                         format(str(datetime), str(type(datetime))))
    return parser.parse(date)


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


def parse_list(value):
    if isinstance(value, set):
        return list(value)
    else:
        return parse_collection(value, list)


def parse_dict(value):
    return parse_collection(value, dict)


def parse_collection(value, as_type):
    if value is None:
        return as_type()
    elif isinstance(value, as_type):
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
    return as_type(value)


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


def parse_yaml_json(data):
    if not data:
        return {}
    d = json_exc = yaml_exc = None
    try:
        d = json.loads(data)
    except Exception as e:
        json_exc = e
    try:
        d = yaml.load(StringIO(data))
    except Exception as e:
        yaml_exc = e
    if json_exc and yaml_exc:
        raise ParseException("Error parsing config from data", [json_exc, yaml_exc])
    elif not isinstance(d, Mapping):
        raise ParseException("Data is parseable but cannot be mapped into a dictionary")
    return d


def parse_exception(exc, extra_msg=''):
    if not exc:
        return []
    exc_list = exc
    if isinstance(exc, Exception):
        tbe = TracebackException(type(exc), exc, exc.__traceback__)
        exc_list = tbe.format()
    lines = []
    for l in exc_list:
        lines.extend(l.split('\n'))
    lines.append(extra_msg)
    return list(map(
        lambda x: x.strip(), filter(lambda x: x, lines)))


def correct_path(path):
    path = re.split('[/\\\\]+', path)
    return os.sep.join(path)


def timestamp(date=None):
    if date and not isinstance(date, datetime):
        return date
    return (date or datetime.now()).strftime('%Y_%m_%d-%H.%M.%S')


def displaytime(date=None):
    if date and not isinstance(date, datetime):
        return date
    return (date or datetime.now()).strftime('%Y/%m/%d %H:%M:%S')


def decode(text, lower=False):
    if not text:
        return
    try:
        text = text.decode()
    except:
        pass

    text = str(text).strip()
    return text.lower() if lower else text


def as_list(obj):
    if not obj:
        return []
    if isinstance(obj, list):
        return obj
    elif isinstance(obj, set):
        return list(obj)
    return [obj]


def intersection(lst1, lst2):
    # Use of hybrid method
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3


def compare_str(a, b):
    return decode(a, True) == decode(b, True)


def compareIter(a, b):
    return (len(a) == len(b) and
            {x in b for x in a} ==
            {x in b for x in a} ==
            {True})
