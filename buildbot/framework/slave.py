from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import pools, interfaces
from buildbot import uthreads

# TODO: allow *remote* slaves

class Slave(pools.PoolMember):
    """
    Class representing a slave; see L{buildbot.master.interfaces.ISlave}.

    Instances of this class can be used directly in simple
    configurations.  More complex configurations may require a
    subclass.

    @ivar password: the password the remote machine will use when contacting
    the buildmaster
    """
    implements(interfaces.ISlave)

    def __init__(self, name, password):
        pools.PoolMember.__init__(self, name)
        self.password = password

    @uthreads.uthreaded
    def runCommand(self, command):
        """Run a command (an instance of a subclass of
        L{buildbot.framework.command.Comand}) on the slave.  Returns a
        deferred which fires when the command completes, or fails if
        a Python exception occurs.  The command is responsible for
        collecting any more detailed information."""
        # TODO: stub for now
        yield command.run()
