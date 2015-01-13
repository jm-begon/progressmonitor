# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"


import time
import os
try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread
from .util import (format_duration, format_size, fallback, 
                   call_with, nb_notifs_from_rate)



# ========================== LISTENER CLASS ========================== #

class ProgressListener(object):

    def __init__(self):
        self._hooks = []

    def add_hook(self, hook):
        self._hooks.append(hook)

    def hook(self, task, exception=None):
        for hook in self._hooks:
            hook(task, exception)

    def __call__(self, task, exception=None):
        self.hook(task, exception)



# ========================== SIMPLE FORMATING HOOK ========================== #

def taskname_hook_factory():
    def taskname_hook(task, exception=None):
        return "Task # "+str(task.id())+": "+task.name()
    return taskname_hook

def threadname_hook_factory():
    def threadname_hook(task, exception=None):
        thread = current_thread()
        return "Thread '" + thread.getName() + "' (id="+str(thread.ident)+")"
    return threadname_hook

def processid_hook_factory():
    def processid_hook(task, exception=None):
        return str(os.getpid())
    return processid_hook

def nb_iterations_hook_factory():
    def nb_iterations_hook(task, exception=None):
        nb_steps = task.nb_steps()
        if nb_steps is None:
            nb_steps = "???"
        return str(task.progress()) + "/" + str(nb_steps)
    return nb_iterations_hook


def exception_hook_factory(subsec_precision=2):
    def exception_hook(task, exception=None):
        msg = ""
        if exception is not None:
            duration = format_duration(task.duration(), subsec_precision)
            msg = "Aborted after "+duration+" (Reason: "+exception.message+")"
        return msg
    return exception_hook


@fallback(nb_iterations_hook_factory)
def progressbar_hook_factory(nb_notifs, fill="=", blank=".",
    format="[%(fill)s>%(blank)s] %(progress)s%%"):
    state = [0]
    def progressbar_hook(task, exception=None):
        # Running or completed
        progress = state[0]
        if exception is not None:
            # No real progress was achieved
            progress -= 1
        fill_ = fill * progress
        blank_ = blank * (nb_notifs - progress)
        prog_number = (float(progress) / nb_notifs)*100
        prog_str = "%.2f" % (prog_number)
        state[0] = progress + 1
        return format % {'fill': fill_, 'blank': blank_, 'progress': prog_str}

    return progressbar_hook

def completion_hook_factory(subsec_precision=2):
    def completion_hook(task, exception=None):
        msg = ""
        if task.is_completed() and exception is None:
            duration = format_duration(task.duration(), subsec_precision)
            msg = "Done in"+duration
        return msg
    return completion_hook


def elapsed_time_hook_factory(subsec_precision=2):
    def elapsed_time_hook(task, exception=None):
        duration = format_duration(task.duration(), subsec_precision)
        return "elapsed time: "+duration
    return elapsed_time_hook



@fallback(elapsed_time_hook_factory)
def remaining_time_hook_factory(length, decay_rate=0.1, 
                                subsec_precision=2, 
                                elapsed_time=True, total_time=True):
    state = dict()
    def remaining_time_hook(task, exception=None):
        progress = task.progress()
        msg = ""
        if progress == 0:
            state["timestamp"] = time.time()
            state["progress"] = progress
        else:
            timestamp = time.time()
            last_timestamp = state["timestamp"]
            last_progress = state["progress"]
            state["timestamp"] = last_timestamp
            state["progress"] = progress
            if elapsed_time:
                # Computing elapsed time
                duration = timestamp - task.timestamp()
                duration_str = format_duration(duration, subsec_precision)
                msg += "elapsed time: " + duration_str + " "
            if not (task.is_completed() or exception is not None):
                # Computing exponential average
                delta_r = progress - last_progress
                delta_t = timestamp - last_timestamp
                current_speed = delta_r/delta_t
                avg_speed = state.get("average_speed", current_speed)
                avg_speed = decay_rate*current_speed + (1-decay_rate)*avg_speed
                remaining_time = (length-progress)/avg_speed
                rem_t_str = format_duration(remaining_time, subsec_precision)
                msg += "remaining time (estimation): " + rem_t_str
                state["average_speed"] = avg_speed
                if total_time:
                    total_duration = remaining_time+duration
                    to_t_str = format_duration(total_duration, subsec_precision)
                    msg += " total time (estimation): " + to_t_str

        return msg

    return remaining_time_hook



