# -*- coding: utf-8 -*-
"""
Lightweight progress bars for sys.stdout


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
__date__ = "08 January 2015"

import sys
import math
from functools import partial

from .util import format_duration
from .monitor import monitor_progress
from .notifrules import rate_rule_factory, span_rule_factory





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
                   should_notify=span_rule_factory(span))()


def rate_progressbar(generator, rate, printer=Printer(),
                     fill=".", blank=" ", error="x"):
    length = len(generator)
    rule = rate_rule_factory(rate, length)
    nb_notifs = int(math.ceil(1./rate))

    def hook(task, exception=None):
        if task.progress() == 0:
            # Setting up
            printer.write("Processing [", blank*nb_notifs, "]")
            printer.move_left(nb_notifs+1)
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


