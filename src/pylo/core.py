# API
import _pylo
from _pylo import *


from .utils import *
from .pyloCurses import * # do after importing from _pylo into this module.
from .provisional import provisionalCore


def load_unified():
    # Use this on systems that support -rdynamic
    return pyloCore(_pylo)

def load(api):
    # bindingsLoad is _pylo native method, api is the back-linked CPointerObject wrapper
    # that is installed into the native data scope.
    # return pyloCore(bindingsLoad(api))

    # print 'loading'
    # raw_input()

    import _pylo as bindingsModule
    bindingsLoad(api) # backlink when -rdynamic not available or used
    return pyloCore(bindingsModule)


class v1apiCore:
    def keyCode(self):
        # default provider for generateInput command cycle extension.
        return self.bindings.LYgetch()
        return self.keyCodePanel()


    def keyCodePanel(self):
        # normal screen, also LYgetch default
        return self.bindings.LYgetch_for(self.bindings.FOR_PANEL)
    def keyCodeChoice(self):
        # mouse menu - LYgetch_choice
        return self.bindings.LYgetch_for(self.bindings.FOR_CHOICE)
    def keyCodeInput(self):
        # form input and textarea field - LYgetch_input
        return self.bindings.LYgetch_for(self.bindings.FOR_INPUT)
    def keyCodePrompt(self):
        # string prompt editing
        return self.bindings.LYgetch_for(self.bindings.FOR_PROMPT)
    def keyCodeSingle(self):
        # single key prompt, confirmation - LYgetch_single
        return self.bindings.LYgetch_for(self.bindings.FOR_SINGLEKEY)


    @cursesOn # ?
    def lineStatus(self, message):
        return self.bindings.statusline(message)

    # @cursesOn # ?
    def userMessage(self, message):
        return self.bindings.htUserMsg(message)

    # @cursesOn # ?
    def infoMessage(self, message):
        return self.bindings.htInfoMsg(message)

    # @cursesOn # ?
    def alertMsg(self, message):
        return self.bindings.htAlert(message)

    # @cursesOn # ?
    def confirm(self, message):
        return self.bindings.htConfirm(message)


    def lineGet(self, hidden = False, max_cols = 0, recall = None):
        # readline input mode
        # recall = {'url', 'command', 'mail'}
        return self.bindings.LYgetBString(hidden, max_cols, recall)


    @cursesOn
    def loadCursesDocument(self, *args):
        # import pdb; pdb.set_trace()
        return self.loadDocument(*args)

    def loadDocument(self, *args):
        # print 'loading document', args
        return self.bindings.loadDocumentAddress(*args)

    def loadHTMLString(self, string, url):
        return self.bindings.loadHTMLString(string, url)


    @property
    def main(self):
        return self.bindings.getHTMainTextObject()


class pyloCore(cursesCore, provisionalCore, v1apiCore):
    def __init__(self, bindings):
        self.bindings = bindings

        cursesCore.__init__(self)
        provisionalCore.__init__(self)

        self.init()


    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.bindings)
    def __str__(self):
        return ', '.join(dir(self.bindings))


    @noCurses
    def init(self):
        startup = getenv('PYLO_STARTUP_SCRIPT')
        if startup and exists(startup):
            # self.enqueueTask(
            self.fileExecute(startup)

        command = getenv('PYLO_STARTUP_COMMAND')
        if command:
            # self.enqueueTask(
            # import pdb; pdb.set_trace()
            self.executeCode(self.execute, command, command = command)


    def lynx_handleCommand(self, cmd): # *args, **kwd):
        # XXX use lynx keymapping
        if cmd == 0: # so it happens that 'y' is 0?
            # see also: self.interpreter
            from code import InteractiveConsole as IC
            import readline

            ns = dict(core = self, command = cmd)

            with withoutCurses():
                IC(locals = ns) \
                    .interact(banner = '')

            return ns.get('__lynx_command', None) # intending: do nothing

        return cmd


    @property
    def main_ctypesModule(self):
        from ctypes import CDLL
        return CDLL('') # .HText_new
