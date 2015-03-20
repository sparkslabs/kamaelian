#!/usr/bin/python

import random

from Axon2.STM import Store, ConcurrentUpdate, BusyRetry

class scheduler(object):
    # __store = Store(immutablevalues=True) # Promise to only store new schedulers if we change this...
    __store = Store(immutablevalues=False) # Promise to only store new schedulers if we change this...
    s = None
    
    singleton_scheduler = None

    @classmethod
    def scheduler(cls):
        if cls.singleton_scheduler is None:
            cls.singleton_scheduler = cls()
        return cls.singleton_scheduler
    
     
        # Should check out class state
        # Then work on it
        sched = cls.__store.usevar("sched")
        cls.__store.dump()
        if sched.value is None:
            S = None
        else:
            S = sched.value
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
#        print "S",id(S), S
        return S

    def __init__(self, *args):
        self.runq = []
        self.pendq = []
        self.pendq_d = {}
#        print "NEW SCHEDULER", self
        
    def format_method(self, meth, args):
        return  "%s_%d.%s%s" % \
             (meth.im_class.__name__, id(meth.im_self)%100, meth.__name__, str(args))

    def __repr__(self):
        runq  = [ self.format_method(meth,args) for (meth,args) in self.runq ]
        pendq = [ self.format_method(meth,args) for (meth,args) in self.pendq ]
        pendq_d = dict([ (key, (self.format_method(self.pendq_d[key][0], self.pendq_d[key][1])) ) for key in self.pendq_d])
        return "scheduler(runq=%s,pendq=%s,pendq_d=%s)" % (runq, pendq, pendq_d)

    def schedule(self, task, *args):
#        print "    scheduler.schedule"
#        print "      PRE"
#        print "           scheduler | " +str(self)
#        print "           task      | " +str(task)
#        print "           args      | " +str(args)
#        print "           id(task)  | ", id(task)
        if not self.pendq_d.get(id(task), False):
            self.pendq_d[id(task)] = (task, args)
            self.pendq.append((task, args))
#        print "      POST"
#        print "           scheduler | " +str(self)

    def tick(self):
#        print "\n    scheduler.tick"
#        print "           pre ", self
#        print "           ditching OLD runq, replacing with pendq"
        self.runq = self.pendq
        self.pendq = []
        self.pendq_d = {}
        for task,args in self.runq:
            task(*args)
#        print "\n    scheduler.tick"
#        print "           post ", self

    def _tick(self):
#        print "DO NOT EVEN GET HERE 1"
        self.runq = self.pendq_d.itervalues()
        self.pendq = []
        self.pendq_d = {}
        for task,args in self.runq:
            task(*args)

    def run(self):
#        print "\n    SCHEDULER STARTED"
#        print "    self.runq", self.runq
#        print "    self.pendq", self.pendq
        while len(self.runq) > 0 or len(self.pendq) > 0 :
            self.tick()
#        else:
#            print "\n    SCHEDULER FINISHED"

class scheduled(object):
    def __init__(self, *argv, **argd):
        self.s = scheduler.scheduler()
#        print "SCHEDULED", self, self.s

