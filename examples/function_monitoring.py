# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
This example illustrates the function monitoring with :func:`monitor_this`
and :func:`monitor_with`(and consequently the config facility).
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'

import time

from progressmonitor import monitor_this, dict_config, monitor_with
from progressmonitor.hook import default_hook





@monitor_this(hook=default_hook())
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
