# -*- coding: utf-8 -*-
"""
test queen
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "15 January 2015"

from nose.tools import assert_equal

from progressmonitor.monitor import monitor_generator
from progressmonitor.rule import span_rule_factory, rate_rule_factory
from progressmonitor.util import nb_notifs_from_rate





def test_always_notif():
    length = 100
    counter = [0]
    def counter_hook(task, exception=None, **kwargs):
        counter[0] += 1

    for _ in monitor_generator(xrange(length), counter_hook):
        pass

    # Notify at the beginning + at the end + once for each iteration
    assert_equal(counter[0], length + 2)


def test_span_notif():
    span = 3
    length = 101

    counter = [0]
    def counter_hook(task, exception=None, **kwargs):
        counter[0] += 1

    for _ in monitor_generator(xrange(length), counter_hook, 
                               should_notify=span_rule_factory(span)):
        pass

    assert_equal(counter[0], ((length-1)/span)+2)

def test_rate_notif():
    rate = 0.23
    length = 123
    nb_notifs = nb_notifs_from_rate(rate, length)

    counter = [0]
    def counter_hook(task, exception=None, **kwargs):
        counter[0] += 1

    for _ in monitor_generator(xrange(length), counter_hook, 
                               should_notify=rate_rule_factory(rate, length)):
        pass

    # Completion notification
    assert_equal(counter[0], nb_notifs+1)




