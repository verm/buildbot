from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import pools
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
