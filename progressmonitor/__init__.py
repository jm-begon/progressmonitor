# -*- coding: utf-8 -*-
"""
Progress monitor is a toolkit for monitoring progress on time intensive tasks.
It features three main functionalities (:mod:`monitor`)
    1. :func:`monitor_progress`: a highly configurable, decorator for 
    `generator`s which allows to monitor progresses of iterative tasks. 
    Operating under-the-hood, the impact on the calling code is minimal.
    2. :func:`monitor_function`: a configurable decorator for functions.
    The monitoring is done on the whole function and the impact can be as 
    small as using the Python decorator facility.
    3. :func:`monitor_code` (or :class:`CodeMonitor`): a configurable 
    context manager for monitoring a block of code

Aside from this module, the remaining of the code is dedicated to 
    - predifined *configuring* functions for the monitorings (notification
    rules, hooks, callbacks, fallback mechanism, etc.)
    - helper code for configuring *faster* and with even *less monitoring code 
    intrusion* in buiseness code (factories, configuration)




Logging note
------------
The progress monitor library resorts on logging for:
    - Warning in case of fallback ('progressmonitor.fallback')

By default, the logging is turned off by setting a logging.NullHandler
as handler for the library's root logger ('progressmonitor'). To enable those
messages, another handler must be set for the library's root logger. 
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "08 January 2015"


# from .monitor import (Task, ProgressableTask, monitor_progress,
# 					  format_duration, format_size, always_notify_rule)
# from .progressbar import span_progressbar, rate_progressbar

# __all__ = ["Task", "ProgressableTask", "monitor_progress", "format_duration", 
# 		   "format_size", "span_progressbar", "rate_progressbar", 
#            "always_notify_rule"]


import logging
logging.getLogger('progressmonitor').addHandler(logging.NullHandler())
