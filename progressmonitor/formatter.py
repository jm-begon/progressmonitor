# -*- coding: utf-8 -*-
"""
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"


import time
import os
import getpass
import platform
try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread
from .util import (format_duration, format_size, fallback)



# ============================= FORMATTER ============================== #

def taskname_formatter_factory():
    def taskname_formatter(task, exception=None, **kwargs):
        return "Task # "+str(task.id)+": "+task.name
    return taskname_formatter

def host_formatter_factory(refresh=False):
    def get_host():
        return getpass.getuser()+"@"+platform.node()

    host = get_host()
    def host_formatter(task, exception=None, **kwargs):
        if refresh:
            return host
        else:
            return get_host()
    return host_formatter

def threadname_formatter_factory(refresh=False):
    def format_thread():
        thread = current_thread()
        return "Thread '" + thread.getName() + "' (id="+str(thread.ident)+")"
    thread_ = format_thread()
    def threadname_formatter(task, exception=None, **kwargs):
        if refresh:
            return thread_
        else:
            return format_thread()
    return threadname_formatter

def processid_formatter_factory(refresh=False):
    pid = str(os.getpid())
    def processid_formatter(task, exception=None, **kwargs):
        if refresh:
            return pid
        else:
            return str(os.getpid())
    return processid_formatter


def nb_iterations_formatter_factory():
    def nb_iterations_formatter(task, exception=None, **kwargs):
        if task.is_completed or exception is not None:
            nb_steps = str(task.progress)
        else:
            nb_steps = task.nb_steps 
            if nb_steps is None:
                nb_steps = "???"
            else:
                nb_steps = str(nb_steps - 1)
        return str(task.progress) + "/" + nb_steps
    return nb_iterations_formatter


def exception_formatter_factory(subsec_precision=2):
    def exception_formatter(task, exception=None, **kwargs):
        msg = ""
        if exception is not None:
            duration = format_duration(task.duration, subsec_precision)
            msg = "Aborted after "+duration+" (Reason: "+exception.message+")"
        return msg
    return exception_formatter


@fallback(nb_iterations_formatter_factory)
def progressbar_formatter_factory(nb_notifs, fill="=", blank=".",
    format="[%(fill)s>%(blank)s] %(progress)s%%"):
    state = [0]
    def progressbar_formatter(task, exception=None, **kwargs):
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

    return progressbar_formatter

def completion_formatter_factory(subsec_precision=2):
    def completion_formatter(task, exception=None, **kwargs):
        msg = ""
        if task.is_completed and exception is None:
            duration = format_duration(task.duration, subsec_precision)
            msg = "Done in "+duration
        return msg
    return completion_formatter


def elapsed_time_formatter_factory(subsec_precision=2):
    def elapsed_time_formatter(task, exception=None, **kwargs):
        duration = format_duration(task.duration, subsec_precision)
        return "elapsed time: "+duration
    return elapsed_time_formatter



@fallback(elapsed_time_formatter_factory)
def remaining_time_formatter_factory(length, decay_rate=0.1, 
                                subsec_precision=2, 
                                elapsed_time=True, total_time=True):
    state = dict()
    def remaining_time_formatter(task, exception=None, **kwargs):
        progress = task.progress
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
                duration = timestamp - task.timestamp
                duration_str = format_duration(duration, subsec_precision)
                msg += "elapsed time: " + duration_str + " "
            if not (task.is_completed or exception is not None):
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

    return remaining_time_formatter



def chunk_formatter_factory(chunk_size, total_size=None):
    total_size_str = ["???"]
    if total_size is not None:
        total_size_str[0] = format_size(total_size)

    def chunck_formatter(task, exception=None, **kwargs):
        progress = task.progress
        if progress == 0 and total_size is None:
            # Trying to get an upper bound on the first call
            try:
                total_size_str[0] = format_size(len(task)*chunk_size)
            except AttributeError:
                pass
        prog_str = format_size(progress*chunk_size)
        if task.is_completed:
            return prog_str if total_size is None else total_size_str[0]
        return prog_str + "/" + total_size_str[0]
    return chunck_formatter    




# ========================= META FORMATTER ========================== #


def string_formatter_factory(format_str, format_mapper):

    def format_string_formatter(task, exception=None, **kwargs):
        val_dict = dict()
        for name, str_formatter in format_mapper.iteritems():
            val_dict[name] = str_formatter(task, exception, **kwargs)
        return format_str.format(**val_dict)

    return format_string_formatter







__formatter_factories__ = {
    "$task" : taskname_formatter_factory,
    "$host": host_formatter_factory,
    "$thread" : threadname_formatter_factory,
    "$pid" : processid_formatter_factory,
    "$iteration" : nb_iterations_formatter_factory,
    "$completion" : completion_formatter_factory,
    "$progressbar" : progressbar_formatter_factory,
    "$elapsed" : elapsed_time_formatter_factory,
    "$time" : remaining_time_formatter_factory,
    "$exception" : exception_formatter_factory,
    "$chunk" : chunk_formatter_factory,
    
}

