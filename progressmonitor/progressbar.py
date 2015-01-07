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
import math
from functools import partial

from .monitor import (monitor_progress, format_duration, rate_format_factory, 
                      span_chunk_format_factory, rate_chunk_format_factory)

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
                number_str = str(progress)
                number_length[0] = len(number_str)
                printer.write(number_str)
                if task.is_completed():
                    # Task completed
                    duration = format_duration(task.duration())
                    printer.writeln(" -- Done in ", duration)
        printer.flush()

    return partial(monitor_progress, generator=generator, hook=hook, 
                   notification_span=span, notification_rate=None, 
                   notification_period=None)()


def rate_progressbar(generator, rate, printer=Printer(),
                     fill=".", blank=" ", error="x"):
    length = len(generator)
    nb_iter = int(math.ceil(length*rate))

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
                   notification_rate=rate)()



def remain_time_progressbar(generator, rate, decay_rate=0.1, 
                            callback=overwrite_callback(), *args, **kwargs):

    hook = rate_format_factory(generator, callback, rate, decay_rate, 
                               *args, **kwargs)

    return partial(monitor_progress, generator=generator, hook=hook, 
                   notification_rate=rate)()

def chunck_progressbar(generator, chunk_size, total_size=None, 
                       rate=0.1, span=10, decay_rate=0.1, 
                       callback=overwrite_callback(), *args, **kwargs):

    try:
        length = len(generator)
        hook = rate_chunk_format_factory(generator,
                                         callback,
                                         chunk_size,
                                         total_size,
                                         rate,
                                         decay_rate,
                                         *args,
                                         **kwargs)

        notif_rate = rate

    except (AttributeError, TypeError):

        hook = span_chunk_format_factory(callback, chunk_size, total_size,
                                         *args, **kwargs)

        notif_rate = None

    return partial(monitor_progress, generator=generator, hook=hook, 
                   notification_rate=notif_rate, notification_span=span)()

