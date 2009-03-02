import os, shutil
from test.base import TestCase
from twisted.internet import reactor, defer
from twisted.python import log
#from buildbot.jobs.impl.local import LocalRemoteSystem

class testImplLocal(TestCase):
    def setUp(self):
        self.workdir = os.path.abspath("trial-jobs")
        if os.path.exists(self.workdir):
            log.msg("removing '%s'" % self.workdir)
            shutil.rmtree(self.workdir)

        # make sure the twisted reactor is running
        d = defer.Deferred()
        reactor.callWhenRunning(d.callback, None)
        return d

    def tearDown(self):
        if os.path.exists(self.workdir):
            log.msg("removing '%s'" % self.workdir)
            shutil.rmtree(self.workdir)

    def no_testBasicRun(self):
        remsys = LocalRemoteSystem('test',
            os.path.join(self.workdir, "test"))
        cmd = remsys.newCommand(command=['true'])
        return cmd.run()

    def no_testRunStatus(self):
        remsys = LocalRemoteSystem('test',
            os.path.join(self.workdir, "test"))
        cmd = remsys.newCommand(command=['false'])
        def ck(cmd):
            assert os.WIFEXITED(cmd.exitstatus)
            assert os.WEXITSTATUS(cmd.exitstatus) != 0
        return cmd.run().addCallback(ck)
