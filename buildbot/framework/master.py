import os
import sys
import random

signal = None
try:
    import signal
except ImportError:
    pass

from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from twisted.application import service

from buildbot.framework import exceptions, interfaces, slaves
import buildbot
import buildbot.config

from buildbot import uthreads

class BuildMaster(service.MultiService):
    """
    The BuildMaster is the top-level application for the buildmaster
    process.  It exists basically to control the slave pool, 
    the source manager pool, and the scheduler pool, and to manage the
    configuration file.

    @ivar slaveManager: configured slaves
    @type slaveManager: L{buildbot.framework.slaves.SlaveManager}

    @ivar masterdir: root directory for the buildmaster
    @type masterdir: string
    """

    def __init__(self, masterdir, configFile):
        service.MultiService.__init__(self)

        assert buildbot.buildmaster is None, "only one BuildMaster is allowed per process"
        buildbot.buildmaster = self

        self.setName("buildmaster")
        self.masterdir = masterdir
        self.configFile = configFile

        self.slaveManager = slaves.SlaveManager(self, "SlaveManager")

    def startService(self):
        service.MultiService.startService(self)
        d = self.loadConfig()

        def cb(r):
            log.msg("configuration loaded successfully")
        def eb(f):
            log.msg("Error loading initial config: %s" % f.getErrorMessage())
            log.msg("No previous configuration; shutting down")
            reactor.callWhenRunning(reactor.stop)
        d.addCallbacks(cb, eb)

    def stopService(self):
        service.MultiService.stopService(self)

    @uthreads.returns_deferred
    def loadConfig(self, configFileForTests=None):
        if configFileForTests:
            f = configFileForTests
        else:
            configFile = os.path.join(self.masterdir, self.configFile)

            log.msg("loading configuration from '%s'" % configFile)

            f = open(configFile, "r")

        # create a dictionary from buildbot.config's namespace, omitting private
        # names beginning with a '_'
        localDict = dict((k,v) for (k,v) in buildbot.config.__dict__.iteritems() if k[0] != '_')
        # TODO: do some sort of plugin scan instead

        # add a few variables of our own
        localDict['master'] = self
        localDict['slaveManager'] = self.slaveManager
        localDict['masterdir'] = self.masterdir

        try:
            exec f in localDict
        except:
            log.msg("error while parsing config file")
            raise
