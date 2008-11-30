from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import pools, interfaces
from buildbot import uthreads

class Scheduler(pools.PoolMember):
    """
    Parent class for all schedulers.  See
    L{buildbot.framework.interfaces.IScheduler} for requirements
    for subclasses.

    @ivar buildmaster: the buildmaster object; set by the buildmaster
    when the Scheduler is added; available after startService.
    """
    def __init__(self, name):
        pools.PoolMember.__init__(self, name)

    ##
    # Convenience methods for child methods

    def doStartAction(self, action, context):
        """
        Start the scheduler's action by calling action(context).  This
        call is spawned in a separate uThread, so the doStartAction call itself
        will not raise an exception.  The uThread is returned, so the scheduler
        can wait for or otherwise monitor it for results.

        The L{context} object should refer to an IHistoryElt provider, but will
        be adapted just in case.
        """
        def callAction(ctxt):
            ctxt = interfaces.IHistoryElt(ctxt)
            yield action(ctxt)
        uthreads.spawn(callAction(context))
