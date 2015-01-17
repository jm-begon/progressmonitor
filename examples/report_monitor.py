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
import getpass
import sys
import smtplib
import logging
from logging.handlers import SMTPHandler


from progressmonitor import dict_config, report_with




def _mult(x, y):
    return x*y

def _add(x, y):
    return x+y

def writeln(messages):
    for message in messages:
        print message








if __name__ == '__main__':

    config = {
        "version": 1,
        "function_monitors": {
            "reporter" : {
                "callback_factory": "$log",
                "logger_name": "on_end"
            }
        }
    }
    dict_config(config)

    



    print "SMTP Host"
    host_ = sys.stdin.readline().rstrip()
    
    port_ = str(smtplib.SMTP_PORT)
    print "SMTP Port (press ENTER for default port: %s" % port_
    p = sys.stdin.readline().rstrip()
    if p != "":
        port_ = p

    mailhost_ = (host_, port_)

    print "From address"
    from_ = sys.stdin.readline().rstrip()

    print "To address"
    to_ = sys.stdin.readline().rstrip()

    credentials_ = None
    secure_ = None
    print "Username (press ENTER to skip authentication)"
    username_ = sys.stdin.readline().rstrip()
    if username_ != "":
        password_ = getpass.getpass("password: ")
        credentials_ = (username_, password_)

        print "Use TTL (y/[n])"
        ttl_ = sys.stdin.readline().rstrip().lower()
        if ttl_.startswith("y"):
            secure_ = ()

    


    subject_ = "progress monitor test"


    logger = logging.getLogger("on_end")
    logger.setLevel(logging.DEBUG)
    handler = SMTPHandler(mailhost=mailhost_,
                          fromaddr=from_,
                          toaddrs=to_,
                          subject=subject_,
                          credentials=credentials_,
                          secure=secure_)

    logger.addHandler(handler)




    @report_with("reporter", task_name="do_task_monitoring")
    def do_task(func=_add, *args):
        """
        Task simulator

        Parameters
        ----------
        func : callable
            The function to apply
        args : list

        Return
        ------
        """
        comp = func.__name__+"("
        for arg in args:
            comp += str(arg)+", "
        comp = comp[:-2] + ") = "
        res = reduce(func, args)
        rtn = comp + str(res)
        print rtn
        print
        time.sleep(2)
        return rtn



    do_task(_mult, 2, 4, -1)

    # print "Function monitoring example"
    # print "---------------------------"
    # do_task(1, 2, a=3)


    # print

    # print "Function monitoring from dict"
    # print "-----------------------------"


    # config = {
    #     "version": 1,
    #     "function_monitors": {
    #         "f_monitor" : {
    #             "callback_factory": "$stdout",
    #             "format_str": "{$task} {$deblogger} {$elapsed} {$exception}",
    #             "multiline": True,
    #         }
    #     }
    # }

    # dict_config(config)

    # @monitor_with("f_monitor")
    # def do_task2(t, *args, **kwargs):
    #     """Task simulator"""
    #     time.sleep(t)
    #     return "done"


    # print do_task2(4, 2, a=3)
