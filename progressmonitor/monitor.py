# -*- coding: utf-8 -*-
"""
A helper module for monitoring progresses
"""
from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"


import time
import math

# ============================== TASK ============================== #
class Task(object):
    """
    ================
    ProgressableTask
    ================
    A :class:`ProgressableTask` represents a task composed of several steps


    Class attributes
    ----------------
    nb_tasks : int
        The number of already created tasks (not thread-safe)

    Class constants
    ---------------
    READY : int 
        State of a ready but not yet running task
    RUNNING : int
        State of a running task
    DONE : int
        State of a completed task
    ABORTED : int
        State of a aborted task


    Constructor parameters
    ----------------------
    nb_steps : int or None
        The number of step before completion. Supply None is this is unknown
    name : str
        The name of the task
    """

    nb_tasks = 0

    READY = 0
    RUNNING = 1
    DONE = 2
    ABORTED = 3

    def __init__(self, nb_steps, name=None):

        self._id = Task.nb_tasks
        Task.nb_tasks += 1

        if name is None:
            name = "Unnamed_task."+str(self._id)
        self._name = name

        self._nb_steps = nb_steps
        self._progress = 0
        self._status = Task.READY
        self._end_time = None
        self._start_time = time.time()

    def id(self):
        """
        Return
        ------
        id : int
            The id of the task
        """
        return self._id

    def name(self):
        """
        Return
        ------
        name : str
            The name of the task
        """
        return self._name

    def status(self):
        """
        Return
        ------
        status : int in {Task.READY, Task.RUNNING, Task.DONE, Task.ABORTED}
            The status of the task
        """
        return self._status

    def nb_steps(self):
        """
        Returns
        -------
        nb_steps : int
            The number of steps required by the task
        """
        return self._nb_steps

    def __len__(self):
        steps = self.nb_steps()
        if steps is None:
            raise AttributeError("Unbounded task")
        return steps

    def duration(self):
        """
        Return
        ------
        duration : float
            the duration of task in seconds (up to now if still running,
            up to completion if completed)
        """
        if self._status == Task.DONE:
            return self._end_time - self._start_time
        else:
            return time.time() - self._start_time

    def progress(self):
        """
        Return
        ------
        progress : int
            The progress so far
        """
        return self._progress

    def is_completed(self):
        """
        Return
        ------
        is_completed : bool
            Whether the task is completed (Task.DONE) or not
        """
        return self._status == Task.DONE

    def timestamp(self):
        """
        Return
        ------
        timestamp : float
            The timestamp of the creation time
        """
        return self._start_time

    def __str__(self):
        length = self.nb_steps()
        length = str(length) if length is not None else "???"
        status = self.status()
        if status == Task.READY:
            status = "is ready"
        elif status == Task.RUNNING:
            status = "is running"
        elif status == Task.DONE:
            status = "is completed"
        elif status == Task.ABORTED:
            status = "has been aborted"
        else:
            status = "unknown status"
        desc = "Task #%d '%s' (%d/%s) %s." % (self.id(), self.name(), 
                                              self.progress(), length, status)
        return desc


class ProgressableTask(Task):
    """
    ================
    ProgressableTask
    ================

    A :class:`Task` which can be run
    """

    def __init__(self, nb_steps, name=None):
        Task.__init__(self, nb_steps, name)


    def start(self):
        """
        (Re)Start the task
        """
        self._progress = 0
        self._status = Task.RUNNING
        self._end_time = None
        self._start_time = time.time()


    def update(self, progress):
        """
        Update progress (if task is running)

        Parameters
        ----------
        progress : int
            the new progression score

        Return
        ------
        done : boolean
            True if the task is completed, False otherwise
        """
        if self._status > Task.RUNNING:
            return self.is_completed()
        self._status = Task.RUNNING
        self._progress = progress
        if self._nb_steps is None:
            return False

        return progress >= self._nb_steps

    def close(self, finished=True):
        """
        Ends the task

        Parameters
        ----------
        finished : boolean (Default : True)
            Whether the task has finished its excution correctly
        """
        if finished:
            self._status = Task.DONE
        else:
            self._status = Task.ABORTED
        self._end_time = time.time()


    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if value is None:
            is_done = ((self._nb_steps is None) or 
                       (self._progress >= self._nb_steps))
            self.close(is_done)
        else:
            self.close(False)
        # Let the exception propagate, if any
        return False





# =========================== NOTIFICATION RULES =========================== #

def always_notify_rule(_):return True

