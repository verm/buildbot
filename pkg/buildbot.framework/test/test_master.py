import os, time
import uthreads
from twisted.trial import unittest
from twisted.application import service
from twisted.internet import defer, reactor
from buildbot.framework import master
from test.base import TestCase
import StringIO

stubclasses = """
from buildbot.framework import interfaces
from zope.interface import implements

from buildbot.framework.sourcemanager import SourceManager
class MySourceManager(SourceManager):
    implements(interfaces.ISourceManager)

from buildbot.framework.slaves import Slave
class MySlave(Slave):
    implements(interfaces.ISlave)

from buildbot.framework.scheduler import Scheduler
class MyScheduler(Scheduler):
    implements(interfaces.IScheduler)
"""

add_one_of_each = """
addSourceManager(MySourceManager('sm'))
addSlave(MySlave('sl', 'pass'))
addScheduler(MyScheduler('sch', lambda stuff : None, None))
"""

just_sourcemgr = """
addSourceManager(MySourceManager('sm2'))
"""

class config(TestCase):
    cfgfile = "master_cfg.py"
    def writeConfig(self, conf):
        open(self.cfgfile, "w").write(conf)
    def tearDown(self):
        if os.path.exists(self.cfgfile):
            os.unlink(self.cfgfile)
        TestCase.tearDown(self)

    @uthreads.returns_deferred
    def testLoadConfig(self):
        bm = master.BuildMaster(".", self.cfgfile)
        self.writeConfig(stubclasses + add_one_of_each)
        yield bm.loadConfig()
        assert len(bm.slaves) == 1
        assert len(bm.sourceManagerPool) == 1
        assert len(bm.schedulerPool) == 1

    @uthreads.returns_deferred
    def testReloadConfig(self):
        bm = master.BuildMaster(".", self.cfgfile)

        self.writeConfig(stubclasses + add_one_of_each)
        yield bm.loadConfig()
        assert len(bm.slaves) == 1
        assert len(bm.sourceManagerPool) == 1
        assert len(bm.schedulerPool) == 1

        self.writeConfig(stubclasses + just_sourcemgr + add_one_of_each)
        yield bm.loadConfig()
        assert len(bm.slaves) == 1
        assert len(bm.sourceManagerPool) == 2
        assert len(bm.schedulerPool) == 1

        self.writeConfig(stubclasses + just_sourcemgr)
        yield bm.loadConfig()
        assert len(bm.slaves) == 0
        assert len(bm.sourceManagerPool) == 1
        assert len(bm.schedulerPool) == 0
