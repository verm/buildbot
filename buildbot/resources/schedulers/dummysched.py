import os, sys
from zope.interface import implements
from twisted.python import log
from twisted.internet import defer, reactor
from buildbot.framework import scheduler, interfaces
from buildbot import uthreads

class DummyScheduler(scheduler.Scheduler):
    """
    A Scheduler that triggers a build for each change to the repository.
    """
    implements(interfaces.IScheduler)

    def __init__(self, name, action, *args, **kwargs):
        """
        @param name: name of this scheduler
        """
        scheduler.Scheduler.__init__(self, name)
        self.action = action
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def startService(self):
        assert not self.timer
        self.timer = reactor.callLater(1, self.doBuild)

    def stopService(self):
        if self.timer:
            self.timer.cancel()

    def doBuild(self):
        self.timer = None
        uthreads.spawn(self.action(*self.args, **self.kwargs))
