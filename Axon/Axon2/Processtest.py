#!/usr/bin/python

import time
from multiprocessing import Process, Queue
import random

class ProducerProcess(Process):
    def __init__(self, outbox1, outbox2):
        print "ProducerProcess", id(self), "Initialising"
        self.outboxes = [outbox1, outbox2]
        super(ProducerProcess, self).__init__()

    def run(self):
        for i in self.main():
            pass

    def main(self):
        time.sleep(5)
        quitTime = time.time() + 2
        while time.time() < quitTime:
            time.sleep(0.3)
            self.outboxes[0].put_nowait("ping")
            yield 1
        self.outboxes[0].put_nowait("quit")
        print "ProducerProcess", id(self), "Finishing"

class ConsumerProcess(Process):
    def __init__(self, inbox1, inbox2):
        print "ConsumerProcess", id(self), "Initialising"
        self.inbox1 = inbox1
        self.control = inbox2
        super(ConsumerProcess, self).__init__()

    def run(self):
        for i in self.main():
            pass

    def controlReady(self, inbox="inbox"):
        self.control.get_nowait()

    def main(self):
        time.sleep(5)
        while 1:
            X = self.inbox1.get()
            print "ConsumerProcess", id(self), X
            if "quit" in X:
                break
            yield 1
        print "ConsumerProcess", id(self), "Finishing"


pipe1 = Queue()
pipe2 = Queue()
ProducerProcess(pipe1, pipe2).start()
ConsumerProcess(pipe1, pipe2).start()
