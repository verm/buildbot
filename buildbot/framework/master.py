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

from buildbot.framework import pools, exceptions, interfaces, slaves
import buildbot
import buildbot.config

from buildbot import uthreads

class BuildMaster(service.MultiService):
    """
    The BuildMaster is the top-level application for the buildmaster
    process.  It exists basically to control the slave pool, 
    the source manager pool, and the scheduler pool, and to manage the
    configuration file.

    @ivar slaves: pool of slaves
    @type slaves: L{buildbot.framework.slaves.SlaveManager}

    @ivar sourceManagerPool: pool of source managers
    @type sourceManagerPool: L{buildbot.framework.pools.ServicePool}

    @ivar schedulerPool: pool of schedulers
    @type schedulerPool: L{buildbot.framework.pools.ServicePool}

    @ivar historyPool: pool of history managers
    @type historyPool: L{buildbot.framework.pools.ServicePool}

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

        self.slaves = slaves.SlaveManager()
        self.slaves.setName("Slave Manager")
        self.slaves.setServiceParent(self)

        self.sourceManagerPool = pools.ServicePool(useNewMembers=True)
        self.sourceManagerPool.setName("SourceManager Pool")
        self.sourceManagerPool.setServiceParent(self)

        self.schedulerPool = pools.ServicePool(useNewMembers=True)
        self.schedulerPool.setName("Scheduler Pool")
        self.schedulerPool.setServiceParent(self)

        self.historyPool = pools.ServicePool(useNewMembers=True)
        self.historyPool.setName("History Pool")
        self.historyPool.setServiceParent(self)

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

        def installhuphandler(r):
            if signal and hasattr(signal, "SIGHUP"):
                signal.signal(signal.SIGHUP, self.handleSIGHUP)
        d.addCallback(installhuphandler)

    def handleSIGHUP(self, *args):
        reactor.callLater(0, self.reconfigService)

    def reconfigService(self):
        d = self.loadConfig()

        def cb(r):
            log.msg("new configuration loaded successfully")
        def eb(f):
            log.msg("Error loading new config: %s" % f.getErrorMessage())
            log.msg("Configuration may be in an inconsistent state")
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

        # add a few variables of our own
        localDict['masterdir'] = self.masterdir

        new_slaves = []
        def addSlave(sl):
            assert interfaces.ISlave.providedBy(sl), \
                "%s is not an ISlave" % sl
            new_slaves.append(sl)
            return sl
        localDict['addSlave'] = addSlave

        new_srcmgrs = []
        def addSourceManager(srcmgr):
            assert interfaces.ISourceManager.providedBy(srcmgr), \
                "%s is not an ISourceManager" % srcmgr
            new_srcmgrs.append(srcmgr)
            return srcmgr
        localDict['addSourceManager'] = addSourceManager

        new_scheds = []
        def addScheduler(sched):
            assert interfaces.IScheduler.providedBy(sched), \
                "%s is not an IScheduler" % sched
            new_scheds.append(sched)
            return sched
        localDict['addScheduler'] = addScheduler

        new_histmgrs = []
        def addHistoryManager(histmgr):
            assert interfaces.IHistoryManager.providedBy(histmgr), \
                "%s is not an IHistoryManager" % histmgr
            new_histmgrs.append(histmgr)
            return histmgr
        localDict['addHistoryManager'] = addHistoryManager

        try:
            exec f in localDict
        except:
            log.msg("error while parsing config file")
            raise

        # update each of the service pools appropriately; this takes care
        # of any necessary starting and stopping of services
        log.msg("updating slaves")
        self.slaves.markOld()
        for slave in new_slaves:
            yield self.slaves.addMember(slave)
        yield self.slaves.removeOld()

        log.msg("updating source managers")
        self.sourceManagerPool.markOld()
        for srcmgr in new_srcmgrs:
            yield self.sourceManagerPool.addMember(srcmgr)
        yield self.sourceManagerPool.removeOld()

        log.msg("updating schedulers")
        self.schedulerPool.markOld()
        for sched in new_scheds:
            yield self.schedulerPool.addMember(sched)
        yield self.schedulerPool.removeOld()

        log.msg("updating history managers")
        self.historyPool.markOld()
        for histmgr in new_histmgrs:
            yield self.historyPool.addMember(histmgr)
        yield self.historyPool.removeOld()
