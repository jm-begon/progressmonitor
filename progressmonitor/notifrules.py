# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

import time

from .util import fallback

# =========================== NOTIFICATION RULES =========================== #

def always_notif_rule_factory():
    def true():
        return True
    return true

def periodic_rule_factory(frequency):
    last_update = [time.time()]
    def periodic_notif_rule(_):
        now = time.time()
        if (now - last_update[0]) >= frequency:
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


