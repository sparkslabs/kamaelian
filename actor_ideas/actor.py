#!/usr/bin/python
"""
Issues:
    - private is icky - it's a work around the fact that method lookup isn't working with inheritance, unless we explicitly tag things
    - @functions have to handle the explicit reply work themselves, rather than hidden "inside" the decorator, which
      makes these (safe) function calls ugly on the implementer (not caller) side
    - ActiveActor is not named fantastically as yet, but does the required job at the moment
    - No pure generator based actors
    - Probably lots of overhead.
    - Inheritance between classes as "damaged"

Benefits:
    - So far, improved clarity, especially in the cross-actor calling convention.
      (Lots better for caller, slightly better for callee at present)

http://en.wikiquote.org/wiki/Kurt_Vonnegut

"""

from threading import Thread
import Queue
from neocast.util import Print

class Bunch(object):
    def __init__(self, __Dict=None, **argd):
        self.__dict__.update(__Dict)
        self.__dict__.update(argd)
        
    def __getattribute__(self, value):
        try:
            theobj = super(Bunch, self).__getattribute__("theobj")
        except AttributeError:
            storedvalue = super(Bunch, self).__getattribute__(value)
            return storedvalue
        
        storedvalue = super(Bunch, self).__getattribute__(value)
        #
        # Ideally we'd do this closure creation work once rather than many times, and
        # also preseve all the function metadata. For the moment though, we don't
        # since we're still scaffolding the system to see if it's doable, and how.
        def func(*argv, **argd):
            return storedvalue(theobj,*argv, **argd)
        #
        return func

# ------------------------------------------------------------------------------------
# 
# Meta class designed to enable a user of this to decorate the class into
# private & non-private elements. These are specifically designed to allow
# someone to make it hard to accidentally shoot your foot off
# 
# The context is that when dealing with concurrency you really don't want to
# accidentally call a thread non-safe piece of code from a outside that thread
# unless you really know what you're doing.
# 
# As a result this collects all the private (non-outside-threadsafe) functions
# into a sub object "_private", and collates all externally callable functions and
# commands a __commands__ and __functions__ dict.
# 
# These functions and commands will send parameters over threadsafe queues into
# the object for processing at a known time such that they also don't interleave.
# 
# Finally there are callables which are passed through as normal methods.
# These remain accessible. The purpose of these is to provide access to any
# public thread-safe API. (For example, an object can provide a "reply" method
# that provides a response queue for threadsafe passing of results. This would
# be called *outside* the thread and simply append to a theadsafe queue)
#
# Other things that can sit inside such functions might update a software
# transactional memory store.
# 
class MyType(type):
    def __new__(meta, name, bases, Dict):
        newdict = {} # We split off the public exposed interface interface into here
        private = {} # We split off the private non-exposed interface into here
        newdict["__commands__"] = {}
        newdict["__functions__"] = {}
        for key in Dict:
            if key[:2] == "__":
                newdict[key] = Dict[key]
            else:
                if isinstance(Dict[key], tuple):
                     methtype, meth = Dict[key]
                     if methtype == "callable":
                         newdict[key] = meth
                     elif methtype == "command":
                         newdict["__commands__"][key] = meth
                     elif methtype == "function":
                         newdict["__functions__"][key] = meth
                else:
                     private[key] = Dict[key]

        newdict["_private"] = Bunch(private)
        theobj = type.__new__(meta, name, bases, newdict)
        
        # Now that we have the object as well, we can stuff a self reference into _private, so that
        # the original methods can still be used as bound methods
        
        # theobj._private.theobj = theobj # This is WRONG - it's the class, not the object
        # For the moment, migrated to Actor
        return theobj


# Decorators designed for use with the metaclass above. Not designed for any other use
def expose(meth): return ("callable", meth)
def command(meth): return ("command", meth)
def function(meth): return ("function", meth)

private = expose # FIXME - HACK

# ------------------------------------------------------------------------------
# Base Actor Classes
# ------------------------------------------------------------------------------
class Actor(Thread):
    __metaclass__ = MyType
    def __init__(self):
        super(Actor,self).__init__()
        self.mailbox = Queue.Queue()
        self.response = Queue.Queue()
        self._private.theobj = self # Without doing this, the _private methods will not function correctly

    # User should not override this method, a new subclass type may do
    @private
    def _handleMailbox(self):
        message = self.mailbox.get()
        return message

    # User should not override this method, though a reimplementer may want to
    @expose
    def run(self):
        wait = False
        delay = 0
        thread = self.main()
        while True:
            message = self._handleMailbox()
            if isinstance(message, tuple):
                if message[0] in self.__commands__:
                    method, argv, argd = message
                    theFunc = self.__commands__[method]
                    theFunc(self, *argv, **argd)

                if message[0] in self.__functions__:
                    method, caller, argv, argd = message
                    theFunc = self.__functions__[method]
#                    result = theFunc(self, caller, *argv, **argd)
                    result = theFunc(self, *argv, **argd)  # FIXME?: There could be something very useful though about including the sender...
                    caller.reply(result)

            if thread:
                thread.next()
    
    # User should not override this method
    @expose
    def reply(self, value):
        self.response.put(value)

    # User should not override this method
    def __getattribute__(self, key):
        try:
            value = super(Actor, self).__getattribute__(key)
            return value
        except AttributeError:
            commands = super(Actor, self).__getattribute__("__commands__")
            if key in commands:
                def func(*argv, **argd): # Again, this should be at minimum cached, or preferably built at startup.
                    self.mailbox.put((key, argv, argd))
                return func

            functions = super(Actor, self).__getattribute__("__functions__")
            if key in functions:
                def func(caller, *argv, **argd): # Again, this should be at minimum cached, or preferably built at startup.
                    """Function created in __getattribute__"""
                    self.mailbox.put((key, caller, argv, argd))
                    result = caller.response.get()
                    return result
                return func

            raise # Just fail

    # We expect the user to override this method
    @expose
    def main(self):
        return False

class ActiveActor(Actor):
    @private
    def _handleMailbox(self):
        try:
            message = self.mailbox.get_nowait()
            return message
        except Queue.Empty:
            return None

