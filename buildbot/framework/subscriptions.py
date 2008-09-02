import weakref
from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
from buildbot import uthreads

class Subscription:
    """
    A L{buildbot.framework.interfaces.ISubscription} implementation for
    use with L{SubscriptionHandler}.
    """
    implements(interfaces.ISubscription)
    def __init__(self, callable, handler):
        self.callable = callable
        self.handler = weakref.ref(handler)

    def call(self, args, kwargs):
        try:
            yield self.callable(*args, **kwargs)
        except Exception:
            log.msg("Subscriber callback failed:")
            log.err()

    def cancel(self):
        if not callable: return
        handler = self.handler() # evaluate the weakref
        if not handler: return

        if self in handler.subscribers:
            handler.subscribers.remove(self)

        self.callable = None

class SubscriptionHandler:
    """
    A small utility class to handle subscriptions; this takes care
    of keeping the list of subscribers and doing the dirty work of
    making new calls as necessary.
    """
    def __init__(self):
        self.subscribers = set([])

    def subscribe(self, callable):
        newsub = Subscription(callable, self)
        self.subscribers.add(newsub)
        return newsub

    def __call__(self, *args, **kwargs):
        # make a copy of the set of subscribers to guard against
        # modification while we're iterating
        for sub in list(self.subscribers):
            uthreads.spawn(sub.call(args, kwargs))
