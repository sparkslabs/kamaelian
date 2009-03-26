#!/usr/bin/python

import random

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

