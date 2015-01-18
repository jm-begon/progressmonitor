# -*- coding: utf-8 -*-
"""
Module :mod:`factory` contains a set of factories for building `monitor`
with :func:`formated_hook_factory`
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

import time
from functools import partial
from string import Formatter

from .util import call_with 
from .rule import rate_rule_factory
from .monitor import monitor_generator, monitor_function, monitor_code
from .hook import formated_hook_factory, report_hook_factory
from .formatter import __formatter_factories__
from .callback import (overwrite_callback_factory, stdout_callback_factory)




# =========================== MONITORING FACTORY ============================ #

def formated_monitoring(generator, 
                        format_str="{$task} {$progressbar} {$time} {$exception}",
                        formatter_factories=__formatter_factories__,
                        rule_factory=rate_rule_factory,
                        callback_factory=overwrite_callback_factory, 
                        **kwargs):
    """
    Build a generator monitor with a :func:`formated_hook_factory` 

    Parameters
    ----------
    generator : iterator/generator
        The generator to monitor
    format_str : str (Default : "{$task} {$progressbar} {$time} {$exception}")
        The formatting string
    formatter_factories : dict (Default : __formatter_factories__)
        A mapping placeholder - :func:`formatter_factory` for substitution
        in the `format_str`
    rule_factory : :func:`rule_factory` (Default : rate_rule_factory)
        The rule to use
    callback_factory : :func:`callback_factory`
        The callback to use
    kwargs : dict
        Additionnal arguments for the factories

    Return
    ------
    :func:`monitor_generator`
    """

    # ---- Adding the format string ---- #
    kwargs["format_str"] = format_str

    # ---- Testing for length ---- #
    length = None
    try:
        length = len(generator)
        kwargs["length"] = length
    except (AttributeError, TypeError):
        pass

    # ---- Choosing the rule ---- #
    rule = call_with(rule_factory, kwargs)

    # ---- Building the callback ---- #
    callback = call_with(callback_factory, kwargs)

    # ---- Building the format_mapper ---- #
    format_mapper = dict()
    formatters = Formatter()
    for _, p_holder, _, _ in formatters.parse(format_str):
        function = formatter_factories[p_holder]
        format_mapper[p_holder] = call_with(function, kwargs)


    # ---- Building the final hook ---- #

    hook = formated_hook_factory(callback, format_str, format_mapper)

    # ---- Naming the task ---- #
    task_name = kwargs.get("task_name", None)

    return monitor_generator(generator, hook, task_name, rule)


def monitor_generator_factory(**kwargs):
    """
    Build a generator monitor with a :func:`formated_hook_factory` 

    Parameters
    ----------
    kwargs : dict
        Arguments:
            format_str : str
                The formatting string
            formatter_factories : dict
                A mapping placeholder - :func:`formatter_factory` 
                for substitutionin the `format_str`
            rule_factory : :func:`rule_factory`
                The rule to use
            callback_factory : :func:`callback_factory`
                The callback to use
            other factory arguments

    Return
    ------
    A function which expects an iterator/generator to turn it into
    a monitored generator
    """
    def embed_gen(generator):
        return formated_monitoring(generator=generator, **kwargs)
    return embed_gen



# ======================= FUNCTION MONITORING FACTORY ======================== #
# -----------------------         All functions         ---------------------- #

def formated_function_monitoring(function, 
                                 format_str="{$fname} {$elapsed} {$exception}",
                                 formatter_factories=__formatter_factories__,
                                 callback_factory=stdout_callback_factory, 
                                 **kwargs):
    """
    Build a function monitor with a :func:`formated_hook_factory` 

    Parameters
    ----------
    function : callable
        The function to monitor
    format_str : str (Default : "{$task} {$progressbar} {$time} {$exception}")
        The formatting string
    formatter_factories : dict (Default : __formatter_factories__)
        A mapping placeholder - :func:`formatter_factory` for substitution
        in the `format_str`
    rule_factory : :func:`rule_factory` (Default : rate_rule_factory)
        The rule to use
    callback_factory : :func:`callback_factory`
        The callback to use
    kwargs : dict
        Additionnal arguments for the factories

    Return
    ------
    :func:`monitor_function`
    """

    # ---- Adding the format string ---- #
    kwargs["format_str"] = format_str


    # ---- Building the callback ---- #
    callback = call_with(callback_factory, kwargs)

    # ---- Building the format_mapper ---- #
    format_mapper = dict()
    formatters = Formatter()
    for _, p_holder, _, _ in formatters.parse(format_str):
        function_ = formatter_factories[p_holder]
        format_mapper[p_holder] = call_with(function_, kwargs)



    # ---- Building the final hook ---- #

    hook = formated_hook_factory(callback, format_str, format_mapper)

    # ---- Naming the task ---- #
    task_name = kwargs.get("task_name", None)

    return partial(monitor_function, function, hook, task_name)


def monitor_function_factory(**kwargs):
    """
    Build a function monitor with a :func:`formated_hook_factory` 

    Parameters
    ----------
    kwargs : dict
        Arguments:
            format_str : str
                The formatting string
            formatter_factories : dict
                A mapping placeholder - :func:`formatter_factory` 
                for substitutionin the `format_str`
            rule_factory : :func:`rule_factory`
                The rule to use
            callback_factory : :func:`callback_factory`
                The callback to use
            other factory arguments

    Return
    ------
    A function which expects a function to turn it into
    a monitored function
    """
    def embed_func(function):
        return formated_function_monitoring(function=function, **kwargs)
    return embed_func



# -----------------------         Reports         ---------------------- #

def report_monitor_factory(function, 
                           callback_factory=stdout_callback_factory,
                           format_result=str,
                           format_timestamp=time.ctime,
                           subsec_precision=2,
                           **kwargs):
    
    """
    Build a function monitor with a :func:`report_hook_factory` 

    Parameters
    ----------
    function : callable
        The function to monitor
    callback_factory : :func:`callback_factory` (Default : 
    stdout_callback_factory)
        The callback to use
    format_result : callable (Default : str)
        A function which transforms the result of the function into a string
    format_timestamp : callable (Default : time.ctime)
        A function which transforms the Unix epoch into a date+time string
    subsec_precision : int (Default : 2)
        The number of decimal digits for the second in the time formatting
    kwargs : dict
        Additionnal arguments for the factories

    Return
    ------
    :func:`monitor_function`
    """
    # ---- Building the callback ---- #
    callback = call_with(callback_factory, kwargs)


    # ---- Building the final hook ---- #
    hook = report_hook_factory(callback, format_result, format_timestamp, 
                               subsec_precision)

    # ---- Naming the task ---- #
    task_name = kwargs.get("task_name", None)

    return partial(monitor_function, function, hook, task_name)

def report_factory(**kwargs):
    """
    Build a function monitor with a :func:`report_hook_factory` 

    Parameters
    ----------
    kwargs : dict
        Arguments:
            callback_factory : :func:`callback_factory`
                The callback to use
            format_result : callable
                A function which transforms the result of the function into
                 a string
            format_timestamp : callable 
                A function which transforms the Unix epoch into a date+time 
                string
            subsec_precision : int
                The number of decimal digits for the second in the time 
                formatting
            Additionnal arguments for the factories

    Return
    ------
    A function which expects a function to turn it into
    a monitored function
    """
    def embed_func(function):
        return report_monitor_factory(function=function, **kwargs)
    return embed_func


# ======================= CODE MONITORING FACTORY ======================== #

def formated_code_monitoring(format_str="{$elapsed} {$exception}",
                             formatter_factories=__formatter_factories__,
                             callback_factory=stdout_callback_factory, 
                             **kwargs):
    """
    Build a function monitor with a :func:`formatted_hook_factory` 

    Parameters
    ----------
    function : callable
        The function to monitor
    format_str : str (Default : "{$elapsed} {$exception}")
        The formatting string
    formatter_factories : dict (Default : __formatter_factories__)
        A mapping placeholder - :func:`formatter_factory` for substitution
        in the `format_str`
    rule_factory : :func:`rule_factory` (Default : rate_rule_factory)
        The rule to use
    callback_factory : :func:`callback_factory` (Default : 
    stdout_callback_factory)
        The callback to use
    kwargs : dict
        Additionnal arguments for the factories

    Return
    ------
    :func:`code_function`
    """
    # ---- Adding the format string ---- #
    kwargs["format_str"] = format_str


    # ---- Building the callback ---- #
    callback = call_with(callback_factory, kwargs)

    # ---- Building the format_mapper ---- #
    format_mapper = dict()
    formatters = Formatter()
    for _, p_holder, _, _ in formatters.parse(format_str):
        function_ = formatter_factories[p_holder]
        format_mapper[p_holder] = call_with(function_, kwargs)



    # ---- Building the final hook ---- #

    hook = formated_hook_factory(callback, format_str, format_mapper)

    # ---- Naming the task ---- #
    task_name = kwargs.get("task_name", None)

    return monitor_code(hook, task_name)





