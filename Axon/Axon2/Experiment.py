#!/usr/bin/python

# class Producer(Component):
#     def main(self):
#         for i in range(10):
#              self.send(i, "outbox")
#              yield 1
# 
# class Consumer(Component):
#     def main(self):
#         while 1:
#              if self.dataReady("inbox"):
#                   data = self.recv("inbox")
#                   print "Got Data", data, id(self)
#              yield 1

import time
from multiprocessing import Process, Queue
from select import select
from Queue import Queue as ThreadQueue
from Queue import Empty as ThreadQueueEmpty

class MasterControl(Process):
    def __init__(self, inQueue, outQueue):
        super(MasterControl, self).__init__()
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.activateRequests = []

    def run(self):
        for i in self.main():
            pass

    def activate(self, some_generator):
        self.activateRequests.put(some_generator)
        print self, "ADDED", some_generator, "TO activation requests"

    def main(self):
        self.activateRequests = ThreadQueue()
        runqueue = []
        while 1: 
             (inready, outready, other) = select([self.inQueue._reader], [self.outQueue._writer], [], 0)
             if outready:
                 print "MCP can send to MAIN"

             if inready:
                 print "MCP can recieve from MAIN"
                 msg = self.inQueue.get()
                 print "MCP recieved", msg, "from MAIN"
                 G = msg.main()
                 msg.scheduler = self
                 runqueue.append(G)
             while True:
                  try:
                      msg = self.activateRequests.get_nowait()
                      G = msg.main()
                      msg.scheduler = self
                      runqueue.append(G)
                  except ThreadQueueEmpty:
                      break

             newqueue = []
             for T in runqueue:
                 try:
                     T.next()
                     newqueue.append(T)
                 except StopIteration:
                     # Component exitted, simply don't append
                     pass

             runqueue = newqueue
             time.sleep(0.5)
             yield 1


inQueue = Queue()
outQueue = Queue()

MCP = MasterControl(inQueue, outQueue)

MCP.start()

from Experiment_Components import Ticker

tosend = [ Ticker() ]
i = 0

while 1:
    time.sleep(1)
    
    (inready, outready, other) = select([outQueue._reader], [inQueue._writer], [], 0)
    if outready:
        print "MAIN can send to MCP"
        if len(tosend)>0:
            msg = tosend.pop(0)
            print "MAIN sending", msg, "to MCP"
            inQueue.put( msg )

    if inready:
        print "MAIN can recieve from MCP"

