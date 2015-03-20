#!/usr/bin/python

from contextlib import contextmanager
from neocast.STM import Store, MAXFAIL

S = Store()
print "SNAPSHOT", S.snapshot()

try:
    repo = S.checkout()
    while repo.notcheckedin:
        with repo.changeset("foo", "bar", "baz") as c:

            d = S.using("foo", "bar", "baz")
            d.foo = 3
            d.bar = 4
            d.baz = 5
            d.commit()

            print c
            c.foo = 5
            c.bar = 6
            c.baz = 7
    
except MAXFAIL, mf:
    print "TRANSACTION COMPLETELY FAILED"

print "FIRST TEST SHOULD FAIL"
print "POST SNAPSHOT", S.snapshot()

# -------------------------------------------------------------------------------------

S = Store()
print "SNAPSHOT", S.snapshot()

try:
    repo = S.checkout()
    while repo.notcheckedin:
        with repo.changeset("foo", "bar", "baz") as c:
            print c
            c.foo = 5
            c.bar = 6
            c.baz = 7
    
    print "TRANSACTION SUCCEEDED"

except MAXFAIL, mf:
    print "TRANSACTION COMPLETELY FAILED"

print "SECOND TEST SHOULD SUCCEED"
print "POST SNAPSHOT", S.snapshot()
