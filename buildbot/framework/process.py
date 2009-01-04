import copy
from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
from buildbot import uthreads

class Context(object):
    """
    The current status of the build process.  This is passed around as 'ctxt' in
    all process-related functions.  See L{interfaces.IContext} for a description
    of the class attributes.
    """
    implements(interfaces.IContext)

    def __init__(self, project):
        self.hist = project
        self.slenv = None

    def subcontext(self, **kwargs):
        ctxt = copy.copy(self)
        for k,v in kwargs.iteritems():
            setattr(ctxt, k, v)
        return ctxt

##
# Useful decorators for process functions

def spawnsBuild(buildName):
    """
    Decorate a build function to create a new IBuildHistory when
    called.  Used like this::
      @spawnsBuild("archtest")
      def archtest(arch):
          # ...

    Note that the new build runs in its own uThread, and begins with no slave
    environments available.  The decorated function will return its uThread::
      archthreads = [ archtest(arch) for arch in architectures ]
    """
    def d(fn):
        def spawnBuild(ctxt, *args, **kwargs):
            subctxt = ctxt.subcontext(
                hist=(yield ctxt.hist.newBuild(buildName)),
                slenv=None)
            th = uthreads.spawn(fn(subctxt, *args, **kwargs))
            raise StopIteration(th)
        return spawnBuild
    return d

def buildStep(stepName):
    """
    Decorate a build function to create a new IStepHistory when called.
    """
    def d(fn):
        def wrapBuildStep(ctxt, *args, **kwargs):
            subctxt = ctxt.subcontext(
                hist=(yield ctxt.hist.newStep(stepName)))
            yield fn(subctxt, *args, **kwargs)
        return wrapBuildStep
    return d
