from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import pools, interfaces, process
from buildbot import uthreads

class Scheduler(pools.PoolMember):
    """
    Parent class for all schedulers.  See
    L{buildbot.framework.interfaces.IScheduler} for requirements
    for subclasses.
    """
    def __init__(self, name, action, project=None):
        pools.PoolMember.__init__(self, name)

        self.action = action
        self.project = project

    ##
    # Convenience methods for child methods

    def doStartAction(self):
        """
        Start the scheduler's action by calling action(context).  This
        call is spawned in a separate uThread, so the doStartAction call itself
        will not raise an exception.  The uThread is returned, so the scheduler
        can wait for or otherwise monitor it for results.

        The L{context} object should refer to an IHistoryElt provider, but will
        be adapted just in case.
        """
        context = process.Context(interfaces.IHistoryElt(self.project))
        def callAction():
            yield self.action(context)
        uthreads.spawn(callAction())
