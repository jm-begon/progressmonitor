# -*- coding: utf-8 -*-
"""
test queen
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "15 January 2015"

from nose.tools import assert_equal

from progressmonitor.monitor import (ProgressableTask, monitor_generator, 
                                     monitor_function, monitor_code, Task)


def except_hook(task, exception=None):
    if exception is not None:
        assert_equal(task.status == Task.ABORTED)
    if task.is_completed:
        raise Exception("Should not be completed")


def test_update_task():
    task = ProgressableTask(1)
    assert_equal(task.progress, 0)
    assert_equal(task.is_completed, False)

    task.update(1)
    task.close(True)
    assert_equal(task.progress, 1)
    assert_equal(task.is_completed, True)

def test_monitor_gen():
    length = 10

    def hook_(task, exception=None):
        assert_equal(exception, None)
        if task.progress == length:
            assert_equal(task.is_completed, True)

    for z, x in zip(monitor_generator(xrange(length), hook=hook_), xrange(length)):
        assert_equal(z, x)

def test_monitor_gen_err():
    length = 10

    try:
        for x in monitor_generator(xrange(length), hook=except_hook):
            if x == 2:
                raise Exception("x==2")
    except:
        pass



def test_monitor_fun():

    def rtn2():
        return 2

    def hook_(task, exception=None):
        assert_equal(exception, None)
        assert_equal(task.function, rtn2)
        if task.progress == 0:
            assert_equal(task.is_completed, False)
        if task.progress == 1:
            assert_equal(rtn2(), task.result)
            assert_equal(task.is_completed, True)

    monitor_function(rtn2, hook_)

def test_monitor_fun_err():

    def rtn2():
        raise Exception("x==2")

    try:
        monitor_function(rtn2, except_hook)
    except:
        pass


def test_monitor_code():


    def hook_(task, exception=None):
        assert_equal(exception, None)
        if task.progress == 0:
            assert_equal(task.is_completed, False)
        if task.progress == 1:
            assert_equal(task.is_completed, True)

    with monitor_code(hook_):
        pass



def test_monitor_code_err():

    try:
        with monitor_code(except_hook):
            raise Exception()
    except:
        pass



