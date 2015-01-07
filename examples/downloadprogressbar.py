# -*- coding: utf-8 -*-
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

from progressmonitor.progressbar import chunck_progressbar

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

    def get_total_size(self):
        return self._total_size

    def get_chunk_size(self):
        return self._chunk_size


if __name__ == '__main__':
    span = 1
    rate = 0.1
    decay_rate = 0.1

    chunk_size = 256
    url = "http://www.google.com/images/srpr/logo11w.png"


    with Chunker(url, chunk_size) as  chunker:
        print "Chuncker length:", len(chunker)
        print "Chuncker total size:", chunker.get_total_size()
        for chunk in chunck_progressbar(chunker, chunk_size, 
                                        chunker.get_total_size(), 
                                        rate, span, decay_rate):
            time.sleep(0.1)

