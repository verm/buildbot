import random
from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from twisted.application import service
from buildbot.framework import interfaces, process, exceptions
from buildbot import uthreads

# TODO: allow *remote* slaves

class SlaveManager(service.MultiService):
    """
    See L{interfaces.ISlaveManager}.
    """
    def __init__(self, master, name):
        service.MultiService.__init__(self)
        def becomeOwned():
            self.setName(name)
            self.setServiceParent(master)
        reactor.callWhenRunning(becomeOwned)

        self.slaves = []

    @uthreads.uthreaded
    def getSlaveEnvironment(self, name, filter=None, wait=True):
        if filter is None: filter = lambda x : True
        candidates = [
            sl for sl in self.slaves
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

    def addSlave(self, slave):
        slave.setManager(self)
        self.slaves.append(slave)

class Slave(service.Service):
    """
    Class representing a slave; see L{interfaces.ISlave}.

    Instances of this class can be used directly in simple configurations.
    More complex configurations may require a subclass.

    @ivar name: the name of this buildslave

    @ivar password: the password the remote machine will use when contacting
    the buildmaster
    """
    implements(interfaces.ISlave)

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def setManager(self, mgr):
        self.setName(self.name)
        self.setServiceParent(mgr)
