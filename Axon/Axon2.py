#!/usr/bin/python

import random

debug = True
def debugPrint(x):
    if debug:
        print x

class scheduler(object):
    s = None

    @classmethod
    def scheduler(cls):
        if not cls.s:
            cls.s = cls()
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

class Bunch(object):
    def __init__(self, **argd):
        self.__dict__.update(argd)

class scheduled(object):
    def __init__(self, *argv, **argd):
        self.s = scheduler.scheduler()

class getmessage(object): pass

#class selfscheduled(scheduled):
class hackysacker(scheduled):
    counter = 0
    def __init__(self, name, circle, *argv, **argd):
        debugPrint("__init__ %s" % name)
        self.s = scheduler.scheduler()
        self.__t = id(self)
        self.name = name
        self.circle = circle
        self.inboxes = {"inbox" : [] }
#        self.inbox = []
        circle.append(self)
        super(hackysacker,self).__init__()

    def activate(self, noschedule=False):
        debugPrint("activate %s" % self.name)
        self.next = self.main().next
        if not noschedule:
            self.s.schedule(self.tick)
        return self

    def reschedule(self, R):
        debugPrint("reschedule %s" % self.name)
        self.s.schedule(self.tick)

    def tick(self):
        debugPrint("tick %s" % self.name)
        try:
            R = self.next()
            debugPrint( "R %s" % repr(R) )
            if R:
                self.s.schedule(R)
        except StopIteration:
            pass

    def run(self):
        debugPrint("run %s" % self.name)
        self.s.run()

    def main(self):
        while 1:
            if hackysacker.counter>turns:
                debugPrint( "And the game is over...." )
                return

            debugPrint("%s: Getting message from %s" % (self.name, repr([ x.name for x in self.inboxes["inbox"]]) ) )
            sender = self.inboxes["inbox"].pop(0)

            hackysacker.counter +=1
            debugPrint("%d: %s got hackeysack from %s" % (hackysacker.counter, self.name, sender.name))

            kickto = random.choice(self.circle)
            debugPrint( "Kicking to %s %s" % ( repr(kickto.tick), repr(kickto.next)) )
            self.post2(self, (kickto, "inbox"))
#            self.post(self, (kickto, "inbox"))
#            kickto.deliv(self)
            yield

    def deliv(self, message,inbox): # 461ms vs 186   
        self.inboxes[inbox].append(message)
        self.s.schedule(self.tick)

    def post(self, message, (recipient, inbox)): #489ms vs  186
        recipient.inboxes[inbox].append(message)
        self.s.schedule(recipient.tick)

    def post2(self, message, (recipient, inbox)): #466ms vs  186
        recipient.deliv(message,inbox)

def runit(hs=10,ts=10,dbg=1):
    global hackysackers,turns,debug
    hackysackers = hs
    turns = ts
    debug = dbg

    hackysacker.counter= 0
    circle = []
    one = hackysacker('0',circle)
    one.activate()
    one.inboxes["inbox"].append(Bunch(name="default"))


    s = scheduler.scheduler()
    for i in xrange(1,hackysackers):
        H = hackysacker(str(i), circle).activate(noschedule=True)

    H.run()

if __name__ == "__main__":
    import profile
#    runit()
    profile.run("runit(10000, 1000, dbg=0)")
