#!/usr/bin/python

from contextlib import contextmanager
import random

class FAIL(Exception):
    pass

class MAXFAIL(Exception):
    pass

class Bunch(object):
    def __init__(self, keys):
        i = 0
        for key in keys:
            self.__dict__[key] = i
            i +=1

class Transaction(object):
    def __init__(self, max_tries=0):
        self.todo = True
        self.num_tries = 0
        self.max_tries = max_tries

    @contextmanager
    def __call__(self, *args):
        print "WOMBAT", args
        B = Bunch(args)
        self.num_tries += 1
        try:
            yield B
            print "TRANSACTION SUCCEEDED after", self.num_tries, "tries"
            self.todo = False
            self.todo 
        except FAIL, f:
            if self.max_tries:
                if self.max_tries == self.num_tries:
                    print "TRANSACTION FAILED", self.num_tries
                    raise MAXFAIL(f)
            print "TRANSACTION FAILED, need to retry", self.num_tries
        print "TABMOW", args

try:
    t = Transaction(max_tries=10)
    while t.todo:
        with t("foo", "bar", "baz") as c:
            print c.foo
            print c.bar
            print c.baz
            c.foo = 5
            c.bar = 6
            c.baz = 7
            if random.randint(0,10):
                raise FAIL()
    print "BUNCH", c
    print "FOO", c.foo
    print "BAR", c.bar
    print "BAZ", c.baz
    
except MAXFAIL, mf:
    print "TRANSACTION COMPLETELY FAILED"


