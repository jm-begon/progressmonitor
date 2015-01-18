# -*- coding: utf-8 -*-
"""
Progress monitor
================
Progress monitor is a toolkit for monitoring progress on time intensive tasks.

It aims at giving flexible tools for monitoring progress with the least
possible buiseness code invasion.

It features three main functionalities (:mod:`monitor`)
    1. :func:`monitor_generator`: a highly configurable, decorator for 
    `generator`s which allows to monitor progresses of iterative tasks. 
    Operating under-the-hood, the impact on the business code is minimal.
    2. :func:`monitor_function`: a configurable decorator for functions.
    The monitoring is done on the whole function and the impact on the 
    business can be as small as using the Python decorator facility.
    3. :func:`monitor_code` (or :class:`CodeMonitor`): a configurable 
    context manager for monitoring a block of code.

Aside from that module, the remaining of the code is dedicated to 
    - predifined *configuring* functions for the monitorings (notification
    rules, hooks, callbacks, fallback mechanism, etc.).
    - helper code for configuring *faster* and with even *less monitoring code 
    intrusion* in buiseness code (factories, configuration).

Main components
===============

Notifcation rules
-----------------
The notification rules concerned the :func:`monitor_generator` for 
iterators/generators. It indicates when (i.e. at which iterations) a event must
be sent to the listeners.

For function/code monitoring, only two events are issued:
    1. At the task's creation
    2. At the completion of the function/piece of code or if an exception 
    occured

See the :mod:`rule` module for more information.

Hooks
-----
Hooks concerned all types of monitoring. It is the mechanism through which
listeners register their interest to receive monitoring events. Each kind of
monitor only provides room for one hook. However, a 
:class:`ProgressListener` is provided in order to multiplex events.

Hooks are assumed to be provided through factories so as to be stateful, 
parametrizable if need be and provide an homogenous building mechanism.

The hooks provided by this library are mainly using callback functions to
digest formatted results provided by formatters.

See :mod:`hook` for more information.

Formatters
----------
Formatters take notification messages as input and output a string based on
their logic.

a meta formatter (:func:`string_formatter_factory`) is provided so as to
combine formatter. It relies on substitution of a given string filled
with placeholder. A system of shortcuts is implemeted:
    - For readibility reasons.
    - So that external formatters can be dynamically loaded in conjunction
    with the configuration scheme.

Formatters are assumed to be provided through factories so as to be stateful, 
parametrizable if need be and provide an homogenous building mechanism.

These formatters are usually used by hooks which transfert their output to
callback functions.

See :mod:`formatter` for more details.


Callbacks
---------
The callbacks concern all types of monitoring relying on formatters. They
are responsible for disposing of the string yielded by them.

See :mod:`callback` for more information.

Factories
---------
The :mod:`factory` is concerned by providing factories for monitors. They rely
on the formatting mechanism.



Fallbacks
---------
A fallback mechanism is provided in the form of decorator for the notification
rules, the formatters and possibly the callbacks: in case of insufficient 
parameters for the corresponding factory, an other is called in it stead. This 
mechanism is transparent to the user but may be logged (see Logging section).

**Warning**: The fallback mechanism does not implement cycle dectection. In
case of cycle, if none of the fallbacks are eligible, instead of breaking,
the fallback mechanism will run on an infinite loop. 

Reporting
---------
A special *on_completion* hook is provided for reporting on functions. it 
transferts a multiline string to a given callback function. This is typically
useful to get an email notification with some details when the main task is
done.

See :func:`report_hook_factory` for more information.


Configuration
-------------
To minimize further the impact on buiseness code, it is possible to preconfigure
monitors somewhat alike to the logging configuration.
In particular, the inheritance/hierarchical structure is present so as to ease
configuration. That is, a monitor named "foo.bar" inherit the configuration
of monitor "foo" (provided it exists).

Configuration can be conducted either from a dictionary :func:`dict_config` or
from a file :func:`file_config` holding directly the dictionary.

Configuration rely on :func:`formated_hook`, meaning that it is reserved
for format-callback hooks. 

It is possible to use formatters, callbacks and notification rules from outside
of this library. 

Configuration may be done several times but overlaps will be overwritten,
keeping the most recent one. This is also true with the preconfigured
formatter, callbacks and rules, so beware !

Business code can load a configuration via (:mod:`config`):
    - :func:`get_generator_monitor` for generators
    - :func:`get_function_monitor` for functions
    - :func:`get_code_monitor` for pieces of code
Two shortcuts are also provided:
    - :func:`monitor_with` for generators, functions and pieces of code
    - :func:`report_with` for reports
Note that with :func:`monitor_with` no default configuration can be provided
if the monitor does not (nor any ancestor) exist. Consequently a warning is 
issued (see Logging section) but the business code is otherwise left untouched 
(no monitoring is performed)


See :mod:`config` for more information.


Overhead
========
Monitoring progress imposes overhead on the buiseness code (computation and 
indirection). However, this overhead should be negligeable compare to the time
required by the monitored task.

Logging
=======
The progress monitor library resorts on logging for:
    - Warning in case of fallback ('progressmonitor.fallback')
    - Warning in case of unknown monitor name ('progressmonitor.config')

By default, the logging is turned off by setting a logging.NullHandler
as handler for the library's root logger ('progressmonitor'). To enable those
messages, another handler must be set for the library's root logger. 
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "08 January 2015"


from .monitor import (monitor_generator, monitor_function, monitor_code, 
                      CodeMonitor)

from .rule import (always_notif_rule_factory, periodic_rule_factory,
                   span_rule_factory, rate_rule_factory)

from .formatter import (taskname_formatter_factory, host_formatter_factory,
                        threadname_formatter_factory, 
                        processid_formatter_factory, 
                        nb_iterations_formatter_factory,
                        exception_formatter_factory,
                        progressbar_formatter_factory,
                        completion_formatter_factory,
                        elapsed_time_formatter_factory,
                        remaining_time_formatter_factory,
                        chunk_formatter_factory,
                        string_formatter_factory)
from .hook import (ProgressListener, callback_hook_factory, set_callback,
                   formated_hook_factory, report_hook_factory)

from .callback import (stdout_callback_factory, stderr_callback_factory, 
                       overwrite_callback_factory, logging_callback_factory,
                       store_till_end_callback_factory, multi_callback_factory)

from .factory import (monitor_generator_factory, report_factory, 
                      formated_code_monitoring)

from .util import (format_duration, format_size, call_with, fallback)


from .config import (get_config, get_monitor, parse_dict_config, 
                     parse_file_config)

__all__ = ["monitor", "monitor_this", "code_monitor", "report_this",
           "monitor_with", "report_with", "dict_config", "file_config",
           "monitor_generator", "monitor_function", "monitor_this", 
           "monitor_code", "CodeMonitor", "always_notif_rule_factory", 
           "periodic_rule_factory", "span_rule_factory", "rate_rule_factory",
           "taskname_formatter_factory", "host_formatter_factory",
           "threadname_formatter_factory", "processid_formatter_factory", 
           "nb_iterations_formatter_factory", "exception_formatter_factory",
           "progressbar_formatter_factory", "completion_formatter_factory",
           "elapsed_time_formatter_factory", "remaining_time_formatter_factory",
           "chunk_formatter_factory", "string_formatter_factory", 
           "ProgressListener", "callback_hook_factory", "set_callback",
           "formated_hook_factory", "report_hook_factory", 
           "stdout_callback_factory", "stderr_callback_factory", 
           "overwrite_callback_factory", "logging_callback_factory",
           "store_till_end_callback_factory", "multi_callback_factory",
           "format_duration", "format_size", "call_with", "fallback"]


from functools import partial
import logging
logging.getLogger('progressmonitor').addHandler(logging.NullHandler())


# ============================= SHORTCUTS =============================== #

def monitor(**kwargs):
    """
    Return a generator embedder.

    Parameters
    ----------
    see :func:`formated_monitoring`

    Return
    ------
    
    """
    return monitor_generator_factory(**kwargs)


def monitor_this(hook, task_name=None):
    """
    Decorator for :func:`monitor_function`

    @monitor_this(hook=hook, task_name=name)
    def foo():
        # compute stuff

    is equivalent to

    monitor_function(foo, hook=hook, task_name=name)

    Yes, it's that easy !
    """
    
    def apply_monitoring(function):
        return partial(monitor_function, function, hook, task_name)
    return apply_monitoring



def code_monitor(**kwargs):
    return formated_code_monitoring(**kwargs)


def report_this(**kwargs):
    return report_factory(**kwargs)

def monitor_with(monitor_name, **kwargs):
    return get_monitor(monitor_name, **kwargs)


def report_with(monitor_name, **kwargs):
    conf = get_config(monitor_name, **kwargs)
    return report_this(**conf)


def dict_config(config_dict):
    parse_dict_config(config_dict)

def file_config(config_file):
    parse_file_config(config_file)

