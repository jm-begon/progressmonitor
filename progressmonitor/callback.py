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

def logging_callback_factory(name, log_level=INFO):
    logger = getLogger(name)
    def logging_callback(string, last_com=False):
        logger.log(log_level, string)

    return logging_callback

__callback_factories__ = {
    "stdout" : stdout_callback_factory,
    "stderr" : stderr_callback_factory,
    "overwrite" : overwrite_callback_factory,
    "log" : logging_callback_factory

}


