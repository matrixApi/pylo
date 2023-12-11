from .core import cursesStart, cursesStop
from .utils import *


class cursesCore:
    # Note: curses routines follow.
    def __init__(self):
        self.cursesOn = cursesOn # staticmethod(cursesOn)
        self.cursesOff = self.noCurses = cursesOff # staticmethod(cursesOff)


@contextmanager
def withCurses():
    cursesStart()

    try: yield
    finally:
        cursesStop()

@contextmanager
def withoutCurses():
    cursesStop()

    try: yield
    finally:
        cursesStart()

def cursesOn(function):
    def usingCurses(*args, **kwd):
        with withCurses():
            return function(*args, **kwd)

    return usingCurses


def cursesOff(function):
    def notUsingCurses(*args, **kwd):
        with withoutCurses():
            return function(*args, **kwd)

    return notUsingCurses

noCurses = cursesOff