def span_notify_rule(span=1):
    """
    Indicates whether to notify or not base on a span
    Parameters
    ----------
    span : int (Default : 1)
        The number of iteration to span without notifying

    Return
    ------
    span_update : callable (int)
        A function wi
    """
    return lambda task: (False if task.progress() == 0 else 
                                (task.progress() % span == 0))


def periodic_notify_rule(frequency):
    last_update=[time.time()]
    def periodic_update(_):
        now = time.time()
        if (now - last_update[0]) >= frequency:
            last_update[0] = now
            return True
        return False
    return periodic_update


def rate_notify_rule(rate, length):
    last_update = [0]
    def rate_update(task):
        progress = task.progress()
        delta = (float(progress - last_update[0])/length)
        if delta >= rate:
            last_update[0] = progress
            return True
        return False
    return rate_update


def rate_rule_and_nb_notifs(rate, length):
    nb_notifs = int(math.ceil(1./rate))
    return rate_notify_rule(rate, length), nb_notifs






# ============================ PROGRESS MONITOR ============================ #

def monitor_progress(generator, hook, name=None, 
                     should_notify=always_notify_rule):

    """
    Generator decorator for monitoring progress on another generator.

    Parameters
    ----------
    generator : Generator
        The generator to monitor
    hook : callable (:class:`Task`, [exception])
        A hook on which to register progress. It must have
        - one mandatory argument which is a :class:`Task`instance
        - one optional argument which is an exception istance in
        case an error occured
    name : str or None (Default : None)
        The  name of the task. If None, a default name will be provided
    should_notify : callable (:class:`Task`) --> bool
        The notification rule. A function which takes as input the task
        and decide whether to notify (return True) or not (return False)

    Warning
    -------
    Needless to say that this function produces overhead. Use it with care.
    """
    length = None
    try:
        length = len(generator)
    except (AttributeError, TypeError):
        pass

    # Creating the task
    try:
        task = ProgressableTask(length, name)
        task.start()
        progress = 0
        # Log the start of the task
        hook(task)
        # Running the decorated generator
        
        for elem in generator:
            # log the iterations of the task
            if not task.update(progress):
                # Task is still in progress
                # Notifiyng the message if necessary
                if should_notify(task):
                    hook(task)
            # Yield the element
            yield elem
            # Increment the progress
            progress += 1
        # Ends the task
        task.close(True)
        # Notify last progress
        hook(task)
    except Exception as excep:
        # Ends the task
        task.close(False)
        # Notify last progress
        hook(task, excep)
        raise



# ============================== FORMATER ============================== #

def format_duration(duration, subsec_precision=2):
    """
    Format the duration expressed in seconds as string

    Parameters
    ----------
    duration : float
        a duration in seconds

    subsec_precision : int (>=0)
        the number of decimal for the second part of the duration
    Return
    ------
    formated : str
        the given duration formated

    Example
    -------
    >>> days = 1
    >>> hours = 4
    >>> minutes = 52
    >>> seconds = 23
    >>> duration = seconds + 60*(minutes + 60*(hours + 24*days))
    >>> format_duration(duration)
    '1d 4h 52m 23s'
    """
    sec = duration % 60
    excess = int(duration) // 60  # minutes
    res = (("%."+str(subsec_precision)+"f %s") % (sec, "s"))
    if excess == 0:
        return res
    minutes = excess % 60
    excess = excess // 60  # hours
    res = str(minutes) + "m " + res
    if excess == 0:
        return res
    hour = excess % 24
    excess = excess // 24  # days
    res = str(hour) + "h " + res
    if excess == 0:
        return res
    res = str(excess)+"d " + res
    return res


def format_size(nb_bytes):
    """
    Format a size expressed in bytes as a string

    Parameters
    ----------
    nb_bytes : int
        the number of bytes

    Return
    ------
    formated : str
        the given number of bytes fromated

    Example
    -------
    >>> format_size(100)
    '100.0 bytes'
    >>> format_size(1000)
    '1.0 kB'
    >>> format_size(1000000)
    '1.0 MB'
    >>> format_size(1000000000)
    '1.0 GB'
    >>> format_size(1000000000000)
    '1.0 TB'
    >>> format_size(1000000000000000000)
    '1000000.0 TB'

    """
    for x in ['bytes', 'kB', 'MB', 'GB']:
        if nb_bytes < 1000.0:
            return "%3.1f %s" % (nb_bytes, x)
        nb_bytes /= 1000.0
    return "%3.1f %s" % (nb_bytes, 'TB')






