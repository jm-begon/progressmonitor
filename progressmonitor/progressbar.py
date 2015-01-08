# -*- coding: utf-8 -*-
"""
Progress bars for sys.stdout


Other progress bar libraries should be fairly easy to plug in. Have a look at:
    - http://thelivingpearl.com/2012/12/31/creating-progress-bars-with-python/
    - https://pypi.python.org/pypi/progressbar/2.2
    - http://code.activestate.com/recipes/475116/ 
    - https://github.com/ikame/progressbar


Note
----
Progress bars on stdout are fine as long as no other piece of code write to it
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import sys
from functools import partial
from string import Formatter

from .monitor import (monitor_progress, format_duration, rate_format_factory, 
                      span_chunk_format_factory, rate_chunk_format_factory,
                      span_notify_rule, rate_rule_and_nb_notifs, 
                      periodic_notify_rule, progressbar_formater, format_task, 
                      elapsed_time_formater, remaining_time_formater, 
                      exception_handler_formater, format_iteration, 
                      chunk_formater, format_from_string)

# ============================ HELPERS ============================ #
def overwrite_callback(stream=sys.stdout):
    string_length = [0]

    def overwrite(string, last_com=False):
        stream.write("\b"*string_length[0])
        stream.write(string)
        new_length = len(string)
        length_diff = string_length[0] - new_length
        if length_diff > 0:
            stream.write(" "*length_diff)
            stream.write("\b"*length_diff)
        string_length[0] = new_length
        if last_com:
            stream.write("\n")
        stream.flush()

    return overwrite


class Printer(object):

    def __init__(self, stream=sys.stdout):
        self.stream = stream

    def write(self, *strings):
        for string in strings:
            self.stream.write(string)

    def writeln(self, *strings):
        self.write(*strings)
        self.stream.write("\n")

    def move_left(self, n=1):
        self.stream.write("\b"*n)

    def flush(self):
        self.stream.flush()


# ========================== LIGHTWEIHGT PROGRESSBAR ========================== #


def span_progressbar(generator, span, printer=Printer()):
    number_length = [0]

    def hook(task, exception=None):
        progress = task.progress()
        if  progress == 0:
            # Setting up
            number_str = "0.0"
            number_length[0] = len(number_str)
            printer.write("Processing : iteration # ", number_str)
        else:
            if exception is not None:
                # Task aborted
                duration = format_duration(task.duration())
                printer.write("Aborted after ", duration)
                printer.writeln("(Reason(s):", exception.message, ")")

            else:
                printer.move_left(number_length[0])
                number_str = "%.2f" % progress
                number_length[0] = len(number_str)
                printer.write(number_str)
                if task.is_completed():
                    # Task completed
                    duration = format_duration(task.duration())
                    printer.writeln(" -- Done in ", duration)
        printer.flush()


    return partial(monitor_progress, generator=generator, hook=hook, 
                   should_notify=span_notify_rule(span))()


def rate_progressbar(generator, rate, printer=Printer(),
                     fill=".", blank=" ", error="x"):
    length = len(generator)
    rule, nb_iter = rate_rule_and_nb_notifs(rate, length)

    def hook(task, exception=None):
        if task.progress() == 0:
            # Setting up
            printer.write("Processing [", blank*nb_iter, "]")
            printer.move_left(nb_iter+1)
        else:
            if exception is not None:
                # Task aborted
                duration = format_duration(task.duration())
                printer.write(error, "] Aborted after ", duration)
                printer.writeln("(Reason(s):", exception.message, ")")
            else:
                printer.write(fill) 
                if task.is_completed():
                    # Task done
                    duration = format_duration(task.duration())
                    printer.writeln("] Done in ", duration)
        printer.flush()

    return partial(monitor_progress, generator=generator, hook=hook, 
                   should_notify=rule)()


# =========================== PROGRESSBAR FACTORY ============================ #

def remain_time_progressbar(generator, rate, decay_rate=0.1, 
                            callback=overwrite_callback(), *args, **kwargs):

    length = len(generator)

    rule, nb_notifs = rate_rule_and_nb_notifs(rate, length)

    hook = rate_format_factory(callback, length, nb_notifs, decay_rate, 
                               *args, **kwargs)

    return partial(monitor_progress, generator=generator, hook=hook, 
                   should_notify=rule)()

def chunck_progressbar(generator, chunk_size, total_size=None, 
                       rate=0.1, span=10, decay_rate=0.1, 
                       callback=overwrite_callback(), *args, **kwargs):

    try:
        length = len(generator)
        rule, nb_notifs = rate_rule_and_nb_notifs(rate, length)

        hook = rate_chunk_format_factory(callback,
                                         length,
                                         nb_notifs,
                                         chunk_size,
                                         total_size,
                                         decay_rate,
                                         *args,
                                         **kwargs)

        

    except (AttributeError, TypeError):

        hook = span_chunk_format_factory(callback, chunk_size, total_size,
                                         *args, **kwargs)
        rule = span_notify_rule(span)

    return partial(monitor_progress, generator=generator, hook=hook, 
                   should_notify=rule)()


def custom_progressbar(generator, 
                       format_str="{task} {progressbar} {time} {exception}",
                       rate=None,
                       span=None,
                       period=5,
                       decay_rate=0.1,
                       chunk_size=8192, total_size=None,
                       callback=overwrite_callback(),
                       *args, **kwargs):
    """
    rate : float (Default : 0.01)
        The rate at which the observer must be notified through the hook,
        expressed relatively to the number of iterations 
        (see `Notification recurrence`)
        For instance, a rate of 0.1 for a generator of 100 elements 
        means that the observer is notified every 10 iterations. 
        Note:
            - Set 0 to notified at each iteration
            - Cannot be used for generator with no :meth:`__len__` method
    span: int (Default : 10)
        The number of iterations before notifying the observer (see
        `Notification recurrence`)
        For instance, a span of 10 means that the observer is notified every
        10 iterations
    period : float (Default : 60.)
        The period at which the observer must be notified through the hook,
        expressed in second (see `Notification recurrence`)
        For instance, with a frequency of 5, the observer will have at 
        least 5 seconds between two consecutive calls of :func:`hook`.
        Note:
            - This indicates the minimum time between two calls

    Notification recurrence
    -----------------------
    The recurrence of notifications can be specified through three parameters:
        1. notification_rate : based on the ratio iteration/nb_interation
        2. notification_span : based on the number of iterations since the last 
        notification
        3. notification_period : based on the time since the last notification
    The actual recurrence mechanism follows this sequence: 
        - if notification_rate is set, it is used for generators with length 
        attribute (the two other are ignored)
        - elif notification_span is set,  is used and notification_period is i
        gnored
        - else notification_period is used
    One and only one mechanism is used for a given task
    """
    

    # Choosing the notification rule
    length = None
    try:
        length = len(generator)
    except (AttributeError, TypeError):
        pass

    # Notification mechanism
    if length is not None and rate is not None:
        rule, nb_notifs = rate_rule_and_nb_notifs(rate, length)
    elif span is not None:
        rule = span_notify_rule(span)
    else:
        rule = periodic_notify_rule(period)

    

    # Parsing format_str to get the sequence of formater
    formatters = Formatter()
    func_mapper = dict()

    for format_rule_tuple in formatters.parse(format_str):
        format_rule = format_rule_tuple[1]
        if format_rule == "task":
            func_mapper["task"] = format_task

        elif format_rule == "progressbar":
            if nb_notifs is None:
                raise ValueError("Rate is mandatory for 'progressbar' option. Rate also required the generator to have a length")
            func_mapper["progressbar"] = progressbar_formater(nb_notifs, 
                                                              *args, **kwargs)
        elif format_rule == "elapsed":
            func_mapper["elapsed"] = elapsed_time_formater(*args, **kwargs)

        elif format_rule == "time":
            if length is None:
                raise ValueError("Length is mandatory for 'time' option")
            func_mapper["time"] = remaining_time_formater(length, 
                                                          decay_rate, 
                                                          *args, **kwargs)
        elif format_rule == "exception":
            func_mapper["exception"] = exception_handler_formater(*args, 
                                                                  **kwargs)
        elif format_rule == "iteration":
            func_mapper["iteration"] = format_iteration
        elif format_rule == "chunk":
            func_mapper["chunk"] = chunk_formater(chunk_size, total_size)
        elif format_rule is None:
            pass
        else:
            raise ValueError("formatting rule '"+format_rule+"' not supported")

    # Building the hook
    hook = format_from_string(callback, format_str, func_mapper)

    return partial(monitor_progress, generator=generator, hook=hook, 
                   should_notify=rule)()


