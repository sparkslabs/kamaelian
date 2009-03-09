#!/usr/bin/python

if 0:
    import psyco
    psyco.full()

if 0:
            def counter():
                for i in range(10):
                    print "counter", i

            class counter2(object):
                def counter(self):
                    for i in range(10):
                        print "counter2", i

            s.schedule(counter)
            s.schedule(counter2().counter)

            for i in range(10):
                counter3(s, i).activate()

            class selfscheduler(object):
                def __init__(self, *argv, **argd):
                    self.s = scheduler.scheduler()
                    self.__t = id(self)

                def activate(self):
                    self.next = self.main().next
                    self.__s.schedule(self.tick)
                    return self

                def reschedule(self, R):
                    self.__s.schedule(self.tick)

                def tick(self):
                    try:
                        R = self.next()
                        if R:
                            self.reschedule(R)
                    except StopIteration:
                        pass

                def main(self):
                    yield 1

                def run(self):
                    self.__s.run()

            class counter3(selfscheduler):
                def main(self):
                    for i in range(10):
                        print "counter3", "Tag", id(self), "loop", i
                        yield 1

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

class scheduled(object):
    def __init__(self, *argv, **argd):
        self.s = scheduler.scheduler()

debug = True
def debugPrint(x):
    if debug:
        print x

class Bunch(object):
    def __init__(self, **argd):
        self.__dict__.update(argd)

import random
class hackysacker(scheduled):
    counter = 0
    def __init__(self, name, circle):
        self.name = name
        self.circle = circle
        circle.append(self)
        super(hackysacker,self).__init__()

    def kick(self, sender=Bunch(name="start")):
        if hackysacker.counter>turns:
            return
        hackysacker.counter +=1
        # debugPrint("%d: %s got hackeysack from %s" % (hackysacker.counter, self.name, sender.name))
        kickto = random.choice(self.circle)
        self.s.schedule(kickto.kick, self)

def runit(hs=10,ts=10,dbg=1):
    global hackysackers,turns,debug
    hackysackers = hs
    turns = ts
    debug = dbg#

    hackysacker.counter= 0
    circle = []
    one = hackysacker('1',circle)

    s = scheduler.scheduler()
    for i in xrange(hackysackers):
        H = hackysacker(str(i), circle)

    s.schedule(H.kick)

    s.run()

if __name__ == "__main__":
    import profile
    profile.run("runit(10000, 1000, dbg=0)")
