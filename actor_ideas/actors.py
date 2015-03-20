
import os
import time

from neocast.actor import expose, command, function, ActiveActor, Actor

class Suicidal(ActiveActor):
    @expose
    def main(self):
        time.sleep(1)
        pid = os.getpid()
        os.system("kill -9 %d" % pid)
        yield

class Pinger(Actor):
    def __init__(self):
        super(Pinger, self).__init__()
        self.count = 0

    @command
    def doPing(self, sender):
        self._private.sayping()
        if sender:
            sender.doPong(self)

    @function
    def getcount(self):
        return self.count

    def sayping(self):
#        print "Ping!"
        self.count = self.count + 1

class Ponger(Actor):
    @command
    def doPong(self, sender):
        self._private.saypong()
        if sender:
            sender.doPing(self)
            count = sender.getcount(self)
#            print "COUNT", count

    def saypong(self):
        pass
#        print "Pong!"

if __name__ == "__main__":
    import time
    pinger = Pinger()
    ponger = Ponger()

    s = Suicidal()
    s.start()

    pinger.start()
    ponger.start()
    pinger.doPing(ponger)
