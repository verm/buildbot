from zope.interface import implements
from twisted.python import log, components
from twisted.application import service
from twisted.internet import defer, reactor
from buildbot.framework import pools, subscriptions
from buildbot import uthreads

class SourceManager(service.Service):
    """
    Parent class for all source managers.  See 
    L{buildbot.framework.interfaces.ISourceManager} for requirements
    for subclasses.
    """
    def __init__(self, master, name):
        def becomeOwned():
            self.setName(name)
            self.setServiceParent(master)
        reactor.callWhenRunning(becomeOwned)

        self.subscribers = subscriptions.SubscriptionHandler()

    ## subscription management

    def subscribeToChanges(self, callable):
        return self.subscribers.subscribe(callable)

    def sendNewSourceStamp(self, ss):
        """
        Send the given SourceStamp to all subscribers.  This should
        only be called from subclasses.  Returns a deferred.
        """
        return self.subscribers.notify(ss)
