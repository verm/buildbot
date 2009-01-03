import os
import weakref
from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces, slaves
from buildbot import uthreads
import buildbot

class DummySlaveEnvironment(object):
    implements(interfaces.ISlaveEnvironment)

    def __init__(self, slavename, name):
        self.slavename = slavename
        self.name = name
        self.path = os.path.join(
            buildbot.buildmaster.masterdir,
            "slaves", slavename, name)
        os.makedirs(self.path)

    def runCommand(self, command):
        print "running %r on slave %s" % (command, self.slavename)
        os.chdir(self.path)
        os.system(command)

class DummySlave(slaves.Slave):
    def __init__(self, name, password):
        slaves.Slave.__init__(self, name, password)
        self.envs = weakref.WeakValueDictionary()

    def getSlaveEnvironment(self, name):
        # TODO: make this an exception, as it will probably happen often
        assert name not in self.envs, \
            "SlaveEnvironment on '%s' with name '%s' is already active" % (self.name, name)
        slenv = DummySlaveEnvironment(self.name, name)
        self.envs[name] = slenv
        return  slenv
