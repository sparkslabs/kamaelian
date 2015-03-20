
import sys

divider = " "
flush = True

def Print(*arg):
    Printnl(*arg)
    sys.stdout.write("\n")
    if flush:
        sys.stdout.flush()


def Printnl(*arg):
    tp = []
    tp = [str(x) for x in arg]
    sys.stdout.write(divider.join(tp))
