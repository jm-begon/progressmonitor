# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

from functools import partial
from string import Formatter

from .util import call_with, nb_notifs_from_rate
from .notifrules import (rate_rule_factory, span_rule_factory, 
                         periodic_rule_factory)
from .monitor import monitor_progress, monitor_function, monitor_code
from .hook import (fullbar_hook_factory, chunkbar_hook_factory, 
                   iterchunk_hook_factory, formated_hook_factory,
                   __hook_factories__)
from .callback import overwrite_callback_factory




# ====================== (PSEUDO) PROGRESSBAR FACTORY ======================= #

def remain_time_progressbar(generator, rate, decay_rate=0.1, 
                            callback=overwrite_callback_factory(), 
                            *args, **kwargs):

    length = len(generator)

    rule = rate_rule_factory(rate, length)


    hook = fullbar_hook_factory(callback, length, rate, decay_rate, 
                                *args, **kwargs)

    task_name = kwargs.get("task_name", None)

    return monitor_progress(generator, hook, task_name, rule)

def chunck_progressbar(generator, chunk_size, total_size=None, 
                       rate=0.1, span=10, decay_rate=0.1, 
                       callback=overwrite_callback_factory(), 
                        *args, **kwargs):

    task_name = kwargs.get("task_name", None)

    try:
        length = len(generator)
        
        rule = rate_rule_factory(rate, length)

        hook = chunkbar_hook_factory(callback, length, rate,
                                     chunk_size, total_size, decay_rate,
                                     *args, **kwargs)

        

    except (AttributeError, TypeError):

        hook = iterchunk_hook_factory(callback, chunk_size, total_size,
                                      *args, **kwargs)
        rule = span_rule_factory(span)

    return monitor_progress(generator, hook, task_name, rule)



# =========================== MONITORING FACTORY ============================ #

def formated_monitoring(generator, 
                        format_str="{$task} {$progressbar} {$time} {$exception}",
                        hook_factories=__hook_factories__,
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
        function = hook_factories[p_holder]
        format_mapper[p_holder] = call_with(function, kwargs)


    # ---- Building the final hook ---- #

    hook = formated_hook_factory(callback, format_str, format_mapper)

    # ---- Naming the task ---- #
    task_name = kwargs.get("task_name", None)

    return monitor_progress(generator, hook, task_name, rule)



def default_monitoring(generator, 
                       format_str="{task} {progressbar} {time} {exception}",
                       rate=0.1, span=10, period=5,
                       hook_factories=__hook_factories__,
                       callback_factory=overwrite_callback_factory,
                       **kwargs):

    # Choosing the notification rule
    if rate is not None:
        rule_factory = rate_rule_factory
        kwargs["rate"] = rate
    if span is not None:
        kwargs["span"] = span
        if rate is None:
            rule_factory = span_rule_factory
    if period is not None:
        kwargs["period"] = period
        if rate is None and span is None:
            rule_factory = periodic_rule_factory
    if rate is None and span is None and period is None:
        raise AttributeError("One of {rate, span, period} must be set")

    return formated_monitoring(generator=generator,
                               format_str=format_str,
                               hook_factories=hook_factories,
                               rule_factory=rule_factory,
                               callback_factory=callback_factory, 
                               **kwargs)




def monitor(**kwargs):

    def embed(generator):
        return formated_monitoring(generator=generator, **kwargs)
    return embed


# ======================= FUNCTION MONITORING FACTORY ======================== #

def formated_function_monitoring(function, 
                                 format_str="{$fname} {$elapsed} {$exception}",
                                 hook_factories=__hook_factories__,
                                 callback_factory=overwrite_callback_factory, 
                                 **kwargs):

    # ---- Adding the format string ---- #
    kwargs["format_str"] = format_str


    # ---- Building the callback ---- #
    callback = call_with(callback_factory, kwargs)

    # ---- Building the format_mapper ---- #
    format_mapper = dict()
    formatters = Formatter()
    for _, p_holder, _, _ in formatters.parse(format_str):
        function_ = hook_factories[p_holder]
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


# ======================= CODE MONITORING FACTORY ======================== #

def formated_code_monitoring(format_str="{$elapsed} {$exception}",
                                 hook_factories=__hook_factories__,
                                 callback_factory=overwrite_callback_factory, 
                                 **kwargs):

    # ---- Adding the format string ---- #
    kwargs["format_str"] = format_str


    # ---- Building the callback ---- #
    callback = call_with(callback_factory, kwargs)

    # ---- Building the format_mapper ---- #
    format_mapper = dict()
    formatters = Formatter()
    for _, p_holder, _, _ in formatters.parse(format_str):
        function_ = hook_factories[p_holder]
        format_mapper[p_holder] = call_with(function_, kwargs)



    # ---- Building the final hook ---- #

    hook = formated_hook_factory(callback, format_str, format_mapper)

    # ---- Naming the task ---- #
    task_name = kwargs.get("task_name", None)

    return monitor_code(hook, task_name)


