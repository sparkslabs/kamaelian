#!/usr/bin/python
"""
This file runs at about 1/2 speed of Axon.py, and marginally faster than the package.
Why?

python -OO /usr/lib/python2.5/timeit.py -s "import Axon2Pre" "Axon2Pre.runit(1000,10000,0)"
"""

import random

C = 0
debug = True
def debugPrint(x):
    if debug:
        print x
    return True

class scheduler(object):
    s = None 
    # This is not thread safe. Should make threadsafe through the use of an STM store.
    # Import existing Kamaelia STM code "as is" I think

    @classmethod
    def scheduler(cls):
        # Should check out class state
        # Then work on it
        if not cls.s:
            cls.s = cls()
        # Then try to commit
        # And if fails retry or succeed gracefully
        # Provides basics for services
        # Indeed all services really act that way.
        # Should have a mechanism for *releasing* as well in that case.
        # Interesting thought.
        return cls.s

    def __init__(self, *args):
        self.runq = []
        self.pendq = []

    def schedule(self, task, *args):
        self.pendq.append((task, args))

    def tick(self):
        self.runq = self.pendq
        self.pendq = []
        for task,args in self.runq:
            task(*args)

    def run(self):
        while len(self.runq) > 0 or len(self.pendq) > 0 :
            self.tick()

class scheduled(object):
    def __init__(self, *argv, **argd):
        self.s = scheduler.scheduler()

class component(scheduled):
    def __init__(self,  *argv, **argd):
        self.s = scheduler.scheduler()
        self.inboxes = {"inbox" : [] }
        self.outboxes = { }
        super(component,self).__init__()

    def activate(self, noschedule=False):
        self.next = self.main().next
        return self

    def send(self, message,outbox): # 461ms vs 186   
        recipient,inbox = self.outboxes[outbox]
        recipient.deliv(message,inbox)

    def deliv(self, message,inbox): # 461ms vs 186   
        self.inboxes[inbox].append(message)
        self.s.schedule(self.tick)

    def post(self, message, (recipient, inbox)):
        self.link((self, "__temporary__"), (recipient, inbox))
        self.send(message, "__temporary__")

    def reschedule(self, R):
        self.s.schedule(self.tick)

    def run(self):
        self.s.run()

    def tick(self):
        try:
            R = self.next()
            if R:
                self.s.schedule(R)
        except StopIteration:
            pass

    def link(self, (sender, outbox), reciever):
        sender.outboxes[outbox] = reciever

class hackysacker(component):
    counter = 0
    def __init__(self, name, circle, *argv, **argd):
        self.name = name
        self.circle = circle
        circle.append(self)
        super(hackysacker,self).__init__()

    def main(self):
        while 1:
            if hackysacker.counter>turns:
                return

            sender = self.inboxes["inbox"].pop(0)
            hackysacker.counter +=1
            kickto = random.choice(self.circle)

            # Fastest (by far) - if we had "handle" built into components this would be valid/nice in places
            # even if it's out of character for the rest of the system
            kickto.deliv(self,"inbox")

            # Next Fastest
#            self.link((self, "outbox"), (kickto, "inbox"))
#            self.send(self, "outbox")

            # Cleaner, but slowest
#            self.post(self, (kickto, "inbox"))
            yield

class Bunch(object):
    def __init__(self, **argd):
        self.__dict__.update(argd)

def runit(hs=10,ts=10,dbg=1):
    global hackysackers,turns,debug
    hackysackers = hs
    turns = ts
    debug = dbg

    hackysacker.counter= 0
    circle = []
    s = scheduler.scheduler()
    one = hackysacker('0',circle)
    one.activate()
    one.deliv(Bunch(name="default"), "inbox")

    for i in xrange(1,hackysackers):
        H = hackysacker(str(i), circle).activate()

    H.run()

if __name__ == "__main__":
    import profile
#    runit()
#    profile.run("runit(30000, 10000, dbg=0)")
    profile.run("runit(10000, 1000, dbg=0)")
