# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
This example illustrates the transparency of failure in case of missing 
configuration with :func:`monitor_with`.
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import time
import sys

from progressmonitor import monitor_with




def do_task():
    """Task simulator"""
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(0.1)



if __name__ == '__main__':
    
    length = 24

    print "Monitoring gen."
    print "---------------"
    for _ in monitor_with("none")(xrange(length)):
        do_task()

    print
    print "Monitoring fun."
    print "---------------"
    @monitor_with("none")
    def embed():
        for _ in xrange(length):
            do_task()
    embed()

    print
    print "Monitoring code"
    print "---------------"

    with monitor_with("none"):
        for _ in xrange(length):
            do_task()
        print 
