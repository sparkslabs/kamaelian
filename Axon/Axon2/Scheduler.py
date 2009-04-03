#!/usr/bin/python

import random

from Axon2.STM import Store, ConcurrentUpdate, BusyRetry

class scheduler(object):
    __store = Store(immutablevalues=True) # Promise to only store new schedulers if we change this...
    s = None 

    @classmethod
    def scheduler(cls):
        # Should check out class state
        # Then work on it
        sched = cls.__store.usevar("sched")
        S = None
        while S is None:
           if not sched.value:
              sched.set( cls() )
              try:
                 sched.commit()
                 S = sched.value
              except ConcurrentUpdate:
                 sched = cls__store.usevar("sched")
              except BusyRetry:
                 sched = cls__store.usevar("sched")
           else:
               S = sched.value
        return S

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

