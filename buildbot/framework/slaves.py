import random
from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from twisted.application import service
from buildbot.framework import pools, interfaces, process, exceptions
from buildbot import uthreads

# TODO: allow *remote* slaves

class SlaveManager(service.Service, pools.Pool):
    """
    See L{interfaces.ISlaveManager}.
    """
    def __init__(self):
        pools.Pool.__init__(self, useNewMembers=False)

    @uthreads.uthreaded
    def getSlaveEnvironment(self, name, filter=None, wait=True):
        if filter is None: filter = lambda x : True
        candidates = [
            sl for sl in self.poolmembers.values()
            if filter(sl)
        ]

        if not candidates:
            raise exceptions.NoAcceptableSlaves

        # TODO: limit to available, block if necessary

        # TODO: shell out to load balancing algo
        slave = random.choice(candidates)

        slenv = (yield slave.getSlaveEnvironment(name))
        assert interfaces.ISlaveEnvironment.providedBy(slenv)
        raise StopIteration(slenv)

    @uthreads.uthreaded
    def stopMember(self, slave):
        pass
        # slave.forceDisconnect()

    # TODO: stopService -> stop all members

class Slave(pools.PoolMember):
    """
    Class representing a slave; see L{interfaces.ISlave}.

    Instances of this class can be used directly in simple configurations.
    More complex configurations may require a subclass.

    @ivar password: the password the remote machine will use when contacting
    the buildmaster
    """
    implements(interfaces.ISlave)

    def __init__(self, name, password):
        pools.PoolMember.__init__(self, name)
        self.password = password

    # TODO: emulateNewMember
