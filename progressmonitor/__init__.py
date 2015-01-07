# -*- coding: utf-8 -*-
"""
Main package (progress monitor)
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'




from .monitor import (Task, ProgressableTask, monitor_progress,
					  format_duration, format_size)
from .progressbar import span_progressbar, rate_progressbar

__all__ = ["Task", "ProgressableTask", "monitor_progress", "format_duration", 
		   "format_size", "span_progressbar", "rate_progressbar"]
