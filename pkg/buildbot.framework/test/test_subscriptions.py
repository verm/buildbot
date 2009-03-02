import os, time
import uthreads
from test.base import TestCase
from twisted.internet import defer, reactor
from buildbot.framework import subscriptions

class t(TestCase):
    @uthreads.returns_deferred
    def testSubscription(self):
        """
        Test things the way they're supposed to work
        """
        subs = subscriptions.SubscriptionHandler()
        mutable = [ False, False ]
        def set0(arg):
            mutable[0] = arg
        def set1(arg):
            yield uthreads.sleep(0.15)
            mutable[1] = arg

        subs.subscribe(set0)
        subs.subscribe(set1)
        assert mutable == [ False, False ], "Mutable is %s" % (mutable,)
        yield subs(True)
        yield uthreads.sleep(0.1)
        assert mutable == [ True, False ], "Mutable is %s" % (mutable,)
        yield uthreads.sleep(0.1)
        assert mutable == [ True, True ], "Mutable is %s" % (mutable,)

    @uthreads.returns_deferred
    def dont_testException(self):
        """
        Test an exception in the callback
        """
        # Unfortunately, an exception in a callback uthread calls log.err,
        # which unittest intercepts and determines that the test has failed.
        # TODO: use self.flushLoggedErrors(MyError) to check that errors
        # were thrown and flush them at the same time. (function is not
        # present in Twisted 2.4)
        class MyError(Exception): pass
        subs = subscriptions.SubscriptionHandler()
        def fail():
            raise MyError
        def fail_uthreaded():
            yield
            raise MyError
        subs.subscribe(fail)
        subs.subscribe(fail_uthreaded)

        yield subs()

    @uthreads.returns_deferred
    def testCancel(self):
        """
        Test cancelling a subscription
        """
        subs = subscriptions.SubscriptionHandler()
        mutable = [ True ]
        def fn(): mutable[0] = False
        s = subs.subscribe(fn)
        s.cancel()
        yield subs()
        assert mutable[0], "fn shouldn't have been called, but it was"
