# -*- coding: utf-8 -*-
"""
:mod:`rule` contains notification rule factories. The factories return
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
parametrizable and be accessed in a standard fashion.
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
    Return a notification rule which is always true

    Return
    ------
    true : callable(_)
    """
    def true(_):
        """
        Return
        ------
        True
        """
        return True
    return true

def periodic_rule_factory(period):
    """
    Return a notification rule which indicates whether to notify or not base
    on the time elapsed since the last notification.

    Parameters
    ----------
    period : float
        The minimum period between two notification (in seconds)

    Return
    ------
    periodic_notif_rule
    """
    last_update = [time.time()]
    def periodic_notif_rule(_):
        """
        Notification rule based on the elapsed time since the last notification

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
def span_rule_factory(span):
    """
    Return a rule which indicates whether to notify or not base on a span ; 
    issue the notification every `span` iterations
    
    Parameters
    ----------
    span : int (Default : 1)
        The number of iteration to span without notifying

    Return
    ------
    span_notif_rule

    Fallback
    --------
    periodic_rule_factory
    """
    def span_notif_rule(task):
        """
        Rule which issues a notification after a fix number of iterations.

        Return
        ------
        should_notify : boolean
            Whether to notify
        """
        return False if task.progress == 0 else (task.progress % span == 0)
    return span_notif_rule


@fallback(span_rule_factory)
def rate_rule_factory(rate, length):
    """
    Return a rule which indicates whether to notify or not base on the rate

    Parameters
    ----------
    rate : float
        The rate at which to issue notifications. The number of notifications
        can be computed as:
            int(math.ceil(1./rate)
    length : int
        The size of the iterator

    Return
    ------
    rate_notif_rule

    Fallback
    --------
    span_rule_factory
    """
    last_update = [0]
    def rate_notif_rule(task):
        """
        Rule which issues a notification at a predifined rate
        Return
        ------
        should_notify : boolean
            Whether to notify
        """
        progress = task.progress
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


