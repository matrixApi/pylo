from queue import Queue, Empty
from contextlib import contextmanager
from traceback import print_exc

from os import getenv
from os.path import exists

from urllib.parse import urlparse, parse_qsl


class LineInput:
    def __init__(self, line):
        self.line = line

def fronting(function):
    def create(*args, **kwd):
        def front(*f_args, **f_kwd):
            return function(*(args + f_args),
                            **dict(kwd, **f_kwd))
        return front
    return create

def parseUrl(address):
    r = urlparse(address)
    return (r, dict(parse_qsl(r.query)))
