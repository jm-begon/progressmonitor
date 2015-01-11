# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

from inspect import getargspec

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
    '1d 4h 52m 23s'
    """
    sec = duration % 60
    excess = int(duration) // 60  # minutes
    res = ("%."+str(subsec_precision)+"f s") % sec
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


def kw_intersect(function, dictionary):
    sub_dict = dict()
    try:
        prototype = getargspec(function)
    except TypeError:
        # In case of a class
        print ">>>", function, function.__class__ #TODO remove
        prototype = getargspec(function.__init__)

    # If function as a **kwargs, it will swallow all the extra arguments
    if prototype.keywords is not None:
        return dictionary
    func_args = prototype.args
    for key in func_args:
        if key in dictionary:
            sub_dict[key] = dictionary[key]
    return sub_dict

def call_with(function, dictionary, *args):
    return function(*args, **kw_intersect(function, dictionary))


def swallow_kwargs():
    def apply_swallow_kwargs(f):
        return lambda **kwargs: call_with(f, **kwargs)

    return apply_swallow_kwargs



# ============================== FALLBACKS ============================== #



def fallback_embeder(func, *funcs):
    def apply_fallback(*args, **kwargs):
        try:
            return call_with(func, kwargs, *args)
        except TypeError:
            for func_ in funcs:
                try:
                    return call_with(func_, kwargs, *args)
                except TypeError:
                    pass
            raise
    return apply_fallback


def fallback(func1, *funcs):
    def fallback_wrapper(f):
        return fallback_embeder(f, *([func1]+list(funcs)))
    return fallback_wrapper








