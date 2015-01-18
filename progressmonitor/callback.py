# -*- coding: utf-8 -*-
"""
Module :mod:`callback` defines a set of callback functions to dispose of
strings return by formatters

Callbacks are assumed to be provided through factories so as to be stateful, 
parametrizable if need be and provide an homogenous building mechanism.

Callbacks are callable of the form
    Parameters
    ----------
    string : str
        The string to process
    last_com : bool (Default : False)
        Whether is it the last message or not
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
    """
    Writes and flushes the string on the stream

    Parameters
    ----------
    stream : :class:`StringIO`
        The stream to uses
    string : str
        The string to write
    last_com : bool (Default : False)
        Whether is it the last message or not
    """
    stream.write(string)
    stream.write(os.linesep)
    stream.flush()

def stdout_callback_factory():
    """
    :func:`callback_factory`

    Return
    ------
    callback : callable
        a callback issuing on stdout
    """
    return partial(_writeln, sys.stdout)

def stderr_callback_factory():
    """
    :func:`callback_factory`

    Return
    ------
    callback : callable
        a callback issuing on stderr
    """
    return partial(_writeln, sys.stderr)

def overwrite_callback_factory(stream=sys.stdout):
    """
    A :func:`callback_factory` which outputs on a stream and overwrite
    the previous message (provided the message is monoline)

    Parameters
    ----------
    stream : :class:`StringIO` (Default : stdout)
        The stream to uses

    Return
    ------
    :func:`overwrite_callback`
    """

    string_length = [0]

    def overwrite_callback(string, last_com=False):
        """
        A :func:`callback` which overwrite the previous message

        Parameters
        ----------
        string : str
            The string to process
        last_com : bool (Default : False)
            Whether is it the last message or not
        """
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
    """
    A :func:`callback_factory` which uses the logging facility

    Parameters
    ----------
    logger_name : str (Default : '')
        The name of the logger to use
    log_level : int (Default : INFO)
        The logging level

    Return
    ------
    :func:`logging_callback`
    """
    logger = getLogger(logger_name)
    def logging_callback(string, last_com=False):
        """
        A :func:`callback` write the string to a logger

        Parameters
        ----------
        string : str
            The string to process
        last_com : bool (Default : False)
            Whether is it the last message or not
        """
        logger.log(log_level, string)
        if last_com and hasattr(logger, "flush"):
            logger.flush()

    return logging_callback


def store_till_end_callback_factory(destination=lambda m: None):
    """
    A :func:`callback_factory` which stores the messages in a list
    and send them to the destination at the last message

    Parameters
    ----------
    destination : callable (Default : destination=lambda m: None)
        A function which takes as input a list of string

    Return
    ------
    :func:`store_till_end_callback`
    """
    messages = []
    def store_till_end_callback(string, last_com=False):
        """
        A :func:`callback` which stores the messages in a list
        and send them to the destination at the last message

        Parameters
        ----------
        string : str
            The string to process
        last_com : bool (Default : False)
            Whether is it the last message or not
        """
        messages.append(string)
        if last_com:
            destination(messages)
    return store_till_end_callback


def multi_callback_factory(callback_factories, **kwargs):
    """
    A :func:`callback_factory` which multiplexes the messages

    Parameters
    ----------
    callback_factories : iterable of :func:`callback_factory`
        The callback to use to issue the message

    Return
    ------
    :func:`multi_callback`
    """
    callbacks = []
    for factory in callback_factories:
        callbacks.append(call_with(factory, kwargs))

    def multi_callback(string, last_com=False):
        """
        A :func:`callback` which multipex messages

        Parameters
        ----------
        string : str
            The string to process
        last_com : bool (Default : False)
            Whether is it the last message or not
        """
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


