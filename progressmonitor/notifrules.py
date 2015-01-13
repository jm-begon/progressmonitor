# -*- coding: utf-8 -*-
"""
:mod:`notifrules` contains notification rule factories. The factories return
notification rule per se.

A notification rule is a function of the type:
    Parameters
    ----------
    task : class:`Task`
        The task on which to decide whether it is time to notify or not
    Return
    ------
    should_notify : boolean
        Whether the notification should be issued

Notification rules are used for iterators/generators monitoring so as not
to issue notification on every iteration.

Notification rules should be provided through a factory so as to be 
parametrizable and be accessed in the same fashion.
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

import time

from .util import fallback

# =========================== NOTIFICATION RULES =========================== #

def always_notif_rule_factory():
    """
    Return
    ------
    true : callable
    """
    def true():
        """
        Return
        ------
        True
        """
        return True
    return true

def periodic_rule_factory(period):
    """
    Parameters
    ----------
    period : float
        The minimum period between two notification (in seconds)
    Return
    ------
    periodic_notif_rule : callable
        see :func:`periodic_notif_rule`
    """
    last_update = [time.time()]
    def periodic_notif_rule(_):
        """
        Return
        ------
        should_notify : boolean
            Whether to notify
        """
        now = time.time()
        if (now - last_update[0]) >= period:
            last_update[0] = now
            return True
        return False
    return periodic_notif_rule


@fallback(periodic_rule_factory)
def span_rule_factory(span=1):
    """
    Indicates whether to notify or not base on a span
    
    Parameters
    ----------
    span : int (Default : 1)
        The number of iteration to span without notifying

    Return
    ------
    span_update : callable (int)
        A function wi
    """
    def span_notif_rule(task):
        return False if task.progress() == 0 else (task.progress() % span == 0)
    return span_notif_rule


@fallback(span_rule_factory)
def rate_rule_factory(rate, length):
    last_update = [0]
    def rate_notif_rule(task):
        progress = task.progress()
        delta = (float(progress - last_update[0])/length)
        if delta >= rate:
            last_update[0] = progress
            return True
        return False

    return rate_notif_rule



__rule_factories__ = {
    "$always_true" : always_notif_rule_factory,
    "$periodic" : periodic_rule_factory,
    "$by_span" : span_rule_factory,
    "$by_rate" : rate_rule_factory

}


