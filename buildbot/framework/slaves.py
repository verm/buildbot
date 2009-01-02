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

    def find(self, filter=None, wait=True):
        if filter is None: filter = lambda x : True
        candidates = [
            sl for sl in self.poolmembers.values()
            if filter(sl)
        ]

        if not candidates:
            raise exceptions.NoAcceptableSlaves

        # TODO: limit to available, block if necessary

        return random.choice(candidates)

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

    @uthreads.uthreaded
    def runCommand(self, command):
        """Run a command (an instance of a subclass of
        L{buildbot.framework.command.Comand}) on the slave.  Returns a
        deferred which fires when the command completes, or fails if
        a Python exception occurs.  The command is responsible for
        collecting any more detailed information."""
        # TODO: stub for now
        yield command.run()
