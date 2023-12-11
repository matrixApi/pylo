from .utils import *
from .pyloCurses import *


class provisionalCore:
    def __init__(self):
        self.queue = Queue()
        self.event = self.Event(self)
        self.namespace = dict()
        self.pages = self.pageCollection(self)
        self.unsecure = self.UnsecureDomain(self)

        def loadLocal():
            return self.ObjectAccess.LocalFilesystem(self)

        self.domains = self.LoadDynamic(local = loadLocal) \
                           .load(unsecure = self.unsecure)


    class Event(object):
        def __init__(self, object):
            self.__object = object

        def __getattr__(self, name):
            try: return object.__getattribute__(self, name)
            except AttributeError:
                return self.Task(self.__object, name)

        class Task:
            def __init__(self, object, name):
                self.object = object
                self.name = name

            @property
            def function(self):
                return getattr(self.object, self.name)

            def __call__(self, *args, **kwd):
                return self.object.enqueueTask(self.function, *args, **kwd)


    @noCurses
    def loopCycle(self):
        try: task = self.queue.get_nowait()
        except Empty: pass
        else: self.dispatchTask(task)

        pass # self.input = None

    def dispatchTask(self, task):
        if isinstance(task, tuple):
            (task, args, kwd) = task
        else:
            args = ()
            kwd = dict()

        try: task(*args, **kwd)
        except:
            print_exc()
            input() # todo: remove this?

    def enqueueTask(self, task, *args, **kwd):
        self.queue.put((task, args, kwd))
        return self
    # __iadd__ = __add__ = enqueueTask

    from pdb import runcall as debugCall, set_trace as debugStart
    debugStart = staticmethod(debugStart)
    debugCall = staticmethod(debugCall)

    # def _debugCall(self, *args, **kwd):
    #     # For debugging the debugger...
    #     self.debugStart()
    #     return self.debugCall(*args, **kwd)

    def noCursesCall(self, function, *args, **kwd):
        with withoutCurses():
            return function(*args, **kwd)

    def systemShell(self, *args, **kwd):
        # my.shbin.execute
        e = io.path(system.environment.SHELL).execute
        return self.noCursesCall(e, *args, **kwd)
    shell = property(systemShell)


    def generateInput(self):
        # Note: do not turn off curses.
        # todo: This should be named something closer to 'get input character'?

        # Todo: by utilizing the bindings input api, we can build a python-driven
        # interface that utilizes, for instance:
        # print 'generateInput'

        try: handler = self.keyHandler
        except AttributeError: pass
        else:
            if callable(handler):
                return handler(self)

        try: input = self.input
        except AttributeError: pass
        else:
            del self.input
            return input

        return # self.bindings.generateInput()

    def handleInput(self, input):
        pass

    @cursesOff
    def evaluateCodeLink(self, address):
        # import pdb; pdb.set_trace()

        # url = Url(address)
        # proto = url.host.proto
        # host = url.host.name.split(':')[0]
        # path = url.path[0].split('/')
        # query = url.query

        (r, query) = parseUrl(address)
        proto = r.scheme
        host = r.netloc
        path = r.path[1:].split('/') # remove preceding '/'

        if proto == 'python':
            return self.domainServe(host, *path, **query)


    def domainServe(self, domain, *path, **query):
        # import pdb
        # pdb.set_trace()

        # print 'serve', string.call(domain, *path, **query)

        try: domain = self.domains[domain]
        except KeyError: pass
        else:
            result = domain(*path, **query)
            if result is None:
                return self.core.bindings.HT_NOT_LOADED

            return result


    class PathMap(dict):
        def byPath(self, *path, **query):
            i = len(path)

            while i:
                p = path[:i]

                try: handler = self[p]
                except KeyError:
                    try: handler = self['/'.join(p)]
                    except KeyError:
                        i -= 1
                        continue

                return handler(*path[i:], **query)

            raise NameError(path)


        def __getitem__(self, item):
            if isinstance(item, (tuple, list)):
                this = self
                for i in item:
                    try: this = getattr(this, i)
                    except AttributeError:
                        raise KeyError(item)

                return this

            return dict.__getitem__(self, item)

        def default(self, *path, **query):
            pass # return ??

        def __call__(self, *path, **query):
            try: return self.byPath(*path, **query)
            except NameError:
                return self.default(*path, **query)


    class LoadDynamic(object):
        'Instantiate domain handler at runtime, based on constructor configuration.'

        def __init__(self, **objects):
            self.objects = objects
            self.data = dict()

        def __getitem__(self, item):
            try: return self.data[item]
            except KeyError:
                accessClass = self.objects[item]
                o = accessClass()
                self.data[item] = o
                return o

        def load(self, **objects):
            self.data.update(objects)
            return self


    # class LoadDynamic(dict):
    #     'Instantiate domain handler at runtime, based on constructor configuration.'

    #     def __new__(cls, **objects):
    #         from types import ClassType

    #         def getItemDynamic(self, name):
    #             try: return dict.__getitem__(self, name)
    #             except KeyError:
    #                 accessClass = objects[name]
    #                 print accessClass
    #                 o = accessClass()
    #                 self[name] = o
    #                 return o

    #         i = ClassType(cls.__name__ + '@%d' % id(objects),
    #                       (cls,), dict(__getitem__ = getItemDynamic))

    #         i = dict.__new__(i) # XXXX calls dict.__init__ with the __new__ arguments, which DEFEATS THE F****** POINT

    #         # import pdb; pdb.set_trace()
    #         return i

    #     def load(self, **objects):
    #         self.update(objects)
    #         return self


    # XXX these are inherently insecure, because any python: protocol link from any page can execute them.
    class UnsecureDomain(PathMap):
        # python://unsecure/execute/print/core,/value?value=1
        def __init__(self, core):
            self.core = core

        def execute(self, *path, **query):
            source = ' '.join(path)
            query['path'] = path
            query['source'] = source
            self.core.executeCode(self.core.execute, source, **query)
            return self.core.bindings.HT_LOADED

    class ObjectAccess(PathMap):
        # python://local/workspace/$program$/notes/wmcOf/value/code/handler?code=print+state&state=on
        @classmethod
        def LocalFilesystem(self, core):
            import common
            return self(core, my)

        def __init__(self, core, object):
            self.core = core
            self.object = object

        def __getitem__(self, item):
            return self.Access(self, *item)

        class Access(list):
            def __init__(self, access, *path):
                self.access = access
                list.__init__(self, path)

            def __call__(self, **query):
                # import pdb; pdb.set_trace()
                if self.access.core.confirm('Alert: Proceed with potentially unsafe program?! '):
                    handler = access(self.access.object, *self)
                    query['this'] = self
                    return handler(**query)


    #@noCurses # nothing displays anyway...
    def handleCommand(self, command):
        if command:
            try: code = compile(command, '<$program$ python command>', 'single')
            except SyntaxError as e:
                print_exc()
            else:
                self.executeCode(self.execute, code, command = command)

        return True

    def executeCode(self, execute, code, **values):
        ns = self.namespace
        ns['core'] = self
        ns['code'] = code
        ns.update(values)

        import __main__ as main
        main = main.__dict__

        try: execute(code, main, ns)
        except:
            print_exc()

    def fileCompile(self, path):
        with open(path) as o:
            source = o.read()

        return compile(source, path, 'exec')

    def fileExecute(self, path):
        return self.executeCode(self.execute,
                                self.fileCompile(path),
                                path = path)

        # try: execfile(path)
        # except:
        #     print_exc()

    def execute(self, code, g, o):
        # WTF ?!?!?!??!?!?!?!!??!?!?!
        # try: exec code in o, g
        # finally:
        #     print 'locals:', ', '.join(o.keys())
        #     print 'globals:', ', '.join(g.keys())

        exec(code, o, g)

    def downloadUrl(self, resource):
        raise NotImplementedError
        return nativeUrlDownload(resource)


    namespace = dict()

    @noCurses # what if it's already off??  might break state on caller restoration.
    def interpreter(self):
        from code import InteractiveConsole as IC
        import readline
        self.namespace['self'] = self
        IC(locals = self.namespace).interact(banner = '')

    class pageCollection(list):
        def __init__(self, core):
            self.core = core

        class document:
            def __init__(self, pages, doc):
                self.pages = pages
                self.doc = doc

            def activateMain(self):
                return self.doc.activateMain()
            __call__ = activateMain
            activate = property(activateMain)

        def openAddress(self, *args):
            doc = self.core.loadCursesDocument(*args)
            doc = self.document(self, doc)
            self.append(doc)
            return doc
        __call__ = openAddress

        def activate(self, index):
            return self.get(index).activateMain()

        def get(self, index):
            return list.__getitem__(self, index)

        def __getitem__(self, title):
            'Activate first document with title.'

            for doc in self:
                if doc.title == title:
                    return doc.activateMain()


    class DocumentInspector:
        @classmethod
        def Inspect(self, core, document):
            # Generate new interpreter.
            return self(core, document).main

        def __init__(self, core, document):
            # Initialize interface object with environment.
            core.document = self
            self.object = document


        # Application Modes.
        mainChoices = dict(u = 'goUp', m = 'selectMain')

        #@fronting
        def main(self, model):
            c = model.keyCode()

            try: k = chr(c)
            except ValueError:
                # print 'main <%d>' % c
                return c

            # Navigate model.document.object
            try:
                # Note: because this code path returns None, loop cycle repeats...
                model.keyHandler = getattr(self, self.mainChoices[k])(model)

            except KeyError:
                return c


        def upNow(self, model):
            # While in this mode, monitor the keystroke, and return it.
            c = model.keyCode()

            if 1:
                # This seems to work, although the 'g' isn't printed
                print('got up now %r\r' % c)

                try: print('up now: %r\r' % chr(c))
                except ValueError:
                    print('up now <%s>\r' % c)

                # Without this, it isn't visible...
                import time
                time.sleep(1)


            return c


        # Actions
        def goUp(self, model):
            # print 'going up...'
            return self.upNow

        def selectMain(self, model):
            model.bindings.getHTMainTextObject().activateMain()


    def inspect(self, document):
        self.keyHandler = self.DocumentInspector.Inspect(self, document)

    def documentLoaded(self, documentObjectNative):
        pass


    # Document building.
    tag = None

    def handleScriptStartComplex(self, script, attributes):
        try: type = attributes['type']
        except KeyError: pass
        else:
            if type == 'text/python':
                if self.tag is None:
                    self.tag = self.PythonScriptElement(None, script, **attributes)
                else:
                    self.tag = self.tag.open('script', script, **attributes)

            elif type == 'text/javascript':
                pass # todo: njs-based script processor.


    def handleScriptEnd(self):
        tag = self.tag

        if tag is not None:
            self.tag = tag.execute(self)

    class PythonScriptElement:
        '''
        <script type="text/python">
        from threading import Thread
        import telnetlib

        @apply
        class Telnet(Thread):
            def __init__(self):
                Thread.__init__(self)
                core.telnetSession = self
                self.responses = []
                self.start()

            def run():
                self.telnet = telnetlib.Telnet('localhost', 2112)

                while True:
                    incoming = self.telnet.read_eager()

                    action = "python://unsecure/execute/core.telnetSession.handle(incoming)?incoming="
                    action += quote(incoming)

                    core.enqueueTask(self.open, action)

            def open(self, action):
                if core.confirm('Handle incoming session data? '):
                    self.responses.append(core.pages(action))

            def handle(self, incoming):
                for line in incoming.split('\n'):
                    if line.startswith('*OOB:'):
                        self.telnet.send('%s\n' % line[5:]) # echo

        </script>
        '''

        def __init__(self, parent, script, **attributes):
            self.parent = parent
            self.script = script
            self.attributes = attributes

        def open(self, type, content, **attributes):
            # Nested elements.
            if type == 'text/python':
                return pyloCore.PythonScriptElement(self, content, **attributes)

            return self

        def execute(self, core):
            try: code = compile(self.script, '<$program$ python script>', 'exec')
            except SyntaxError as e:
                print_exc()
            else:
                if core.confirm('Execute page script? '):
                    core.executeCode(core.execute, code, tag = self,
                                     **self.attributes)

            return self.parent


    def synchronize(self, serverClass, *args, **kwd):
        # Start synchronization.
        control = self.event.synchronizationControl
        control = self.synchronization(control)

        return serverClass(self, control, *args, **kwd)

    def synchronizationControl(self, synchronization):
        # Run this in the event queue to operate the synchronization.
        # This exists so as to bind with the core instance's event dispatch.

        synchronization(self)


    class synchronization:
        # This object synchronously controls the operation of the $program$
        # browser application.  Its purpose is to create a network server
        # node out of it -- or at least an extension point.
        #
        # What this means is that the $program$ browser functionality only
        # runs when the synchronization server continues it.  It does
        # this by executing around parallelization of messaging signals.

        # Note that this is done by not directly referencing the core
        # except in a way that it might be used to interpret the signal.

        def __init__(self, control):
            self.control = control
            self.queue = Queue()

            self.synchronize()

        def synchronize(self):
            # Register this application object as a server.
            self.control(self)

        def resume(self):
            self.queue.put(True)
        def stop(self):
            self.queue.put(False)

        def interpretSignal(self, core):
            return bool(self.queue.get())

        def __call__(self, core):
            if self.interpretSignal(core): # Blocking.
                # Get ready for next operation.
                self.synchronize()


        class network:
            # XXX The initial synchronization state is not handled without a minimal user interaction.

            # The extension is initialized before the application (interactivity) loop, but the
            # event handler runs with every browser event.  A synchronization network will control
            # browser operation, but it should be mentioned that, as a curses program, there is
            # little concept of a $program$ program that is headless.
            #
            # This means that the network synchronization function must be started in a console,
            # until the core can be decoupled from its interface.  So it's management of an
            # additional window :-(

            PYLO_STARTUP_COMMAND = 'core.synchronize(core.synchronization.web, "127.0.0.1", 8040, start = True)'

            def __init__(self, core, synchronization, *args, **kwd):
                self.core = core

                self.resume = synchronization.resume
                self.stop = synchronization.stop

                self.init(*args, **kwd)

            def init(self, start = False):
                if start:
                    from common.runtime.functional.parallelized import nth
                    nth(self.run)

            def run(self):
                # I don't know, just operate resume/stop.
                try: pass
                finally:
                    self.stop()


            def message(self, *args, **kwd):
                return self.messager.call(self.core.enqueueTask,
                                          *args, **kwd)

            class messager:
                @classmethod
                def call(self, enqueue, function, *args, **kwd):
                    m = self(function)
                    enqueue(m, *args, **kwd)
                    return m.value

                def __init__(self, function):
                    self.function = function
                    self.queue = Queue()

                def __call__(self, *args, **kwd):
                    try: result = self.function(*args, **kwd)
                    except Exception as e: result = (False, e)
                    else: result = (True, e)

                    self.queue.put(result)

                @property
                def value(self):
                    (success, r) = self.queue.get()
                    if success:
                        return r

                    raise r


            # Server methods.
            def download(self, url):
                # Basically, initiate a document page download,
                # and then return the resulting object to the
                # network initiator.

                # XXX this will fail especially because, as a
                # single-threaded server request procedure,
                # the pages function will block on the condition
                # following the resumption of the synchronization
                # after this request...
                #
                # So the solution is to create a parallelized
                # waiting routine that allows the synchronization
                # server to operate.

                return self.message(self.core.pages, url)

        network.base = network


        class web(network):
            class serverClass:
                def _dispatch(self, method, params):
                    # The purpose of this server class method is to resume the browser
                    # application synchronization after each request.  Note: this may
                    # be a lame (non-robust) method for a complete synchronization
                    # solution.

                    try: return self.base._dispatch(self, method, params)
                    finally: self.network.resume()

            def init(self, address, port, **kwd):
                from xmlrpc.server import SimpleXMLRPCServer as XMLRPC

                class serverClass(self.serverClass, XMLRPC):
                    base = XMLRPC

                self.server = serverClass((address, port))
                self.server.network = self
                self.server.register_introspection_functions()
                self.register(self.server.register_function)
                self.base.init(self, **kwd)

            def run(self):
                self.server.serve_forever()

            def register(self, register):
                register(self.download, 'location.download')

        network.web = web


