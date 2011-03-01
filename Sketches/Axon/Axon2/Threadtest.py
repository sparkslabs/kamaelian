#!/usr/bin/python

import time
from threading import Thread
import random

import Queue

class ProducerThread(Thread):
    def __init__(self, outbox1, outbox2):
        print "ProducerThread", id(self), "Initialising"
        self.outboxes = [outbox1, outbox2]
        super(ProducerThread, self).__init__()

    def run(self):
        for i in self.main():
            pass

    def main(self):
        quitTime = time.time() + 2
        while time.time() < quitTime:
            time.sleep(0.3)
            self.outboxes[0].put_nowait("ping")
            yield 1
        self.outboxes[0].put_nowait("quit")
        print "ProducerThread", id(self), "Finishing"

class ConsumerThread(Thread):
    def __init__(self, inbox1, inbox2):
        print "ConsumerThread", id(self), "Initialising"
        self.inbox1 = inbox1
        self.control = inbox2
        super(ConsumerThread, self).__init__()

    def run(self):
        for i in self.main():
            pass

    def controlReady(self, inbox="inbox"):
        self.control.get_nowait()

    def main(self):
        while 1:
            X = self.inbox1.get()
            print "ConsumerThread", id(self), X
            if "quit" in X:
                break
            yield 1
        print "ConsumerThread", id(self), "Finishing"


pipe1 = Queue.Queue()
pipe2 = Queue.Queue()
ProducerThread(pipe1, pipe2).start()
ConsumerThread(pipe1, pipe2).start()

















