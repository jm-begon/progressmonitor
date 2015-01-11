# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

from ast import literal_eval

from .factory import monitor as monitor_factory
from .hook import __hook_factories__
from .notifrules import __rule_factories__
from .callback import __callback_factories__

# ============================ MANAGER ============================ #

class Manager(object):

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super(Manager, cls).__new__(cls, *args, **kwargs)
            cls._singleton._monitors = dict()
        return cls._singleton

    def add_monitor(self, name, monitor):
        self._monitors[name] = monitor
        return monitor


    def get_monitor(self, name):
        return self._monitors[name]



# ============================ DICT PARSING ============================ #

class Const(object):

    VERSION = "version"
    RULES_FACTORIES_SECTION = "notification_rules_factories"
    HOOK_FACTORIES_SECTION = "hook_factories"
    MONITORS_SECTION = "monitors"
    RULE_TAG = "rule"
    HOOK_TAG = "hook"
    CALLBACK_TAG = "callback"
    RULE_KW = "rule_factory"
    HOOK_KW = "hook_factories"
    CALLBACK_KW = "callback_factory"




def _external_load(string):
    mod_str, obj_str = string.rsplit(".", 1)
    mod = __import__(mod_str, fromlist=[obj_str])
    obj = getattr(mod, obj_str)
    return obj





def _dict_config_v1(config_dict):
    manager = Manager()

    # ---- Predefined stuffs  ---- #
    rule_facto = __rule_factories__
    hook_facto = __hook_factories__
    callback_facto = __callback_factories__

    # ---- Getting the rules ---- #
    # Getting the external dict
    if Const.RULES_FACTORIES_SECTION in config_dict:
        rules_ext_d = config_dict[Const.RULES_FACTORIES_SECTION]
        # Loading the external rules
        for name, function in rules_ext_d.iteritems():
            rule_facto[name] = _external_load(function)


    # ---- Getting the hook factories ---- #
    if Const.HOOK_FACTORIES_SECTION in config_dict:
        hook_factories_ext_d = config_dict[Const.HOOK_FACTORIES_SECTION]
        # Loading the external rules
        for name, function in hook_factories_ext_d.iteritems():
            hook_facto[name] = _external_load(function)


    # ---- Getting the monitors ---- #
    for name, conf in config_dict[Const.MONITORS_SECTION].iteritems():
        # Building the callback factory
        if Const.CALLBACK_TAG in conf:
            callback_str = conf[Const.CALLBACK_TAG]
            callback = callback_facto[callback_str]
            del conf[Const.CALLBACK_TAG]
            conf[Const.CALLBACK_KW] = callback


        # Building the rule factory
        if Const.RULE_TAG in conf:
            rule_str = conf[Const.RULE_TAG]
            rule = rule_facto[rule_str]
            del conf[Const.RULE_TAG]
            conf[Const.RULE_KW] = rule

        # Creating the monitor
        monitor = monitor_factory(**conf)

        # Setting the monitor
        manager.add_monitor(name, monitor)


# ============================ PUBLIC EXPOSURE ============================ #

def get_monitor(name, *args, **kwargs):
    return Manager().get_monitor(name, *args, **kwargs) 



def dict_config(config_dict):
    version = config_dict.get(Const.VERSION, 1)
    if version == 1:
        _dict_config_v1(config_dict)
    else:
        raise AttributeError("Version "+str(version)+" is not supported")


def file_config(config_file):
    with open(config_file) as fp:
        config_dict = literal_eval(fp.read())
    dict_config(config_dict)
