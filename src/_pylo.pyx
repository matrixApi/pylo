cdef extern from 'LYCurses.h':
    cdef void start_curses()
    cdef void stop_curses()

cdef extern from 'LYStrings.h':
    cdef int _lynx_LYgetch "LYgetch" ()


HT_NOT_LOADED   = 0
HT_LOADED       = 1

FOR_PANEL       = 0
FOR_CHOICE      = 1
FOR_INPUT       = 2
FOR_PROMPT      = 3
FOR_SINGLEKEY   = 4


def cursesStart():
    start_curses()
def cursesStop():
    stop_curses()


bindingsModule = None

def bindingsLoad(api):
    # Note: using -rdynamic
    pass


def statusline(message):
    pass
def htUserMsg(message):
    pass
def htInfoMsg(message):
    pass
def htAlert(message):
    pass
def htConfirm(message):
    pass


def LYgetch_for():
    '''
    FOR_PANEL
    FOR_CHOICE
    FOR_INPUT
    FOR_PROMPT
    FOR_SINGLEKEY

    '''

    pass

def LYgetch():
    return _lynx_LYgetch()
def LYgetBString(hidden, max_cols, recall):
    pass


class HTTextObject:
    def activateMain(self):
        pass

def getHTMainTextObject():
    return HTTextObject()


def loadDocumentAddress(*args):
    pass
def loadHTMLString(string, url):
    pass