def chunk_hook_factory(chunk_size, total_size=None):
    total_size_str = ["???"]
    if total_size is not None:
            total_size_str[0] = format_size(total_size)
    def chunck_hook(task, exception=None):
        progress = task.progress()
        if progress == 0 and total_size is None:
            # Trying to get an upper bound on the first call
            try:
                total_size_str[0] = format_size(len(task)*chunk_size)
            except AttributeError:
                pass
        prog_str = format_size(progress*chunk_size)
        if task.is_completed():
            return prog_str if total_size is None else total_size_str[0]
        return prog_str + "/" + total_size_str[0]
    return chunck_hook    



# ========================= COMPOSITE FORMATING HOOK ========================= #

def add_(factory, separator=" ", **kwargs):
    """
    Decorator which combines two formaters
    """
    format1 = call_with(factory, kwargs)
    def decorate(format2):
        def composite_hook(task, exception=None):
            return format1(task, exception)+separator+format2(task, exception)
        return composite_hook
    return decorate



def fullbar_hook_factory(callback, length, rate, 
                         decay_rate, **kwargs):

    nb_notifs = nb_notifs_from_rate(rate, length)

    # Establishing formating process
    @add_(taskname_hook_factory)
    @add_(progressbar_hook_factory, nb_notifs=nb_notifs, **kwargs)
    @add_(remaining_time_hook_factory, length=length, decay_rate=decay_rate, 
          **kwargs)
    @add_(exception_hook_factory, **kwargs)
    def format(task, exception=None):
        return ""


    # Main hook
    def fullbar_hook(task, exception=None):
        last_com = task.is_completed() or exception is not None
        callback(format(task, exception), last_com)

    return fullbar_hook


def chunkbar_hook_factory(callback, length, rate, chunk_size, 
                          total_size, decay_rate, **kwargs):

    nb_notifs = nb_notifs_from_rate(rate, length)

    # Establishing formating process
    @add_(taskname_hook_factory)
    @add_(progressbar_hook_factory, nb_notifs=nb_notifs, **kwargs)
    @add_(chunk_hook_factory, chunk_size=chunk_size, total_size=total_size)
    @add_(remaining_time_hook_factory, length=length, decay_rate=decay_rate,
          **kwargs)
    @add_(exception_hook_factory, **kwargs)
    def format(task, exception=None):
        return ""


    # Main hook
    def chunkbar_hook(task, exception=None):
        last_com = task.is_completed() or exception is not None
        callback(format(task, exception), last_com)

    return chunkbar_hook

def iterchunk_hook_factory(callback, chunk_size, total_size, **kwargs):
        
    # Establishing formating process
    @add_(taskname_hook_factory)
    @add_(chunk_hook_factory, chunk_size=chunk_size, total_size=total_size)
    @add_(elapsed_time_hook_factory, **kwargs)
    @add_(exception_hook_factory, **kwargs)
    def format_fallback(task, exception=None):
        return ""

    # Main hook
    def iterchunk_hook(task, exception=None):
        last_com = task.is_completed() or exception is not None
        callback(format_fallback(task, exception), last_com)

    return iterchunk_hook


# ====================== FORMATING HOOK FOR FUNCTIONS ====================== #
def func_str_hook_factory():
    def func_str_hook(task, monitored_func, exception=None):
        return str(monitored_func)
    return func_str_hook


def deblogger_hook_factory(multiline=False):
    def deblogger_hook(task, monitored_func, monitored_args, monitored_kwargs, 
                       exception=None):
        if task.progress() == 0:
            if multiline:
                msg = "Called:\n function: %s\n args: %r\n kwargs:%r\n"
                return msg % (str(monitored_func), monitored_args, 
                              monitored_kwargs)
            else:
                return "%s (args: %r  kwargs:%r)" % (str(monitored_func), 
                                                     monitored_args, 
                                                     monitored_kwargs)
        else:
            return str(monitored_func)
    return deblogger_hook


# ========================= STRING FORMATING HOOK ========================= #

def formated_hook_factory(callback, format_str, format_mapper):

    def formated_hook(task, exception=None, **kwargs):
        last_com = task.is_completed() or exception is not None
        val_dict = dict()
        for name, function_ in format_mapper.iteritems():
            val_dict[name] = call_with(function_, kwargs, task, 
                                       exception=exception)
        callback(format_str.format(**val_dict), last_com)

    return formated_hook






__hook_factories__ = {
    "$task" : taskname_hook_factory,
    "$thread" : threadname_hook_factory,
    "$pid" : processid_hook_factory,
    "$iteration" : nb_iterations_hook_factory,
    "$completion" : completion_hook_factory,
    "$progressbar" : progressbar_hook_factory,
    "$elapsed" : elapsed_time_hook_factory,
    "$time" : remaining_time_hook_factory,
    "$exception" : exception_hook_factory,
    "$chunk" : chunk_hook_factory,
    "$fname": func_str_hook_factory,
    "$deblogger": deblogger_hook_factory,
}

