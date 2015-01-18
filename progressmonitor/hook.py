# -*- coding: utf-8 -*-
"""
Module :mod:`hook` contains hook functions. They have the form
    Parameters
    ----------
    task : :class:`Task`
        The monitored task
    exception : Exception (Default : None)
        The exception if one occured (None otherwise)
    Return
    ------
    None

Hooks are assumed to be provided through factories so as to be stateful, 
parametrizable if need be and provide an homogenous building mechanism.

Hooks rely on callbacks which are of the form
    Parameters
    ----------
    string : str
        The string to register somewhere
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
    """
    ================
    ProgressListener
    ================
    A :class:`ProgressListener` can register severals hooks on a monitor
    """

    def __init__(self):
        self._hooks = []

    def add_hook(self, hook):
        """
        Add the given hook

        Parameters
        ----------
        hook : `hook` function
            The hook to register
        """
        self._hooks.append(hook)

    def hook(self, task, exception=None):
        """
        hook function

        Parameters
        ----------
        task : :class:`Task`
            The task to format
        exception : Exception (Default : None)
            The exception if one occured (None otherwise)
        """
        for hook in self._hooks:
            hook(task, exception)

    def __call__(self, task, exception=None):
        """
        hook function
        
        Parameters
        ----------
        task : :class:`Task`
            The task to format
        exception : Exception (Default : None)
            The exception if one occured (None otherwise)
        """
        self.hook(task, exception)




# ============================= CALLBACK HOOKS =============================== #

def callback_hook_factory(callback, formatter):
    """
    Hook factory which uses a formatter and send the result to a callback
    function.

    Parameters
    ----------
    callback : callable
        A :func:`callback` function to dispose of the string yielded by the 
        formatter
    formatter : callable
        A :func:`formatter` to treat

    Return
    ------
    :func:`callback_hook`
    """
    def callback_hook(task, exception=None):
        """
        func:`hook`

        uses a formatter and send the result to a callback
        function.

        Parameters
        ----------
        task : :class:`Task`
            The monitored task
        exception : Exception (Default : None)
            The exception if one occured (None otherwise)
        """
        callback(formatter(task, exception))
    return callback_hook

def set_callback(callback):
    """
    Set the given callback to formatter

    Parameters:
    -----------
    callback : :func:`callback`
        The callback to set on the formatter

    Usage
    -----
    Use it as a decorator:
    @set_callback(callback_func)
    def formatter():
        pass
    """

    def callback_hook(string_hook):
        def apply_hook(task, exception=None):
            last_com = task.is_completed or exception is not None
            message = string_hook(task, exception)
            callback(message, last_com)
            return message 
        return apply_hook
    return callback_hook


def formated_hook_factory(callback, format_str, format_mapper):
    """
    Return a hook which forward the string yielded by
    a :func:`format_string_formatter` through the given callback

    Parameters
    ----------
    callback : :func:`callback`
        The callback to set on the formatter
    format_str : str
        The formatting string with place holder to be replaced.
    format_mapper : dict
        The dictionary containing the mapping placeholder - formatter

    Return
    ------
    :func:`formated_hook`
    """

    formatter = string_formatter_factory(format_str, format_mapper)

    @set_callback(callback)
    def formated_hook(task, exception=None):
        """
        :func:`hook`

        Return
        ------
        string : str
            The formatted result
        """
        return formatter(task, exception)

    return formated_hook

# ------------------------ for functions ------------------------------- #

def report_hook_factory(callback, format_result=str, format_timestamp=time.ctime,
                        subsec_precision=2):
    """
    Return a :func:`report_hook`. Use for function only

    Parameters
    ----------
    callback : :func:`callback`
        The callback through which to send the string
    format_result : callable (Default : str)
        A function which transforms the result of the function into a string
    format_timestamp : callable (Default : time.ctime)
        A function which transforms the Unix epoch into a date+time string
    subsec_precision : int (Default : 2)
        The number of decimal digits for the second in the time formatting

    Return
    ------
    :func:`report_hook`

    Warning
    -------
    The issue string is multiline
    """

    layout = """Meta
====
Host: {$host}
Pid: {$pid}
Thread: {$thread}
Task name: {$task}

Function
========
Name: {_$fname}
doc: {_$doc}
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


    def report_hook(task, exception=None):
        """
        func:`hook` which produces a report of the function.

        Parameters
        ----------
        task : :class:`Task`
            The monitored task
        exception : Exception (Default : None)
            The exception if one occured (None otherwise)

        Return
        ------
        string : str
            A multiline string report of the function
        """
        # On end only
        if task.is_completed or exception is not None:
            # Fill in the meta
            fillin["$host"] = host_formatter_factory()(task, exception)
            fillin["$pid"] = processid_formatter_factory()(task, exception)
            fillin["$thread"] = threadname_formatter_factory()(task, exception)
            fillin["$task"] = taskname_formatter_factory()(task, exception)

            # Fill in the function part
            func = task.function
            fillin["_$fname"] = func
            fillin["_$doc"] = "n/a"
            if hasattr(func, "__doc__"): 
                fillin["_$doc"] = func.__doc__
            fillin["_$fargs"] = task.args
            fillin["_$fkwargs"] = task.kwargs

            # Fill in the results
            fillin["_$fresult"] = task.result

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




