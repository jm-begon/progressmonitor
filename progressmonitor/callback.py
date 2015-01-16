# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

import sys
import os
from functools import partial
from logging import getLogger, INFO

from .util import call_with



def _writeln(stream, string, last_com=False):
    stream.write(string)
    stream.write(os.linesep)
    stream.flush()

def stdout_callback_factory():
    return partial(_writeln, sys.stdout)

def stderr_callback_factory():
    return partial(_writeln, sys.stderr)

def overwrite_callback_factory(stream=sys.stdout):
    string_length = [0]

    def overwrite_callback(string, last_com=False):
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

    return overwrite_callback

def logging_callback_factory(logger_name="", log_level=INFO):
    logger = getLogger(logger_name)
    def logging_callback(string, last_com=False):
        logger.log(log_level, string)
        if last_com and hasattr(logger, "flush"):
            logger.flush()

    return logging_callback


def store_till_end_callback_factory(destination=lambda m: None):
    messages = []
    def store_till_end_callback(string, last_com=False):
        messages.append(string)
        if last_com:
            destination(messages)
    return store_till_end_callback


def multi_callback_factory(callback_factories, **kwargs):
    callbacks = []
    for factory in callback_factories:
        callbacks.append(call_with(factory, kwargs))

    def multi_callback(string, last_com=False): 
        for callback in callbacks:
            callback(string, last_com)

    return multi_callback


__callback_factories__ = {
    "$stdout" : stdout_callback_factory,
    "$stderr" : stderr_callback_factory,
    "$overwrite" : overwrite_callback_factory,
    "$log" : logging_callback_factory,
    "$store_till_end" : store_till_end_callback_factory,
    "$multi" : multi_callback_factory

}


