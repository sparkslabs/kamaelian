#!/usr/bin/python

from Axon2.Scheduler import scheduled

class component(scheduled):
    def __init__(self,  *argv, **argd):
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

