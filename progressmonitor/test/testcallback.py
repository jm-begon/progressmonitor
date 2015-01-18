# -*- coding: utf-8 -*-
"""
test queen
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "15 January 2015"

from nose.tools import assert_equal

from progressmonitor.callback import (store_till_end_callback_factory,
                                      multi_callback_factory)


def test_ste():
    msgs = ["aaa", "bbb", "ccc"]
    def dest(l):
        for x, y in zip(l, msgs):
            assert_equal(x, y)

    stecb = store_till_end_callback_factory(dest)
    for msg in msgs[:-1]:
        stecb(msg)
    stecb(msgs[-1], True)
    
def test_mcf():

    msgs = ["aaa", "bbb", "ccc"]
    l1 = []
    l2 = []

    def l1_cb_fac():
        def l1_cb(string, last_com=False):
            l1.append(string)
        return l1_cb

    def l2_cb_fac():
        def l2_cb(string, last_com=False):
            l2.append(string)
        return l2_cb

    cb = multi_callback_factory([l1_cb_fac, l2_cb_fac])
    for msg in msgs:
        cb(msg)

    for i in xrange(len(msgs)):
        assert_equal(msgs[i], l1[i])
        assert_equal(msgs[i], l2[i])
        