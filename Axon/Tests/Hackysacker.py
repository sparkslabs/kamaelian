#!/usr/bin/python
"""
python -OO /usr/lib/python2.5/timeit.py -s "import Hackysacker" "Hackysacker.runit(1000,10000,0)"
10 loops, best of 3: 240 msec per loop

python -OO /usr/lib/python2.5/timeit.py -s "import Hackysacker" "Hackysacker.runit(10000,1000,0)"
10 loops, best of 3: 168 msec per loop

python -OO /usr/lib/python2.5/timeit.py -s "import Hackysacker" "Hackysacker.runit(10000,10000,0)"
10 loops, best of 3: 373 msec per loop

python -OO /usr/lib/python2.5/timeit.py -s "import Hackysacker" "Hackysacker.runit(100000,100000,0)"
10 loops, best of 3: 4.63 sec per loop
"""
import random

from Axon2.Component import component

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

#            sender = self.inboxes["inbox"].pop(0)
            sender = self.recv("inbox")
            hackysacker.counter +=1
            kickto = random.choice(self.circle)
            self.post(self, (kickto, "inbox"))
            # Fastest (by far) - if we had "handle" built into components this would be valid/nice in places
            # even if it's out of character for the rest of the system
            # 10 loops, best of 3: 182 msec per loop
#            kickto.deliv(self,"inbox")

            # Next Fastest - 10 loops, best of 3: 235 msec per loop
#            self.link((self, "outbox"), (kickto, "inbox"))
#            self.send(self, "outbox")

            # Cleaner (and safe - it's a wrapper around link/send) but slowest - 10 loops, best of 3: 240 msec per loop
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
    one = hackysacker('0',circle)
    one.activate()
    one.deliv(Bunch(name="default"), "inbox")

    for i in xrange(1,hackysackers):
        H = hackysacker(str(i), circle).activate()

    H.run()

if __name__ == "__main__":
    import profile
#    runit()
###    profile.run("runit(10000, 1000, dbg=0)")
    profile.run("runit(10000, 1000, dbg=0)")
#    profile.run("runit(30000, 10000, dbg=0)")
