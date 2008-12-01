from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
from buildbot import uthreads

##
# Useful decorators for process functions

def newBuild(buildName):
    """
    Decorate a build function to create a new IBuildHistory context when
    called.  Used like this::
      @newBuild("make-dist")
      def make_dist(context):
          # ...
    """
    def d(fn):
        def w(context, *args, **kwargs):
            unique = yield _uniquifyName(buildName, context.hist)
            context = context.newSubcontext(
                subhistory=(yield context.hist.newBuild(unique)))
            yield fn(context, *args, **kwargs)
        return w
    return d

def newStep(stepName):
    """
    Decorate a build function to create a new IStepHistory context when
    called.
    """
    def d(fn):
        def w(context, *args, **kwargs):
            unique = yield _uniquifyName(stepName, context.hist)
            context = context.newSubcontext(
                subhistory=(yield context.hist.newStep(unique)))
            yield fn(context, *args, **kwargs)
        return w
    return d

def _uniquifyName(name, hist):
    """Generate a unqiue name for a child of context by appending a dash and a
    number."""
    kidNames = yield hist.getChildEltKeys()
    if name not in kidNames:
        raise StopIteration(name)
    i = 1
    while 1:
        namenum = "%s-%d" % (name, i)
        if namenum not in kidNames:
            raise StopIteration(namenum)
        i += 1

class Context(object):
    implements(interfaces.IContext)

    def __init__(self, historyelt):
        self.hist = historyelt

    def newSubcontext(self, subhistory):
        return Context(historyelt=subhistory)
