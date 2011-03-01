#!/usr/bin/python

from Axon2.Scheduler import scheduled

from collections import deque

class component(scheduled):
    Inboxes = {
        "inbox" : "default inbox",
        "control" : "default control inbox",
    }
    Outboxes = {
        "outbox" : "default outbox",
        "signal" : "default control signal outbox",
    }
    def __init__(self,  *argv, **argd):
        self.inboxes = { }
#        print "\nCOMPONENT NEW", repr(self)
        for boxname in self.Inboxes:
        #    self.inboxes[boxname] = []
            self.inboxes[boxname] = deque()
        self.outboxes = { }
        super(component,self).__init__()
    
    def __repr__(self):
        return self.__class__.__name__+"_"+str(id(self)%100)

    def activate(self, schedule=True):
#        print "    ", repr(self) + ".activate(schedule=",schedule,")"
        self.next = self.main().next
        if schedule:
            self.reschedule(None)
        return self

    def send(self, message,outbox): # 461ms vs 186   
        try:
            recipient,inbox = self.outboxes[outbox]
        except KeyError:
            return
        recipient.deliv(message,inbox)

    def deliv(self, message,inbox): # 461ms vs 186
#        print "\n    MESSAGE DELIVERY", "to", self, "message", message, "box", inbox
        self.inboxes[inbox].append(message)
        self.s.schedule(self.tick)

    def post(self, message, (recipient, inbox)):
        self.link((self, "__temporary__"), (recipient, inbox))
        self.send(message, "__temporary__")
        self.unlink( (self, "__temporary__") )

    def reschedule(self, R):
        self.s.schedule(self.tick)

    def run(self):
        self.s.run()

    def tick(self):
#        print "\nCOMPONENT TICK", repr(self)
        try:
            R = self.next()
            if hasattr(R, "handle"):
               R.handle(self)
            elif R:
               self.reschedule(R)
        except StopIteration:
            pass

    def link(self, (sender, outbox), reciever):
        sender.outboxes[outbox] = reciever

    def unlink(self, (sender, outbox)):
        del sender.outboxes[outbox]

    def recv(self, inbox="inbox"):
        return self.inboxes[inbox].popleft()
       # return self.inboxes[inbox].pop(0)

    def Inbox(self,inbox="inbox"):
        for _ in xrange(len(self.inboxes[inbox])):
            yield self.recv(inbox)

    def dataReady(self, inbox="inbox"):
        return len(self.inboxes[inbox])>0
