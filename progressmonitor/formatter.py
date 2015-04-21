# -*- coding: utf-8 -*-
"""
Module :mod:`Formatter` contains several formatters. That is, pseudo-hook
which, based on the state of the task, return a string capturing some
of its aspect.

Formatters are assumed to be provided through factories so as to be stateful, 
parametrizable if need be and provide an homogenous building mechanism.

Formatters are hook-like, meaning thy have the form:
    Parameters
    ----------
    task : :class:`Task`
        The task to format
    exception : Exception (Default : None)
        The exception if one occured (None otherwise)
    Return
    ------
    string : str
        The formatted string

Formatters are usually used by hooks which transfert their output to
callback functions.
"""


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = '1.0'
__date__ = "08 January 2015"


import time
import os
import math
try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread
    
from .util import (format_duration, format_size, fallback)



# ============================= FORMATTER ============================== #

def taskname_formatter_factory():
    """
    Formatter factory

    Return
    ------
    :func:`taskname_formatter`
    """
    def taskname_formatter(task, exception=None):
        """
        Formatter

        Example
        -------
        Task # 0: do_task_monitoring
        """
        return "Task # "+str(task.id)+": "+task.name
    return taskname_formatter

def host_formatter_factory():
    """
    Formatter factory

    Return
    ------
    :func:`host_formatter`
    """
    def host_formatter(task, exception=None):
        """
        Formater

        Example
        -------
        foo@bar
        """
        try:
            import getpass
            import platform
            return getpass.getuser()+"@"+platform.node()
        except:
            return "n/a"
    return host_formatter

def threadname_formatter_factory(refresh=False):
    """
    Formatter factory

    Parameters
    ----------
    refresh : bool (Default : False)
        Whether to refresh the information at each notification

    Return
    ------
    :func:`format_thread
    """
    def format_thread():
        """
        Return
        ------
        string : str
            "Thread '<thread name>' (<thread id>)"
        """
        thread = current_thread()
        return "Thread '" + thread.getName() + "' (id="+str(thread.ident)+")"
    thread_ = format_thread()
    def threadname_formatter(task, exception=None):
        """
        Formatter

        Example
        -------
        Thread 'MainThread' (id=140735205905152)
        """
        if refresh:
            return thread_
        else:
            return format_thread()
    return threadname_formatter


def processid_formatter_factory(refresh=False):
    """
    Formatter factory

    Parameters
    ----------
    refresh : bool (Default : False)
        Whether to refresh the information at each notification

    Return
    ------
    :func:`processid_formatter`
    """
    pid = str(os.getpid())
    def processid_formatter(task, exception=None):
        """
        Formater returning the pid

        string : str
            The process id

        Example
        -------
        1827
        """
        if refresh:
            return pid
        else:
            return str(os.getpid())
    return processid_formatter


def nb_iterations_formatter_factory():
    """
    Formatter factory

    Return
    ------
    :func:`nb_iterations_formatter`
    """
    def nb_iterations_formatter(task, exception=None):
        """
        Formatter

        Return
        ------
        string : str
            the current number of iteration

        Example
        -------
        89/101
        """
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
    """
    Formatter factory

    Parameters
    ----------
    subsec_precision : int (Default : 2)
        The number of decimal digits for the second in the time formatting

    Return
    ------
    :func:`exception_formatter`
    """
    def exception_formatter(task, exception=None):
        """
        Formatter in case of exception

        Return
        ------
        string : str
            The formatted exception

        Example
        -------
        Aborted after 5.24 s (Reason: Broken generator)
        """
        msg = ""
        if exception is not None:
            duration = format_duration(task.duration, subsec_precision)
            msg = "Aborted after "+str(duration)+" (Reason: "+str(exception.message)+")"
        return msg
    return exception_formatter


@fallback(nb_iterations_formatter_factory)
def progressbar_formatter_factory(length, nb_steps=10, fill="=", blank=".",
    format="[%(fill)s>%(blank)s] %(progress)s%%"):
    """
    Formatter factory

    Parameters
    ----------
    length : int >= 0
        The size of the iterator
    nb_steps : int >= 0 (Default : 10)
        The number of steps in the progress bar
    fill : str (Defailt : "=")
        The filling char for the progress bar
    blank : str (Default : ".")
        The blank char for the progress bar
    format : srt (Default : "[%(fill)s>%(blank)s] %(progress)s%%")
        The format of the progress bar (fill, blank and progress are
        mandatory)

    Return
    ------
    :func:`progressbar_formatter`

    Fallback
    --------
    :func:`nb_iterations_formatter_factory`
    """
    # Length could be derived from the task but that would be to late
    # for the fallback
    threshold = int(math.ceil(float(length)/nb_steps))
    def progressbar_formatter(task, exception=None):
        """
        Formatter for progress bar

        Return
        ------
        string : str
            The formatted progress bar

        Example
        -------
        [========>..] 86.27%
        """
        if task.is_completed or length == 0:
            # fill the whole bar
            fill_ = fill * nb_steps
            blank_ = ""
            prog_str = "100"
        else:
            # fill must be computed
            filled = task.progress // threshold
            fill_ = fill * filled
            blank_ = blank * (nb_steps - filled)
            prog_number = (float(task.progress) / length)*100
            prog_str = "%.2f" % (prog_number)

        return format % {'fill': fill_, 'blank': blank_, 'progress': prog_str}

    return progressbar_formatter

