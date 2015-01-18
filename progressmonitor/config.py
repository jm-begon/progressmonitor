# -*- coding: utf-8 -*-
"""
Module :mod:`config` holds the whole configuration mechanism. 

Configuration can be conducted either from a dictionary :func:`dict_config` or
from a file :func:`file_config` holding directly the dictionary.

Configuration may be done several times but overlaps will be overwritten,
keeping the most recent one. This is also true with the preconfigured
formatter, callbacks and rules, so beware !

The dictionary has the following form:
{
    "version": <#num>,
    "callbacks": {
        <$aaa>: <mod.function_name>,
        ...
    },
    "rules": {
        <$bbb>: <mod.function_name>,
        ...
    },
    "formatters": {
        <$ccc>: <mod.function_name>,
        ...
    },
    "generator_monitors": {
        <gen_name>: {
            <args>: <value>,
            ...
        },
    },
    "function_monitors": {
        <func_name>: {
            <args>: <value>,
            ...
        },
    },
    "code_monitors": {
        <code_name>: {
            <args>: <value>,
            ...
        },
    },
}

Version section (mandatory)
    <#num> => the version number
callback section (optional)
    <$aaa> => a string starting with '$' : the shortcut name for the callback
    factory
rules section (optional)
    <$bbb> => a string starting with '$' : the shortcut name for the rule
    factory
formatters section (optional)
    <$ccc> => a string starting with '$' : the shortcut name for the formatter
    factory
generator_monitors section (optional)
    <gen_name> => the name of the monitor
        <args> => the name of the argument
        <value> => the value for the arguments
function_monitors section (optional)
    <func_name> => the name of the monitor
        <args> => the name of the argument
        <value> => the value for the arguments
code_monitors section (optional)
    <code_name> => the name of the monitor
        <args> => the name of the argument
        <value> => the value for the arguments
<mod.function_name> => the full path to the function (will be loaded 
dynamically)

The monitor name have hierarchical structure alike the logging.
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "08 January 2015"

import re
from ast import literal_eval
import logging

from .factory import monitor_generator_factory
from .factory import (monitor_function_factory, formated_code_monitoring)
from .formatter import __formatter_factories__
from .rule import __rule_factories__
from .callback import __callback_factories__
from .util import IdProxy

# ============================ MANAGER ============================ #

class Manager(object):

    UNKNOWN_MONITOR = 0
    GENERATOR_MONITOR = 1
    FUNCTION_MONITOR = 2
    CODE_MONITOR = 3

    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super(Manager, cls).__new__(cls, *args, **kwargs)
            cls._singleton._meta = dict()
        return cls._singleton

    def add_config(self, monitor_name, conf, monitor_type):
        self._meta[monitor_name] = (conf, monitor_type)

    def _get_ancestors_conf(self, monitor_name):
        unknown = Manager.UNKNOWN_MONITOR
        monitor_type = unknown
        conf = dict()
        prefixes = [monitor_name[:m.start()] 
                    for m  in re.finditer('\.',monitor_name)]
        prefixes.append(monitor_name)
        for prefix in prefixes:
            anc_conf, type_ = self._meta.get(prefix, (dict(), unknown))
            if type_ != Manager.UNKNOWN_MONITOR:
                monitor_type = type_
            conf.update(anc_conf)
        return conf, monitor_type



    def get_config(self, monitor_name, **kwargs):
        conf, monitor_type = self._get_ancestors_conf(monitor_name)
        if len(kwargs) > 0:
            conf.update(kwargs)
        return conf, monitor_type




# ============================ DICT PARSING ============================ #

class Const(object):

    VERSION = "version"
    MONITORS = "generator_monitors"
    FUNC_MONITORS = "function_monitors"
    CODE_MONITORS = "code_monitors"
    
    CALLBACK_SEC = "callbacks"
    RULE_SEC = "rules"
    FORMATTER_SEC = "formatters"



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
    substit_dict.update(__formatter_factories__)
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
    if Const.FORMATTER_SEC in config_dict:
        for k, v in config_dict[Const.FORMATTER_SEC].iteritems():
            if k.startswith("$"):
                loaded = _external_load(v)
                substit_dict[k] = loaded
                __formatter_factories__[k] = loaded

    # callback
    if Const.CALLBACK_SEC in config_dict:
        for k, v in config_dict[Const.CALLBACK_SEC].iteritems():
            if k.startswith("$"):
                loaded = _external_load(v)
                substit_dict[k] = loaded
                __callback_factories__[k] = loaded

    # ---- Performing the substitutions ---- #
    config_dict = _substitute(config_dict, substit_dict)

    

    # ---- Getting the monitors for generators---- #
    if Const.MONITORS in config_dict:
        for name, conf in config_dict[Const.MONITORS].iteritems():        
            # Adding to the manager
            manager.add_config(name, conf, Manager.GENERATOR_MONITOR)

    # ---- Getting the monitors for functions ---- #
    if Const.FUNC_MONITORS in config_dict:
        for name, conf in config_dict[Const.FUNC_MONITORS].iteritems():
            # Adding to the manager
            manager.add_config(name, conf, Manager.FUNCTION_MONITOR)

    # ---- Getting the monitors for functions ---- #
    if Const.CODE_MONITORS in config_dict:
        for name, conf in config_dict[Const.CODE_MONITORS].iteritems():
            # Adding to the manager
            manager.add_config(name, conf, Manager.CODE_MONITOR)

# ============================ PUBLIC EXPOSURE ============================ #
def get_config(monitor_name, **kwargs):
    conf, _ = Manager().get_config(monitor_name, **kwargs)
    return conf

def get_monitor(monitor_name, **kwargs):
    conf, monitor_type = Manager().get_config(monitor_name, **kwargs)
    if monitor_type == Manager.GENERATOR_MONITOR:
        return monitor_generator_factory(**conf)
    elif monitor_type == Manager.FUNCTION_MONITOR:
        return monitor_function_factory(**conf)
    elif monitor_type == Manager.CODE_MONITOR:
        return formated_code_monitoring(**conf)
    else:
        # If unknown, do not crash caller code
        logger = logging.getLogger('progressmonitor.config')
        msg = "Unknown monitor name '%s'. Skipping monitoring." % monitor_name
        logger.warning(msg)
        return IdProxy()

def get_generator_monitor(monitor_name, **kwargs):
    conf = get_config(monitor_name, **kwargs)
    return monitor_generator_factory(**conf)

def get_function_monitor(monitor_name, **kwargs):
    conf = get_config(monitor_name, **kwargs)
    return monitor_function_factory(**conf)

def get_code_monitor(monitor_name, **kwargs):
    conf = get_config(monitor_name, **kwargs)
    return formated_code_monitoring(**conf)



def parse_dict_config(config_dict):
    version = config_dict.get(Const.VERSION, 1)
    if version == 1:
        _dict_config_v1(config_dict)
    else:
        raise AttributeError("Version "+str(version)+" is not supported")


def parse_file_config(config_file):
    with open(config_file) as fp:
        config_dict = literal_eval(fp.read())
    parse_dict_config(config_dict)
