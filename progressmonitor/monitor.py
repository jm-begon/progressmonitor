# -*- coding: utf-8 -*-
"""
The :mod:`progressmonitor.monitor` module is progressmonitor's main module.
It provides library users with methods to monitor:
    - iterators/generators (:func:`monitor_progress`)
    - functions (:func:`monitor_function`)
    - piece of code (:func:`monitor_code`)
"""
from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'
__date__ = "08 January 2015"


import time
from functools import partial

from .rule import always_notif_rule_factory

# ============================== TASK ============================== #
class Task(object):
    """
    ====
    Task
    ====
    A :class:`Task` represents a task composed of several steps


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

    @property
    def id(self):
        """
        Return
        ------
        id : int
            The id of the task
        """
        return self._id

    @property
    def name(self):
        """
        Return
        ------
        name : str
            The name of the task
        """
        return self._name

    @property
    def status(self):
        """
        Return
        ------
        status : int in {Task.READY, Task.RUNNING, Task.DONE, Task.ABORTED}
            The status of the task
        """
        return self._status

    @property
    def nb_steps(self):
        """
        Returns
        -------
        nb_steps : int
            The number of steps required by the task
        """
        return self._nb_steps

    def __len__(self):
        steps = self.nb_steps
        if steps is None:
            raise AttributeError("Unbounded task")
        return steps

    @property
    def duration(self):
        """
        Return
        ------
        duration : float
            the duration of task in seconds (up to now if still running,
            up to completion if completed)
        """
        if self._status == Task.DONE or self._status == Task.ABORTED:
            return self._end_time - self._start_time
        else:
            return time.time() - self._start_time

    @property
    def progress(self):
        """
        Return
        ------
        progress : int
            The progress so far
        """
        return self._progress

    @property
    def is_completed(self):
        """
        Return
        ------
        is_completed : bool
            Whether the task is completed (Task.DONE) or not
        """
        return self._status == Task.DONE

    @property
    def timestamp(self):
        """
        Return
        ------
        timestamp : float
            The timestamp of the creation time
        """
        return self._start_time

    def __str__(self):
        length = self.nb_steps
        length = str(length) if length is not None else "???"
        status = self.status
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
        desc = "Task #%d '%s' (%d/%s) %s." % (self.id, self.name, 
                                              self.progress, length, status)
        return desc


class ProgressableTask(Task):
    """
    ================
    ProgressableTask
    ================

    A :class:`Task` which can be run.
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
            return self.is_completed
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









# ============================ PROGRESS MONITOR ============================ #

def monitor_generator(generator, hook, task_name=None, 
                     should_notify=always_notif_rule_factory()):

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
    task_name : str or None (Default : None)
        The  name of the task. If None, a default name will be provided
    should_notify : callable (:class:`Task`) --> bool
        The notification rule. A function which takes as input the task
        and decide whether to notify (return True) or not (return False)

    Yield
    -----
    The elements of the given generator

    Exception
    ---------
    Exceptions are not swallowed
    """
    length = None
    try:
        length = len(generator)
    except (AttributeError, TypeError):
        pass

    # Creating the task
    try:
        task = ProgressableTask(length, task_name)
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
        hook(task=task)
    except Exception as excep:
        # Ends the task
        task.close(False)
        # Notify last progress
        hook(task, excep)
        raise




def monitor_function(function, hook, task_name=None, *args, **kwargs):
    """
    Monitor the given function. That is, submit two events to the hook:
        - Task creation
        - Task end (either completion or interruption)

    Parameters
    ----------
    function : callable 
        The function to monitor
    hook : callable (:class:`Task`, [exception])
        A hook on which to register progress. It must have
        - one mandatory argument which is a :class:`Task`instance
        - one optional argument which is an exception istance in
        case an error occured
    task_name : str or None (Default : None)
        The  name of the task. If None, a default name will be provided
    *args :
        The positional arguments to call the function with
    **kwargs :
        The keyword arguments to call the function with

    Return
    ------
    result : 
        The result of the function(*args, **kwargs) call

    Exception
    ---------
    Exceptions are not swallowed
    """
    # Task will only last one call
    task = ProgressableTask(1, task_name)
    hook_kwargs = {
        "monitored_func": function,
        "monitored_args": args,
        "monitored_kwargs": kwargs,
        "monitored_result": None,
    }
    try:
        #Initial hook call
        hook(task, None, **hook_kwargs)

        result = function(*args, **kwargs)
        hook_kwargs["monitored_result"] = result
        # Ends the task
        task.update(1)
        task.close(True)
        # Notify last progress
        hook(task, None, **hook_kwargs)

    except Exception as excep:
        # Ends the task
        task.close(False)
        # Notify last progress
        hook(task, excep, **hook_kwargs)
        raise

    return result





class CodeMonitor(object):
    """
    ===========
    CodeMonitor
    ===========
    A class:`CodeMonitor` is a context manager for monitoring pieces
    of code

    Constructor parameters
    ----------------------
    hook : callable (:class:`Task`, [exception])
        A hook on which to register progress. It must have
        - one mandatory argument which is a :class:`Task`instance
        - one optional argument which is an exception istance in
        case an error occured
    task_name : str or None (Default : None)
        The  name of the task. If None, a default name will be provided

    Exception
    ---------
    Exceptions are not swallowed

    Usage
    -----
    with CodeMonitor(hook=hook, task_name=name):
        # compute stuff

    Yes, it's that easy !
    """

    def __init__(self, hook, task_name=None):
        self._hooks = [hook]
        self.task = ProgressableTask(1, task_name)

    def add_hooks(self, hook):
        self._hooks.append(hook)

    def start(self):
        self.task.start()
        for hook in self._hooks:
            hook(self.task, None)

    def stop(self, finished=True, exception=None):
        self.task.close(finished)
        for hook in self._hooks:
            hook(self.task, exception)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if value is None:
            is_done = ((self.task.nb_steps is None) or 
                       (self.task.progress >= self.task.nb_steps))
            self.stop(is_done)
        else:
            # Exception
            self.stop(False, value)
        # Let the exception propagate, if any
        return False


def monitor_code(hook, task_name=None):
    """
    Provide a context manager to monitor code blocks.

    Parameters
    ----------
    hook : callable (:class:`Task`, [exception])
        A hook on which to register progress. It must have
        - one mandatory argument which is a :class:`Task`instance
        - one optional argument which is an exception istance in
        case an error occured
    task_name : str or None (Default : None)
        The  name of the task. If None, a default name will be provided

    Return
    ------
    code_monitor : :class:`CodeMonitor`
        the context manager
    """
    # Provided for aesthetic reasons
    return CodeMonitor(hook, task_name)
