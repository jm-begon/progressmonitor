# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"


import time
import os
import getpass
import platform
try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread

from .util import (format_duration)
from .formatter import (string_formatter_factory, host_formatter_factory, 
                        processid_formatter_factory, 
                        threadname_formatter_factory, 
                        taskname_formatter_factory)



# ========================== LISTENER CLASS ========================== #

class ProgressListener(object):

    def __init__(self):
        self._hooks = []

    def add_hook(self, hook):
        self._hooks.append(hook)

    def hook(self, task, exception=None, **kwargs):
        for hook in self._hooks:
            hook(task, exception, **kwargs)

    def __call__(self, task, exception=None, **kwargs):
        self.hook(task, exception, **kwargs)




# ============================= CALLBACK HOOKS =============================== #

def callback_hook_factory(callback, formatter):
    def callback_hook(task, exception=None, **kwargs):
        callback(formatter(task, exception, **kwargs))
    return callback_hook

def set_callback(callback):

    def callback_hook(string_hook):
        def apply_hook(task, exception=None, **kwargs):
            last_com = task.is_completed or exception is not None
            message = string_hook(task, exception, **kwargs)
            callback(message, last_com)
            return message 
        return apply_hook
    return callback_hook


def formated_hook_factory(callback, format_str, format_mapper):

    formatter = string_formatter_factory(format_str, format_mapper)

    @set_callback(callback)
    def formated_hook(task, exception=None, **kwargs):
        return formatter(task, exception, **kwargs)

    return formated_hook

# ------------------------ for functions ------------------------------- #

def report_hook_factory(callback, format_result=str, format_timestamp=time.ctime,
                        subsec_precision=2):

    layout = """Meta
====
Host: {$host}
Pid: {$pid}
Thread: {$thread}
Task name: {$task}

Function
========
Name: {_$fname}
Args: {_$fargs}
Kwargs: {_$fkwargs}

Result
======
{_$fresult}

Exception
=========
{_$except}

Time
====
Started: {_$start}
Duration : {_$duration}
    """
    fillin = dict()


    def report_hook(task, exception=None, **kwargs):
        # On end only
        if task.is_completed or exception is not None:
            # Fill in the meta
            fillin["$host"] = host_formatter_factory()(task, exception, 
                                                       **kwargs)
            fillin["$pid"] = processid_formatter_factory()(task, exception, 
                                                           **kwargs)
            fillin["$thread"] = threadname_formatter_factory()(task, exception, 
                                                               **kwargs)
            fillin["$task"] = taskname_formatter_factory()(task, exception, 
                                                           **kwargs)

            # Fill in the function part
            fillin["_$fname"] = kwargs["monitored_func"]
            fillin["_$fargs"] = kwargs["monitored_args"]
            fillin["_$fkwargs"] = kwargs["monitored_kwargs"]

            # Fill in the results
            fillin["_$fresult"] = format_result(kwargs["monitored_result"])

            # Fill in the exception
            if exception is None:
                fillin["_$except"] = "None"
            else:
                fillin["_$except"] = str(exception)

            # Fill in time
            fillin["_$start"] = format_timestamp(task.timestamp)
            fillin["_$duration"] = format_duration(task.duration, 
                                                   subsec_precision)

            callback(layout.format(**fillin))

    return report_hook