# ============================== FORMATING HOOK ============================== #


def format_task(task, exception=None):
    return "Task # "+str(task.id())+": "+task.name()

def format_thread(task, exception=None):
    try:
        from threading import current_thread
    except ImportError:
        from threading import currentThread as current_thread
    thread = current_thread()
    return "Thread '" + thread.getName() + "' (id="+str(thread.ident)+")"

def format_process(task, exception=None):
    import os
    return str(os.getpid())

def format_iteration(task, exception=None):
    nb_steps = task.nb_steps()
    if nb_steps is None:
        nb_steps = "???"
    return str(task.progress()) + "/" + str(nb_steps)

def chunk_formater(chunk_size, total_size=None):
    total_size_str = ["???"]
    if total_size is not None:
            total_size_str[0] = format_size(total_size)
    def format_chunck(task, exception=None):
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
    return format_chunck


def exception_handler_formater(subsec_precision=2, *args, **kwargs):
    def format_exception(task, exception=None):
        msg = ""
        if exception is not None:
            duration = format_duration(task.duration(), subsec_precision)
            msg = "Aborted after "+duration+" (Reason: "+exception.message+")"
        return msg
    return format_exception



def progressbar_formater(nb_notifs, fill="=", blank=".",
    format="[%(fill)s>%(blank)s] %(progress)s%%", *args, **kwargs):

    state = [0]
    def format_(task, exception=None):
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


    return format_

def done_in_formater(subsec_precision=2, *args, **kwargs):
    def format_completion(task, exception=None):
        msg = ""
        if task.is_completed() and exception is None:
            duration = format_duration(task.duration(), subsec_precision)
            msg = "Done in"+duration
        return msg
    return format_completion

def elapsed_time_formater(subsec_precision=2, *args, **kwargs):
    def format_elapsed_time(task, exception=None):
        duration = format_duration(task.duration(), subsec_precision)
        return "elapsed time: "+duration
    return format_elapsed_time

def remaining_time_formater(length, decay_rate=0.1, 
                            subsec_precision=2, 
                            elapsed_time=True, total_time=True, 
                            *args, **kwargs):
    state = dict()
    def format_remaining_time(task, exception=None):
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

    return format_remaining_time


    



def add_(format1):
    """
    Decorator which combines two formater
    """
    return lambda format2: lambda task, exception=None: format1(task, exception)+" "+format2(task, exception)



def rate_format_factory(callback, length, nb_notifs, 
                        decay_rate, *args, **kwargs):

    # Establishing formating process
    @add_(format_task)
    @add_(progressbar_formater(nb_notifs, *args, **kwargs))
    @add_(remaining_time_formater(length, decay_rate, *args, **kwargs))
    @add_(exception_handler_formater(*args, **kwargs))
    def format(task, exception=None):
        return ""


    # Main hook
    def hook(task, exception=None):
        last_com = task.is_completed() or exception is not None
        callback(format(task, exception), last_com)

    return hook


def rate_chunk_format_factory(callback, length, nb_notifs, chunk_size, 
                              total_size, decay_rate, *args, **kwargs):

    # Establishing formating process
    @add_(format_task)
    @add_(progressbar_formater(nb_notifs, *args, **kwargs))
    @add_(chunk_formater(chunk_size, total_size))
    @add_(remaining_time_formater(length, decay_rate, *args, **kwargs))
    @add_(exception_handler_formater(*args, **kwargs))
    def format(task, exception=None):
        return ""


    # Main hook
    def hook(task, exception=None):
        last_com = task.is_completed() or exception is not None
        callback(format(task, exception), last_com)

    return hook

def span_chunk_format_factory(callback, chunk_size, total_size, *args, **kwargs):
        
    # Establishing formating process
    @add_(format_task)
    @add_(chunk_formater(chunk_size, total_size))
    @add_(elapsed_time_formater(*args, **kwargs))
    @add_(exception_handler_formater(*args, **kwargs))
    def format_fallback(task, exception=None):
        return ""

    # Main hook
    def hook(task, exception=None):
        last_com = task.is_completed() or exception is not None
        callback(format_fallback(task, exception), last_com)

    return hook

def format_from_string(callback, format_str, func_mapper):

    def hook(task, exception=None):
        last_com = task.is_completed() or exception is not None
        val_dict = dict()
        for name, function in func_mapper.iteritems():
            val_dict[name] = function(task, exception)
        callback(format_str.format(**val_dict), last_com)

    return hook












