# -*- coding: utf-8 -*-
"""
test queen
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "15 January 2015"

from cStringIO import StringIO
import sys
from nose.tools import assert_equal

from progressmonitor.monitor import monitor_generator
from progressmonitor.formatter import (nb_iterations_formatter_factory, 
                                       exception_formatter_factory)
from progressmonitor.hook import callback_hook_factory
from progressmonitor.callback import stdout_callback_factory


def lrange(length):
    for x in xrange(length):
        yield x

def broken_gen(length, error_step):
    for x in xrange(length):
        if x == error_step:
            raise Exception("x == error_step")
        yield x

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

def get_hook(formatter):
    return callback_hook_factory(stdout_callback_factory(), formatter)

def is_true(v):
    assert_equal(v, True)


def test_nb_iterations():
    result1 = """0/9
0/9
1/9
2/9
3/9
4/9
5/9
6/9
7/9
8/9
9/9
9/9"""
    with Capturing() as output:
        hook = get_hook(nb_iterations_formatter_factory())
        for _ in monitor_generator(xrange(10), hook):
            pass
        is_true(output.compare_with(result1))

    result2 = """0/???
0/???
1/???
2/???
3/???
4/???
5/???
6/???
7/???
8/???
9/???
9/9"""
    with Capturing() as output:
        hook = get_hook(nb_iterations_formatter_factory())
        for _ in monitor_generator(lrange(10), hook):
            pass
        is_true(output.compare_with(result2))

def test_exception():
    with Capturing() as output:
        hook = get_hook(exception_formatter_factory())
        try:
            for x in monitor_generator(broken_gen(10, 2), hook):
                pass
        except:
            pass
    is_true(output[-1].startswith("Aborted after"))




