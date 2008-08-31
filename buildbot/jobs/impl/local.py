"""Trivial implementation of job control to simply run commands locally.  """

import os
import types
from buildbot import interfaces
from zope.interface import implements
from twisted.internet import reactor, defer, task, error
import twisted.internet.interfaces
from twisted.python import log, failure, runtime

class LocalRemoteSystem(object):
    implements(interfaces.IRemoteSystem)

    def __init__(self, name, basedir):
        """Create a new object; mulitple LocalRemoteSystems can run on the same
        system, and will not interfere as long as their basedirs do not
        overlap."""
        self.name = name
        self.basedir = basedir
        self.activeCommands = []

        if not os.path.exists(basedir):
            os.makedirs(basedir)

    def __repr__(self):
        return "<LocalRemoteSystem '%s'>" % self.name

    def newCommand(self, **kwargs):
        cmd = LocalRemoteCommand(remote=self, **kwargs)
        self.activeCommands.append(cmd)
        return cmd

class LocalRemoteCommand(object):
    implements(interfaces.IRemoteCommand, twisted.internet.interfaces.IProcessProtocol)

    def __init__(self, remote=None, command=None, env=None, setEnv=None, cwd=None):
        assert isinstance(remote, LocalRemoteSystem)
        self.remote = remote
        assert isinstance(command, types.ListType)
        self.command = command
        assert isinstance(env, types.DictType) or env is None
        self.env = env
        assert isinstance(setEnv, types.DictType) or setEnv is None
        self.setEnv = setEnv
        self.cwd = cwd

        self.state = 'new'

    def run(self):
        assert self.state == 'new'
        self.state = 'running'

        # set up parameters

        if runtime.platformType  == 'win32':
            argv = [ os.environ['COMSPEC'], '/c' ] + list(self.command)
        else:
            argv = self.command

        if self.env is not None:
            env = self.env.copy()
        else:
            env = os.environ.copy()

        if self.setEnv is not None:
            env.update(self.setEnv)

        cwd = os.path.join(self.remote.basedir, self.cwd or '')
        env['PWD'] = cwd

        # win32eventreactor's spawnProcess (under twisted <= 2.0.1) returns
        # None, as opposed to all the posixbase-derived reactors (which
        # return the new Process object). This is a nuisance. We can make up
        # for it by having the ProcessProtocol give us their .transport
        # attribute after they get one. I'd prefer to get it from
        # spawnProcess because I'm concerned about returning from this method
        # without having a valid self.process to work with. (if kill() were
        # called right after we return, but somehow before connectionMade
        # were called, then kill() would blow up).
        self.process = None
        p = reactor.spawnProcess(self, argv[0], argv, env, cwd)
        if p is not None and self.process is None:
            self.process = p

        self.proc_deferred = defer.Deferred()
        return self.proc_deferred

    ## IProcessProtocol methods

    def makeConnection(self, process):
        if self.process is None:
            self.process = process

    def childDataReceived(self, childFD, data):
        pass

    def childConnectionLost(self, childFD):
        pass

    def processEnded(self, reason):
        self.state = 'done'
        self.process = None

        # contrary to the API docs, reason is a list
        if type(reason) is types.ListType:
            reason = reason[0]

        if isinstance(reason.value, (error.ProcessDone, error.ProcessTerminated)):
            self.exitstatus = reason.value.status
            self.proc_deferred.callback(self)
        else:
            self.exitstatus = -1
            self.proc_deferred.errback(reason)
