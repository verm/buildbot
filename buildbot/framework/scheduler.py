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

    @uthreads.uthreaded
    def doStartAction(self, sourcestamp):
        """
        Start the scheduler's action by calling C{self.action(ctxt,
        sourcestamp)}.  The uThread is returned, so the scheduler can wait for
        or otherwise monitor it for results.
        """
        hist = interfaces.IHistoryElt(self.project)
        ctxt = process.Context(hist)
        th = (yield self.action(ctxt, sourcestamp))
        raise StopIteration(th)
