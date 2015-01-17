# -*- coding: utf-8 -*-
"""
test queen
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "15 January 2015"

from nose.tools import assert_equal
import dis

from progressmonitor.formatter import (progressbar_formatter_factory, 
                                       nb_iterations_formatter_factory,
                                       elapsed_time_formatter_factory,
                                       remaining_time_formatter_factory)
from progressmonitor.rule import (periodic_rule_factory, 
                                  span_rule_factory, rate_rule_factory)
from progressmonitor.util import call_with






def test_fb_rate2span():
    kwargs = {"rate": 0.1, "span":10}
    r1 = call_with(rate_rule_factory, kwargs)
    r2 = call_with(span_rule_factory, kwargs)
    assert_equal(r1.__name__, r2.__name__)

def test_fb_span2period():
    kwargs = {"period":1}
    r1 = call_with(span_rule_factory, kwargs)
    r2 = call_with(periodic_rule_factory, kwargs)
    assert_equal(r1.__name__, r2.__name__)


def test_fb_pb2nbiter():
    kwargs = {}
    r1 = call_with(progressbar_formatter_factory, kwargs)
    r2 = call_with(nb_iterations_formatter_factory, kwargs)
    assert_equal(r1.__name__, r2.__name__)

def test_fb_remaining2elapsed():
    kwargs = {}
    r1 = call_with(remaining_time_formatter_factory, kwargs)
    r2 = call_with(elapsed_time_formatter_factory, kwargs)
    assert_equal(r1.__name__, r2.__name__)
