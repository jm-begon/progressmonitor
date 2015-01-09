# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

from functools import partial
from ast import literal_eval

from .progressbar import monitor as monitor_factory

class Manager(object):

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super(Manager, cls).__new__(cls, *args, **kwargs)
            cls._singleton._monitors = dict()
        return cls._singleton


    def get_monitor(self, name, *args, **kwargs):
        monitor = self._monitors.get(name, None)
        if monitor is None:
            print "Monitor", name, id(self), #TODO remove
            print self._monitors #TODO remove
            monitor = monitor_factory(*args, **kwargs)
            self._monitors[name] = monitor
            print self._monitors #TODO remove
        return monitor

def get_monitor(name, *args, **kwargs):
    return Manager().get_monitor(name, *args, **kwargs) 


def dict_config_v1(config_dict):
    notif_rules_str = "notification_rules"
    hook_str = "hooks"
    monitor_str = "monitors"
    # Loading the notifiction rules
    if notif_rules_str in config_dict:
        rules_dict = config_dict[notif_rules_str]
        # TODO
    # Loading the hooks
    if hook_str in config_dict:
        hook_dict = config_dict[hook_str]
        # TODO
    # Getting the monitors
    if monitor_str in config_dict:
        monitor_dict = config_dict[monitor_str]
        for name, conf in monitor_dict.iteritems():
            get_monitor(name, **conf)



def dict_config(config_dict):
    version = config_dict.get("version", 1)
    if version == 1:
        dict_config_v1(config_dict)
    else:
        raise AttributeError("Version "+str(version)+" is not supported")


def file_config(config_file):
    with open(config_file) as fp:
        config_dict = literal_eval(fp.read())
    dict_config(config_dict)
