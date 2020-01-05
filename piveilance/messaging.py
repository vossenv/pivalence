import logging
import sys
from traceback import format_exception

from piveilance.config import Logging
from piveilance.util import parse_exception


class ErrorHandler:

    @classmethod
    def handle_thread_error(cls, e):
        sys.excepthook(type(e).__name__, e, e.__traceback__)

    @classmethod
    def excephook(cls, type, value, tb):
        list_err = parse_exception(format_exception(type, value, tb))
        Logging.get_logger().log_list(list_err, logging.ERROR)
