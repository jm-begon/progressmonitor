# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

import time
from functools import partial
from string import Formatter

from .util import call_with, nb_notifs_from_rate 
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

    # ---- Adding the format string ---- #
    kwargs["format_str"] = format_str

    # ---- Testing for length ---- #
    length = None
    try:
        length = len(generator)
        kwargs["length"] = length
        if "rate" in kwargs:
            nb_notifs = nb_notifs_from_rate(kwargs["rate"], length)
            kwargs["nb_notifs"] = nb_notifs

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
    

    # ---- Building the callback ---- #
    callback = call_with(callback_factory, kwargs)


    # ---- Building the final hook ---- #
    hook = report_hook_factory(callback, format_result, format_timestamp, 
                               subsec_precision)

    # ---- Naming the task ---- #
    task_name = kwargs.get("task_name", None)

    return partial(monitor_function, function, hook, task_name)

def report_factory(**kwargs):
    def embed_func(function):
        return report_monitor_factory(function=function, **kwargs)
    return embed_func


# ======================= CODE MONITORING FACTORY ======================== #

def formated_code_monitoring(format_str="{$elapsed} {$exception}",
                             formatter_factories=__formatter_factories__,
                             callback_factory=stdout_callback_factory, 
                             **kwargs):

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





