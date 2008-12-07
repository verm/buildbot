from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import pools, subscriptions
from buildbot import uthreads

class SourceManager(pools.PoolMember):
    """
    Parent class for all source managers.  See 
    L{buildbot.framework.interfaces.ISourceManager} for requirements
    for subclasses.
    """
    def __init__(self, name):
        pools.PoolMember.__init__(self, name)
        self.subscribers = subscriptions.SubscriptionHandler()

    ## subscription management

    def subscribeToChanges(self, callable):
        return self.subscribers.subscribe(callable)

    def sendNewSourceStamp(self, ss):
        """
        Send the given SourceStamp to all subscribers.  This should
        only be called from subclasses.  Returns a deferred.
        """
        return self.subscribers(self, ss)
