#!/usr/bin/python

import random

C = 0
debug = True
def debugPrint(x):
    if debug:
        print x
    return True

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

class hackysacker(scheduled):
    counter = 0
    def __init__(self, name, circle, *argv, **argd):
        self.s = scheduler.scheduler()
        self.__t = id(self)
        self.name = name
        self.circle = circle
        self.inboxes = {"inbox" : [] }
        self.outboxes = { }
        circle.append(self)
        super(hackysacker,self).__init__()

    def link(self, sender, outbox, reciever):
        sender.outboxes[outbox] = reciever

    def run(self):
        self.s.run()

    def main(self):
        while 1:
            if hackysacker.counter>turns:
                return

            sender = self.inboxes["inbox"].pop(0)
            hackysacker.counter +=1
            kickto = random.choice(self.circle)
            self.link(self, "outbox", (kickto, "inbox"))
            self.send(self, "outbox")
#            self.post2(self, (kickto, "inbox"))
            yield

    def deliv(self, message,inbox): # 461ms vs 186   
        self.inboxes[inbox].append(message)
        self.s.schedule(self.tick)

    def send(self, message,outbox): # 461ms vs 186   
        recipient,inbox = self.outboxes[outbox]
        recipient.deliv(message,inbox)

    def post(self, message, (recipient, inbox)): #489ms vs  186
        recipient.inboxes[inbox].append(message)
        self.s.schedule(recipient.tick)

    def post2(self, message, (recipient, inbox)): #466ms vs  186
        recipient.deliv(message,inbox)

    def activate(self, noschedule=False):
        self.next = self.main().next
        return self

    def reschedule(self, R):
        self.s.schedule(self.tick)

    def tick(self):
        try:
            R = self.next()
            if R:
                self.s.schedule(R)
        except StopIteration:
            pass

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
    profile.run("runit(10, 10, dbg=0)")