'''
Bridging the network:

    A parallelized apartment control-network could initiate $PROGRAM$ network transactions using
    the core api.  That network would be responsible for serving the data from the returned
    document structure.  Actually operating the document page would require additional code
    for multithreading the $program$/network apartments.

    --
    $program$ should be compiled as a library, not just an executable.  Then, it could be linked
    as a python module so that its code an be hosted in networked compartments.  Because
    this complicates the $program$, I choose instead to focus on these bindings and the
    instrumented modifications to the codebase that generate a python lifecycle.

    --
    core.event.loadDocument -- unsuitable because events run without curses

    core.event.loadCursesDocument -- suitable because this turns on curses for event dispatch
    core.event.pages -- calls loadCursesDocument and also manages the result.


    class control(rpcServer):
        """
        future.Work(control(address, port, core.event))

        unsecure = 'unsecure'

        page = control.client(address, port).page
        page.open(unsecure, 'https://unsecure.com')

        if active:
            page.raiseUp(unsecure)
        else:
            # What about client contextmanagers?
            print page.image(unsecure)['links'][0]['href']
            page.close(unsecure)

            """

        def init(self, core):
            self.core = core
            self.pages = dict()

        class page(rpcServer.methods):
            def open(self, request, name, url):
                if name in request.server.pages:
                    return False

                request.server.pages[name] = request.server.core.pages(url)
                return True

            def close(self, request, name):
                if name not in request.server.pages:
                    return False

                del request.server.pages[name]
                return True


            def image(self, request, name):
                if name in request.server.pages:
                    page = request.server.pages[name]
                    return dict(lines = page.lines,
                                links = page.links)

            def raiseUp(self, request, name):
                if name in request.server.pages:
                    request.server.pages[name].activateMain()
                    return True

                    '''


