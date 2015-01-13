# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"

import re
from ast import literal_eval

from .factory import monitor as monitor_factory
from .factory import monitor_function_factory, formated_code_monitoring
from .hook import __hook_factories__
from .notifrules import __rule_factories__
from .callback import __callback_factories__

# ============================ MANAGER ============================ #

class Manager(object):

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super(Manager, cls).__new__(cls, *args, **kwargs)
            cls._singleton._confs = dict()
        return cls._singleton

    def add_config(self, monitor_name, conf):
        self._confs[monitor_name] = conf

    def _get_ancestors_conf(self, monitor_name):
        conf = dict()
        prefixes = [monitor_name[:m.start()] 
                    for m  in re.finditer('\.',monitor_name)]
        prefixes.append(monitor_name)
        for prefix in prefixes:
            conf.update(self._confs.get(prefix, dict()))
        return conf



    def get_config(self, monitor_name, **kwargs):
        conf = self._get_ancestors_conf(monitor_name)
        if len(kwargs) > 0:
            tmp = conf.copy()
            tmp.update(kwargs)
            conf = tmp
        return conf




# ============================ DICT PARSING ============================ #

class Const(object):

    VERSION = "version"
    MONITORS = "progress_monitors"
    FUNC_MONITORS = "function_monitors"
    CODE_MONITORS = "code_monitors"
    
    CALLBACK_SEC = "callbacks"
    RULE_SEC = "rules"
    HOOK_SEC = "hooks"



def _external_load(string):
    mod_str, obj_str = string.rsplit(".", 1)
    mod = __import__(mod_str, fromlist=[obj_str])
    obj = getattr(mod, obj_str)
    return obj


def _substitute(struct, substit_dict):
    if hasattr(struct, "startswith"):
        if struct.startswith("$"):
            return substit_dict[struct]
        
    elif hasattr(struct, "iteritems"):
        # dict --> inspect 
        for k, v in struct.iteritems():
            struct[k] = _substitute(v, substit_dict)

    else:
        try:
            # List -> inspect
            for i, elem in enumerate(struct):
                struct[i] = _substitute(elem, substit_dict)
        except TypeError:
            pass

    return struct

def _dict_config_v1(config_dict):
    manager = Manager()

    # ---- Predefined replacement rules  ---- #
    substit_dict = dict()
    substit_dict.update(__rule_factories__)
    substit_dict.update(__hook_factories__)
    substit_dict.update(__callback_factories__)


    # ---- Adding the substitutions ---- #
    # rules
    if Const.RULE_SEC in config_dict:
        for k, v in config_dict[Const.RULE_SEC].iteritems():
            if k.startswith("$"):
                loaded = _external_load(v)
                substit_dict[k] = loaded
                __rule_factories__[k] = loaded

    # hook
    if Const.HOOK_SEC in config_dict:
        for k, v in config_dict[Const.HOOK_SEC].iteritems():
            if k.startswith("$"):
                loaded = _external_load(v)
                substit_dict[k] = loaded
                __hook_factories__[k] = loaded

    # callback
    if Const.CALLBACK_SEC in config_dict:
        for k, v in config_dict[Const.CALLBACK_SEC].iteritems():
            if k.startswith("$"):
                loaded = _external_load(v)
                substit_dict[k] = loaded
                __callback_factories__[k] = loaded

    # ---- Performing the substitutions ---- #
    config_dict = _substitute(config_dict, substit_dict)

    

    # ---- Getting the monitors ---- #
    if Const.MONITORS in config_dict:
        for name, conf in config_dict[Const.MONITORS].iteritems():        
            # Adding to the manager
            manager.add_config(name, conf)

    # ---- Getting the monitors for functions ---- #
    if Const.FUNC_MONITORS in config_dict:
        for name, conf in config_dict[Const.FUNC_MONITORS].iteritems():
            # Adding to the manager
            manager.add_config(name, conf)

    # ---- Getting the monitors for functions ---- #
    if Const.CODE_MONITORS in config_dict:
        for name, conf in config_dict[Const.CODE_MONITORS].iteritems():
            # Adding to the manager
            manager.add_config(name, conf)

# ============================ PUBLIC EXPOSURE ============================ #

def get_monitor(monitor_name, **kwargs):
    conf = Manager().get_config(monitor_name, **kwargs) 
    return monitor_factory(**conf)


def monitor_with(monitor_name, **kwargs):
    conf = Manager().get_config(monitor_name, **kwargs)
    return monitor_function_factory(**conf)

def code_monitor(monitor_name, **kwargs):
    conf = Manager().get_config(monitor_name, **kwargs)
    return formated_code_monitoring(**conf)

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
