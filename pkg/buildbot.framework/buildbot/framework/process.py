import copy
from zope.interface import implements, directlyProvides
from zope.interface import noLongerProvides, classProvides
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
        self.parent = None
        self.hist = project

    def subcontext(self, **kwargs):
        ctxt = copy.copy(self)
        for k,v in kwargs.iteritems():
            setattr(ctxt, k, v)
        ctxt.parent = self
        return ctxt

##
# Top-level BuildProcess class

class BuildProcess(object):
    """

    @ivar _uthread: the microthread in which run() is running
    """

    classProvides(interfaces.IBuildProcessFactory)

    ## IBuildProcessFactory methods

    def __init__(self, **kwargs):
        self.args = kwargs
        directlyProvides(self, interfaces.IBuildProcessFactory)

    def _promote_factory_to_process(self):
        assert interfaces.IBuildProcessFactory.providedBy(self), \
            "this object is not a factory"
        noLongerProvides(self, interfaces.IBuildProcessFactory)
        directlyProvides(self, interfaces.IBuildProcess)
        
    def __call__(self, **kwargs):
        newargs = self.args.copy()
        newargs.update(kwargs)
        return self.__class__(**newargs)

    def spawn(self, ctxt, **kwargs):
        assert interfaces.IBuildProcessFactory.providedBy(self), \
            "this object is not a factory"
        sub = self(**kwargs)
        sub._promote_factory_to_process()

        @uthreads.uthreaded
        def kick_off_build():
            subctxt = yield sub.make_context(ctxt)
            yield sub.run(subctxt, **sub.args)

        sub._uthread = uthreads.spawn(kick_off_build())

        return sub

    ## IBuildProcess methods

    @uthreads.uthreaded
    def run(self, ctxt, **kwargs):
        assert interfaces.IBuildProcess.providedBy(self), \
            "call spawn() to start a new build"
        raise NotImplementedError("You should override the run() method")

    @uthreads.uthreaded
    def make_context(self, ctxt):
        subhist = yield ctxt.hist.newBuild(self.make_history_name)
        raise StopIteration(ctxt.subcontext(hist=subhist))

    def make_history_name(self, ctxt):
        return self.__class__.__name__

##
# Useful decorators for process functions

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
