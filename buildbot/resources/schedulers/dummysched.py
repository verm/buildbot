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

    def __init__(self, name, action, project=None):
        scheduler.Scheduler.__init__(self, name=name, action=action,
                                    project=project)

        self.timer = None

    def startService(self):
        assert not self.timer
        self.timer = reactor.callLater(1, self.doBuild)

    def stopService(self):
        if self.timer:
            self.timer.cancel()

    def doBuild(self):
        self.timer = None
        def waitforit():
            th = self.doStartAction()
            yield th.join()
            print "thread done"
        uthreads.spawn(waitforit())
