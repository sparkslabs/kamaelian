#!/usr/bin/python


class Component(object):
    Boxes = ["inbox", "outbox"]
    def __init__(self, **argd):
         super(Component,self).__init__(**argd) 
         self.__dict__.update(argd)
         self.boxes = {}
         for boxname in self.Boxes:
             self.boxes[boxname] = list()

    def send(self, outbox, data):  self.boxes[outbox].append(data)
    def recv(self, inbox):         self.boxes[inbox].pop(0)
    def dataReady(self, inbox):    return len(self.boxes[inbox])
    def run_one(self):
        for _ in self.main():
            pass
    def activate(self, C):
        print "ACTIVATE", C, "using", self.scheduler, "?"
        self.scheduler.activate(C)

class Tocker(Component):
    def main(self):
        while 1:
            print "tock"
            yield 1

class Ticker(Component):
    def main(self):
        T = Tocker()
        self.activate(T) # This starts in the same process as *this* ticker
        while 1:
            print "tick"
            yield 1

