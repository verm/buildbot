from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import pools, interfaces, process
from buildbot import uthreads

class Scheduler(pools.ServicePoolMember):
    """
    Parent class for all schedulers.  See
    L{buildbot.framework.interfaces.IScheduler} for requirements
    for subclasses.
    """
    def __init__(self, name, action, project=None):
        pools.ServicePoolMember.__init__(self, name)

        self.action = action
        self.project = project

    ##
    # Convenience methods for child methods

    def doStartAction(self):
        """
        Start the scheduler's action by calling action().  This call is spawned
        in a separate uThread, so the doStartAction call itself will not raise
        an exception.  The uThread is returned, so the scheduler can wait for
        or otherwise monitor it for results.
        """
        def runAction(ctxt):
            x = (yield self.action(ctxt))
            # if action() just triggered a build, then wait for it to finish
            if isinstance(x, uthreads.uThread):
                yield x.join()
            # otherwise, action did something else (probably running a bunch of threads),
            # and is now finished, so this thread is finished, too

        hist = interfaces.IHistoryElt(self.project)
        ctxt = process.Context(hist)
        return uthreads.spawn(runAction(ctxt))
