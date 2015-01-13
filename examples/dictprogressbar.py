# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
Custom progress bar configured from dictionary
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import time

from progressmonitor.config import get_monitor, dict_config


def lrange(n):
    for i in xrange(n):
        yield i

def do_task():
    """Task simulator"""
    time.sleep(0.1)


def writeln(messages):
    for message in messages:
        print message


if __name__ == '__main__':
    length = 102

    rate = 0.1
    span=10
    decay_rate = 0.1

    format_str = "{$thread} {$task} {$progressbar} {$time} {$exception}"
    format_str2= "Process {$pid}: {$task} [{$iteration}] -- {$elapsed} {$exception}"

    
    config = {
        "version": 1,
        "callbacks" : {
            "$writeln": ""+__name__+".writeln",
        },
        "progress_monitors": {
            "lengthy": {
                "format_str": format_str,
                "rate": rate,
                "span": span,
                "decay_rate":decay_rate,
                "blank": " ", 
                "callback_factory": "$multi",
                "callback_factories": ["$stdout", "$store_till_end"],
                "destination": "$writeln",
            },
            "lengthy.overwrite": {
                "callback_factory": "$overwrite",
                "name": "Fallback example",
            },
            "unlengthy": {
                "rule_factory": "$by_rate",
                "format_str": format_str2,
                "rate": None,
                "span": span,
                "decay_rate": decay_rate,
            },
        }
    }

    dict_config(config)
    

    print "With length example"
    print "---------------------"
    generator_ = xrange(length)
    for _ in get_monitor("lengthy", task_name="Lengthy")(generator_):
        do_task()

    print
    time.sleep(0.1)
    print


    print "Fallback example (without length)"
    print "---------------------"
    generator_ = lrange(length)
    for _ in get_monitor("lengthy.overwrite")(generator_):
        do_task()

    print
    time.sleep(0.1)
    print


    print "Without length example"
    print "---------------------"
    generator_ = lrange(length)
    for _ in get_monitor("unlengthy")(generator_):
        do_task()