def completion_formatter_factory(subsec_precision=2):
    """
    Formatter factory

    Parameters
    ----------
    subsec_precision : int (Default : 2)
        The number of decimal digits for the second in the time formatting

    Return
    ------
    :func:`completion_formatter`
    """
    def completion_formatter(task, exception=None):
        """
        Formatter for completion time. 

        Return
        ------
        string : str
            The elasped time at the task completion or an empty string

        Example
        -------
        Done in 5.65 s
        """
        msg = ""
        if task.is_completed and exception is None:
            duration = format_duration(task.duration, subsec_precision)
            msg = "Done in "+duration
        return msg
    return completion_formatter


def elapsed_time_formatter_factory(subsec_precision=2):
    """
    Formatter factory

    Parameters
    ----------
    subsec_precision : int (Default : 2)
        The number of decimal digits for the second in the time formatting

    Return
    ------
    :func:`elapsed_time_formatter`
    """
    def elapsed_time_formatter(task, exception=None):
        """
        Formatter for completion time

        Return
        ------
        string : str
            The elasped time so far

        Example
        -------
        elasped time: 7.43 s
        """
        duration = format_duration(task.duration, subsec_precision)
        return "elapsed time: "+duration
    return elapsed_time_formatter



@fallback(elapsed_time_formatter_factory)
def remaining_time_formatter_factory(length, decay_rate=0.1, 
                                subsec_precision=2, 
                                elapsed_time=True, total_time=True):
    """
    Formatter factory. Estimate the remaining and total time of the task
    by exponential moving average.

    Parameters
    ----------
    length : int
        The size of the iterator
    decay_rate : float 0 <= decay_rate <= 1
        The decay rate for the exponetial moving average (alpha parameter)
    subsec_precision : int (Default : 2)
        The number of decimal digits for the second in the time formatting
    elapsed_time : bool (Default : True)
        Whether to indicate the elapsed time
    total_time : bool (Default : True)
        Whether to indicate the total time

    Fallback
    --------
    :func:`elapsed_time_formatter_factory`

    Return
    ------
    :func:`remaining_time_formatter`
    """
    # Length could be derived from the task but that would be to late
    # for the fallback
    state = dict()
    def remaining_time_formatter(task, exception=None):
        """
        Formatter which indicates the elapsed, remaining and total time.
        The remaining/total time is estimated by exponential moving average

        Return
        ------
        string : str
            The elasped/remaining/total time so far

        Example
        -------
        elapsed time: 4.52s remaining time (estimation): 7.20s total time
        (estimation): 11.72s
        """
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
    """
    Formatter factory for data process in bytes

    Parameters
    ----------
    chunk_size : int >= 0
        The chunk size in bytes
    total_size : int or None (Default : None)
        The total size (in bytes) of the data to process or None. If None,
        the total size will be infered (if possible) from the size of the
        iterator (as len(gen)*chunk_size)

    Return
    ------
    :func:`chunck_formatter`
    """
    total_size_str = ["???"]
    if total_size is not None:
        total_size_str[0] = format_size(total_size)

    def chunck_formatter(task, exception=None):
        """
        Formatter which indicates the number of bytes treated so far

        Return
        ------
        string : str
            The number of bytes treader so far

        Example
        -------
        10.8 kB/14.1 kB
        """
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
    """
    Meta formatter : a formater based on other formater

    Parameters
    ----------
    format_str : str
        The formatting string with place holder to be replaced.
    format_mapper : dict
        The dictionary containing the mapping placeholder - formatter

    Return
    ------
    :func:`format_string_formatter`
    """

    def format_string_formatter(task, exception=None):
        """
        Meta formatter

        Return
        ------
        string : str
            The formatted result

        Example
        -------
        format_str = {$thread} {$task} {$progressbar} {$time} {$exception}

        Thread 'MainThread' (id=140735231197952) Task # 0: Lengthy 
        [=========> ] 97.06% elapsed time: 10.18s 
        remaining time (estimation): 0.56s total time (estimation): 10.74s 
        """
        val_dict = dict()
        for name, str_formatter in format_mapper.iteritems():
            val_dict[name] = str_formatter(task, exception)
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

