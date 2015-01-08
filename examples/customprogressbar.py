# -*- coding: utf-8 -*-
"""
Custom progress bar
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import time

from progressmonitor.progressbar import custom_progressbar


def lrange(n):
    for i in xrange(n):
        yield i

def do_task():
    """Task simulator"""
    time.sleep(0.1)




if __name__ == '__main__':
    length = 102
    rate = 0.1
    span=10
    decay_rate = 0.1


    format_str = "{task} {progressbar} {time} {exception}"

    print "With length example"
    print "---------------------"
    generator = xrange(length)
    for _ in custom_progressbar(generator, format_str, rate, span, 
                                decay_rate=decay_rate, blank=" "):
        do_task()

    print
    time.sleep(0.1)
    print

    format_str = "{task} [{iteration}] -- {elapsed} {exception}"

    print "Without length example"
    print "---------------------"
    generator = lrange(length)
    for _ in custom_progressbar(generator, format_str, rate=None, span=span, 
                                decay_rate=decay_rate, blank=" "):
        do_task()