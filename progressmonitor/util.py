# -*- coding: utf-8 -*-
"""
Module :mod:`util` contains utiliatry methods.
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

import math
from inspect import getargspec
import logging


def nb_notifs_from_rate(rate, length):
    """
    Compute the number of notifications from the rate

    Parameters
    ----------
    rate : float 0 <= rate <= 1
        The notification rate
    length : int >= 0
        The size of the iterator

    Return
    ------
    The number of notifications corresponding to the given rate
    """
    if length is None:
        raise AttributeError("'nb_notifs' can only be determined if length \
                              is available")
    return int(math.ceil(1./rate))


# ============================== FORMATER ============================== #

def format_duration(duration, subsec_precision=2):
    """
    Format the duration expressed in seconds as string

    Parameters
    ----------
    duration : float
        a duration in seconds

    subsec_precision : int (>=0)
        the number of decimal for the second part of the duration
    Return
    ------
    formated : str
        the given duration formated

    Example
    -------
    >>> days = 1
    >>> hours = 4
    >>> minutes = 52
    >>> seconds = 23
    >>> duration = seconds + 60*(minutes + 60*(hours + 24*days))
    >>> format_duration(duration)
    '1d 4h 52m 23.00s'
    """
    sec = duration % 60
    excess = int(duration) // 60  # minutes
    res = ("%."+str(subsec_precision)+"fs") % sec
    if excess == 0:
        return res
    minutes = excess % 60
    excess = excess // 60  # hours
    res = str(minutes) + "m " + res
    if excess == 0:
        return res
    hour = excess % 24
    excess = excess // 24  # days
    res = str(hour) + "h " + res
    if excess == 0:
        return res
    res = str(excess)+"d " + res
    return res


def format_size(nb_bytes):
    """
    Format a size expressed in bytes as a string

    Parameters
    ----------
    nb_bytes : int
        the number of bytes

    Return
    ------
    formated : str
        the given number of bytes fromated

    Example
    -------
    >>> format_size(100)
    '100.0 bytes'
    >>> format_size(1000)
    '1.0 kB'
    >>> format_size(1000000)
    '1.0 MB'
    >>> format_size(1000000000)
    '1.0 GB'
    >>> format_size(1000000000000)
    '1.0 TB'
    >>> format_size(1000000000000000000)
    '1000000.0 TB'

    """
    for x in ['bytes', 'kB', 'MB', 'GB']:
        if nb_bytes < 1000.0:
            return "%3.1f %s" % (nb_bytes, x)
        nb_bytes /= 1000.0
    return "%3.1f %s" % (nb_bytes, 'TB')



# ============================== INSPECTION ============================== #


def kw_intersect(function, dictionary, *args, **kwargs):
    """
    Computes the intersection between the function's parameters and
    the given dictionary

    Parameters
    ----------
    function : callable
        The function to process
    dictionary : dict
        The dictionary to process
    args : list
        The list of positional arguments
    kwargs : dict
        The keyword arguments

    Return
    ------
    intersect_dict : dict
        The intersection between the function's parameters and the given 
        dictionary
    """
    try:
        prototype = getargspec(function)
    except TypeError:
        # In case of a class
        prototype = getargspec(function.__init__)

    # If function as a **kwargs, it will swallow all the extra arguments
    if prototype.keywords is not None and len(args) == 0:
        return dictionary
    # Intersecting dictionaries
    sub_dict = dict()
    func_args = prototype.args
    for i, key in enumerate(func_args):
        if i >= len(args):
            if key in dictionary:
                sub_dict[key] = dictionary[key]
            if key in kwargs:
                sub_dict[key] = kwargs[key]
    return sub_dict

def call_with(function, dictionary, *args, **kwargs):
    """
    Call the given function with the given dictionary with the additional
    supplied arguments 

    Parameters
    ----------
    function : callable
        The function to process
    dictionary : dict
        The dictionary to process
    args : list
        The list of positional arguments
    kwargs : dict
        The keyword arguments

    Return
    ------
    The result of the function with the given sefely inputs
    """
    return function(*args, **kw_intersect(function, dictionary, *args, **kwargs))



# ============================== FALLBACKS ============================== #



def fallback_embeder(func, *funcs):
    """
    Embed the given function for callbacks

    Parameters
    ----------
    func : callable factory
        The function to protect
    funcs : iterator of callable factories
        The safegard functions

    Return
    ------
    The first function which can be applied

    Logging
    -------
    Issue a logging warning on fallback on the logger 
    name "progressmonitor.fallback"
    """
    def apply_fallback(*args, **kwargs):
        try:
            return call_with(func, kwargs, *args)
        except TypeError, reason1:
            logger = logging.getLogger("progressmonitor.fallback")
            logger.warning("Fallback : "+str(reason1))
            for func_ in funcs:
                try:
                    return call_with(func_, kwargs, *args)
                except TypeError, reason2:
                    logger.warning("Fallback : "+str(reason2))
            raise
    return apply_fallback


def fallback(func1, *funcs):
    """
    fallback decorator

    Parameters
    ----------
    func1 : callable
        The first function to use in case of fallback
    funcs : list of callable
        THe sequence of function to use in case of fallback (func1 included)

    Return
    ------
    func : callable
        A function expected another function to embed in a fallback

    Usage
    -----
    @fallback(f1)
    def f2():
        pass
    """
    def fallback_wrapper(f):
        return fallback_embeder(f, *([func1]+list(funcs)))
    return fallback_wrapper



class IdProxy(object):
    """
    =======
    IdProxy
    =======
    A proxy for function and context manager.

    >>> f = lambda x: x**2
    >>> proxy = IdProxy()
    >>> proxy(f) == f
    True
    >>> proxy(f)(2) == f(2)
    True
    """

    def __call__(self, f):
        return f

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False







