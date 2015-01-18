# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
This example illustrates the code monitoring with :func:`code_monitor`.
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import time
import sys

from progressmonitor import code_monitor




def do_task():
    """Task simulator"""
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(0.1)



if __name__ == '__main__':
    
    length = 102

    print "Monitoring code"
    print "---------------"

    with code_monitor():
        print 
        for _ in xrange(length):
            do_task()
        print 
