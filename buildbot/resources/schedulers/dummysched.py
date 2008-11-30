import os, sys
from zope.interface import implements
from twisted.python import log
from twisted.internet import defer, reactor
from buildbot.framework import scheduler, interfaces
from buildbot import uthreads

class DummyScheduler(scheduler.Scheduler):
    """
    A Scheduler that triggers a build after 1 second
    """
    implements(interfaces.IScheduler)

    def __init__(self, name, action, context):
        """
        @param name: name of this scheduler
        """
        scheduler.Scheduler.__init__(self, name=name)
        self.action = action
        self.context = context

        self.timer = None

    def startService(self):
        assert not self.timer
        self.timer = reactor.callLater(1, self.doBuild)

    def stopService(self):
        if self.timer:
            self.timer.cancel()

    def doBuild(self):
        self.timer = None
        self.doStartAction(self.action, self.context)
