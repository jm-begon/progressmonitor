# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
Basic example of rate progress bar
"""

from __future__ import generators

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "3-clause BSD License"
__version__ = 'dev'

import time
import math
try:
    # Python 2
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen
except ImportError:
    # Python 3+
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen

from progressmonitor import monitor_with, dict_config

class Chunker:

    def __init__(self, url, chunk_size=8192):
        self._url = url
        self._response = None
        self._size = None
        self._total_size = None
        self._chunk_size = chunk_size

    def __enter__(self):
        self._response = urlopen(self._url)
        return self

    def __exit__(self, type, value, traceback):
        self._response.close()
        self._response = None
        # Let the exception propagate
        return False

    def __len__(self):
        if self._response is None:
            raise AttributeError("URL not opened yet")
        if self._size is None:
            tmp = self._response.info().getheader('Content-Length').strip()
            self._total_size = int(tmp)
            self._size = int(math.ceil(float(tmp)/self._chunk_size))
        return self._size

    def __iter__(self):
        if self._response is None:
            raise StopIteration("URL not opened")
        while True:
            chunk = self._response.read(self._chunk_size)
            if not chunk:
                raise StopIteration()
            yield chunk

    @property
    def total_size(self):
        return self._total_size

    @property
    def chunk_size(self):
        return self._chunk_size


if __name__ == '__main__':
    rate = 0.1
    decay_rate = 0.1

    chunk_size = 256
    url = "http://www.google.com/images/srpr/logo11w.png"

    format_str = "{$progressbar} {$chunk} {$time} {$exception}"


    config = {
        "version": 1,
        "generator_monitors": {
            "chunker": {
                "format_str": format_str,
                "chunk_size": chunk_size,
                "decay_rate": decay_rate,
                "rate": rate,
            },
        }
    }

    dict_config(config)


    with Chunker(url, chunk_size) as  chunker:
        print "Chuncker length:", len(chunker)
        print "Chuncker total size:", chunker.total_size
        for chunk in monitor_with("chunker")(chunker):
            time.sleep(0.1)

