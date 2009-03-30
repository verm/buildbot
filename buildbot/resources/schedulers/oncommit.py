import os, sys
from zope.interface import implements
from twisted.python import log
from twisted.internet import defer, reactor
from buildbot.framework import scheduler, interfaces
from buildbot import uthreads

class OnCommitScheduler(scheduler.Scheduler):
    implements(interfaces.IScheduler)

    def __init__(self, name, action, project, sourcemanager):
        scheduler.Scheduler.__init__(self, name=name, action=action,
                                    project=project)
        self.sourcemanager = sourcemanager
        self.subscription = None

    def startService(self):
        self.subscription = self.sourcemanager.subscribeToChanges(self.newSource)

    def stopService(self):
        if self.subscription:
            self.subscription.cancel()
            self.subscription = None

    @uthreads.uthreaded
    def newSource(self, ss):
        # TODO: treeStableTimer
        yield self.doStartAction(sourcestamp=ss)
