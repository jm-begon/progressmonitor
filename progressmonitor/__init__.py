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
    Operating under-the-hood, the impact on the calling code is minimal.
    2. :func:`monitor_function`: a configurable decorator for functions.
    The monitoring is done on the whole function and the impact can be as 
    small as using the Python decorator facility.
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
iterators/generators. It indicates when (at which iterations) a event must
be sent to the listeners.

See the :mod:`notifrules` module for more information.

Hooks
-----
Hooks concerned all types of monitoring. It is the mechanism through which
listeners register their interest to receive monitoring events. Each kind of
monitoring only provides room for one hook. However, a 
:class:`ProgressListener` is provided so as to multiplex events.

Hooks are assumed to be provided through factory functions so as to be 
parametrizable if need be. 

The :mod:`hook` module provides many such factories whose hook return a string.
Those need an encapsulating hook so as to dispose of the string. The built-in
mechanism uses callback functions.

These hooks can be combined in two ways:
    - A decorator :func:`add_` is provided so as to stack string hooks.
    - The :func:`formated_hook_factory` allows to format a message using
    other hooks. This approach is more flexible and more powerful (beware
    of key collision, though).

Callback
--------
The callbacks concern all types of monitoring relying on string hooks. They
are responsible for disposing of the string yielded by the hooks.

See :mod:`callback` for more information.

Factory
-------
The :mod:`Factory` is concerned by providing factories function for 


Fallbacks
---------
A fallback mechanism is provided in the form of decorator for the notification
rules, the hooks and possibly the callbacks: in case of insufficient parameters
for the corresponding factory, an other is called in it stead. This mechanism
is transparent to the user but may be logged (see Logging section).


Configuration
-------------
So as to minimize further the impact on buiseness code, it is possible
to preconfigure monitors somewhat alike to the logging configuration.
In particular, the inheritance/hierarchical structure is present so as to ease
configuration. That is, a monitor named "foo.bar" inherit the configuration
of monitor "foo" (provided it exists).

Configuration rely on :func:`formated_hook`, meaning that it is reserved
for string hook composition. Three functions are provided:
    - :func:`get_monitor` for iterators/generators monitoring
    - :func:`monitor_with` for function monitoring (use it as a decorator)
    - :func:`code_monitor` for code block monitoring (use it as a context 
    manager in a `with` statement)

Configuration may be done several times but overlaps will be overridden.

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

By default, the logging is turned off by setting a logging.NullHandler
as handler for the library's root logger ('progressmonitor'). To enable those
messages, another handler must be set for the library's root logger. 
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "08 January 2015"


from .monitor import (monitor_generator, monitor_function, monitor_this, 
                      monitor_code, CodeMonitor)

__all__ = ["monitor_generator", "monitor_function", "monitor_this", 
           "monitor_code", "CodeMonitor"]

import logging
logging.getLogger('progressmonitor').addHandler(logging.NullHandler())
