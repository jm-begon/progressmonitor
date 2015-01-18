# -*- coding: utf-8 -*-
"""
test queen
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "15 January 2015"

from cStringIO import StringIO
import sys
from nose.tools import assert_equal

from progressmonitor import monitor_with
from progressmonitor.formatter import (nb_iterations_formatter_factory, 
                                       exception_formatter_factory)
from progressmonitor.hook import callback_hook_factory
from progressmonitor.callback import stdout_callback_factory




class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

    def compare_with(self, string):
        strings = string.split("\n")
        for s1, s2 in zip(self, strings):
            if s1 != s2:
                return False
        return True

    def starts_with(self, string):
        for s in self:
            if not s.startswith(string):
                return False

        return True

    def __str__(self):
        r = ""
        for s in self:
            r += s
        return r


def test_fail_monitor_with_gen():
    length = 24
    result = "." * 24
    with Capturing() as output:
        for _ in monitor_with("None")(xrange(length)):
            sys.stdout.write(".")
    assert_equal(result, str(output))

def test_fail_monitor_with_func():
    length = 24
    result = "." * 24
    @monitor_with("None")
    def embed():
        for _ in xrange(length):
            sys.stdout.write(".")
    with Capturing() as output:
        embed()

    assert_equal(result, str(output))

def test_fail_monitor_with_code():
    length = 24
    result = "." * 24
    with Capturing() as output:
        with monitor_with("None"):
            for _ in monitor_with("None")(xrange(length)):
                sys.stdout.write(".")
    assert_equal(result, str(output))   