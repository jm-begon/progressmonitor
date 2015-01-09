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

from progressmonitor.progressbar import rate_progressbar

def do_task():
    """Task simulator"""
    time.sleep(0.1)


class BrokenGenerator:
    """Generator which breaks at some point"""

    def __init__(self, length, broke_on):
        self.length = length
        self.broke_on = broke_on
        self.curr = 0
    def __len__(self):
        return self.length

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr < self.length:
            if self.curr < self.broke_on:
                rtn = self.curr
                self.curr += 1
                return rtn
            else:
                raise RuntimeError("Broken at "+str(self.curr))
        raise StopIteration()

    def next(self):
        """return the next iterations"""
        return self.__next__()


if __name__ == '__main__':
    length = 111
    rate = 0.1

    print "Exceptionless example"
    print "---------------------"
    generator = xrange(length)
    for _ in rate_progressbar(generator, rate):
        do_task()

    time.sleep(2)
    print 

    print "Example with exception"
    print "----------------------"
    broking_iter = 95
    broken_gen = BrokenGenerator(length, broking_iter)
    for _ in rate_progressbar(broken_gen, rate, fill="=", blank="-"):
        do_task()

