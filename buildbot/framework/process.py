from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
from buildbot import uthreads

class ProcessThread(uthreads.uThread):
    """
    A uThread with extra attributes used to track the status of build processing.
    
    @ivar hist: the current L{IHistoryElement}
    @type hist: L{IHistoryElement} provider
    """
    __slots__ = ( 'hist' )

    def __init__(self, hist, *args, **kwargs):
        uthreads.uThread.__init__(self, *args, **kwargs)
        self.hist = hist

##
# Useful decorators for process functions

def spawnsBuild(buildName):
    """
    Decorate a build function to create a new IBuildHistory when
    called.  Used like this::
      @spawnsBuild("archtest")
      def archtest():
          # ...
    """
    def d(fn):
        def spawnBuild(*args, **kwargs):
            pth = uthreads.current_thread()
            unique = yield _uniquifyName(buildName, pth.hist)
            subhistory = (yield pth.hist.newBuild(unique))
            subth = ProcessThread(pth.hist, fn, args, kwargs)
            subth.start()
            raise StopIteration(subth)
        return spawnBuild
    return d

def buildStep(stepName):
    """
    Decorate a build function to create a new IStepHistory when called.
    """
    def d(fn):
        def wrapBuildStep(*args, **kwargs):
            pth = uthreads.current_thread()
            unique = yield _uniquifyName(stepName, pth.hist)

            oldhist = pth.hist
            pth.hist = (yield pth.hist.newStep(unique))
            try:
                yield fn(*args, **kwargs)
            finally:
                pth.hist = oldhist
        return wrapBuildStep
    return d

##
# Utility functions

def _uniquifyName(name, hist):
    """Generate a unqiue name for a child of hist by appending a dash and a
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

