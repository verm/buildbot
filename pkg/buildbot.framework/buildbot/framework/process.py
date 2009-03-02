import copy
from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
import uthreads

class Context(object):
    """
    The current status of the build process.  This is passed around as 'ctxt' in
    all process-related functions.  See L{interfaces.IContext} for a description
    of the class attributes.
    """
    implements(interfaces.IContext)

    def __init__(self, project):
        self.hist = project

    def subcontext(self, **kwargs):
        ctxt = copy.copy(self)
        for k,v in kwargs.iteritems():
            setattr(ctxt, k, v)
        ctxt.parent = self
        return ctxt

##
# Useful decorators for process functions

def action(fn):
    def spawn(ctxt, sourcestamp):
        th = uthreads.spawn(fn(ctxt, sourcestamp))
        return th
    return spawn

def build(buildName):
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
        @uthreads.uthreaded
        def spawnBuild(ctxt, *args, **kwargs):
            subctxt = ctxt.subcontext(
                hist=(yield ctxt.hist.newBuild(buildName)))
            th = uthreads.spawn(fn(subctxt, *args, **kwargs))
            raise StopIteration(th)
        return spawnBuild
    return d

def step(stepName):
    """
    Decorate a build function to create a new IStepHistory when called.
    """
    def d(fn):
        @uthreads.uthreaded
        def wrapStep(ctxt, *args, **kwargs):
            subctxt = ctxt.subcontext(
                hist=(yield ctxt.hist.newStep(stepName)))
            yield fn(subctxt, *args, **kwargs)
        return wrapStep
    return d
