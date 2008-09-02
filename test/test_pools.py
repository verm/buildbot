import os, time
from buildbot import uthreads
from twisted.trial import unittest
from twisted.application import service
from twisted.internet import defer, reactor
from buildbot.framework import pools

class FakePoolMember(pools.PoolMember):
    def __init__(self, name):
        pools.PoolMember.__init__(self, name)
        self.attr = None

    @uthreads.uthreaded # make this yield a deferred, just to test
    def stopService(self):
        yield uthreads.sleep(0)

    def replacePredecessor(self, pred):
        self.attr = pred.attr

    def emulateNewMember(self, new):
        self.attr = new.attr

class replacement(unittest.TestCase):
    def setUp(self):
        self.pool = None

    def tearDown(self):
        if self.pool and self.pool.running:
            return self.pool.stopService()

    @uthreads.uthreaded
    def testUseNewMembers(self):
        """
        Test simple replacement, using new members.
        """
        self.pool = pool = pools.ServicePool(useNewMembers=True)

        # fill the pool
        initial_names = ['curly', 'larry', 'moe']
        for n in initial_names:
            yield pool.addMember(FakePoolMember(n))

        assert sorted(pool.getMemberNames()) == initial_names, str(pool.getMemberNames())
        old_larry = pool.getMemberNamed('larry')
        old_larry.attr = "attr"

        # start a replacement
        pool.markOld()
        new_names = ['barry', 'jerry', 'larry']
        for n in new_names:
            yield pool.addMember(FakePoolMember(n))
        yield pool.removeOld()

        assert sorted(pool.getMemberNames()) == new_names, str(pool.getMemberNames())
        new_larry = pool.getMemberNamed('larry')
        assert new_larry is not old_larry
        assert new_larry.attr == "attr", "larry didn't correctly inherit attr from his predecessor"

    @uthreads.uthreaded
    def testUseOldMembers(self):
        """
        Test replacement using old members.
        """
        self.pool = pool = pools.ServicePool(useNewMembers=False)
        pool.startService()

        # fill the pool
        old_erika = FakePoolMember("erika")
        yield pool.addMember(old_erika)

        assert sorted(pool.getMemberNames()) == ['erika'], str(pool.getMemberNames())

        # start a replacement
        pool.markOld()
        new_erika = FakePoolMember("erika")
        new_erika.attr = "attr"
        yield pool.addMember(new_erika)
        yield pool.removeOld()

        assert pool.getMemberNamed('erika') is old_erika, "failed to keep the predecessor"
        assert old_erika.running, "old member is not still running"
        assert not new_erika.running, "new member is still running"
        assert old_erika.attr == "attr", "old_erika didn't correctly copy attr from new_erika"