'''
cursesStart
cursesStop

bindingsModule
bindingsLoad

statusline(message)
htUserMsg(message)
htInfoMsg(message)
htAlert(message)
htConfirm(message)

HT_NOT_LOADED
HT_LOADED

LYgetch_for:
    FOR_PANEL
    FOR_CHOICE
    FOR_INPUT
    FOR_PROMPT
    FOR_SINGLEKEY

LYgetch
LYgetBString(hidden, max_cols, recall)

getHTMainTextObject().activateMain()

loadDocumentAddress(*args)
loadHTMLString(string, url)

'''


# class curses:
#     def __init__(self, function):
#         self.function = function

#     def on(self, *args, **kwd):
#         with self.turnedOn():
#             return self.function(*args, **kwd)

#     def off(self, *args, **kwd):
#         with self.turnedOff():
#             # print self.function
#             return self.function(*args, **kwd)

#     @contextmanager
#     def turnedOn(self):
#         cursesStart()

#         try: yield
#         finally:
#             cursesStop()

#     @contextmanager
#     def turnedOff(self):
#         cursesStop()

#         try: yield
#         finally:
#             cursesStart()

#     @classmethod
#     def With(self, function):
#         return self(function).on

#     @classmethod
#     def Without(self, function):
#         return self(function).off


# noCurses = curses.Without
