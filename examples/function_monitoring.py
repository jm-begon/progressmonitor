# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
Basic example of rate progress bar
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import time

from progressmonitor import monitor_this, dict_config, monitor_with
from progressmonitor.formatter import elapsed_time_formatter_factory
from progressmonitor.callback import stdout_callback_factory


def get_hook():
    eth = elapsed_time_formatter_factory()
    cb = stdout_callback_factory()

    def actual_hook(task, exception=None, **kwargs):
        last_com = task.is_completed or exception is not None
        cb(eth(task, exception, **kwargs), last_com)

    return actual_hook


@monitor_this(hook=get_hook())
def do_task(t, *args, **kwargs):
    """Task simulator"""
    print "\ttime:", t
    print "\targs:", args
    print "\tkwargs", kwargs
    time.sleep(t)






if __name__ == '__main__':

    print "Function monitoring example"
    print "---------------------------"
    do_task(4, 2, a=3)


    print

    print "Function monitoring from dict"
    print "-----------------------------"


    config = {
        "version": 1,
        "function_monitors": {
            "f_monitor" : {
                "callback_factory": "$stdout",
                "format_str": "{$task} {$elapsed} {$exception}",
                "multiline": True,
            }
        }
    }

    dict_config(config)

    @monitor_with("f_monitor")
    def do_task2(t, *args, **kwargs):
        """Task simulator"""
        time.sleep(t)
        return "done"


    print do_task2(4, 2, a=3)
