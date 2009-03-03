import os
import weakref
import shutil
from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces, slaves
import uthreads
import buildbot

class DummySlaveEnvironment(object):
    implements(interfaces.ISlaveEnvironment)

    def __init__(self, slavename, name):
        self.slavename = slavename
        self.name = name
        self.basepath = self.cwd = os.path.join(
            buildbot.buildmaster.masterdir,
            "slaves", slavename, name)
        self.env = os.environ.copy()

        os.makedirs(self.basepath)

    ## filesystem operations

    @uthreads.uthreaded
    def chdir(self, ctxt, newdir, baseRelative=False):
        # TODO add IStepHistory
        if baseRelative:
            self.cwd = os.path.join(self.basepath, newdir)
        else:
            self.cwd = os.path.join(self.cwd, newdir)
        print "changing directory to '%s'" % self.cwd
    
    @uthreads.uthreaded
    def rename(self, ctxt, srcfilename, destfilename):
        # TODO add IStepHistory
        os.rename(srcfilename, destfilename)
    
    @uthreads.uthreaded
    def remove(self, ctxt, filename, recursive=False):
        # TODO add IStepHistory
        if recursive:
            shutil.rmtree(filename)
        else:
            os.remove(filename)
    
    @uthreads.uthreaded
    def mkdir(self, ctxt, filename):
        # TODO add IStepHistory
        os.makedirs(filename)
    
    ## environment

    @uthreads.uthreaded
    def getEnv(self, ctxt):
        return self.env.copy()

    @uthreads.uthreaded
    def setEnv(self, ctxt, **kwargs):
        # TODO add IStepHistory
        self.env.update(kwargs)

    ## file transfers

    @uthreads.uthreaded
    def upload(self, ctxt, srcfilename, destfile):
        # TODO add IStepHistory
        src = open(srcfilename, "r")
        blocksize = 32768
        while 1:
            d = src.read(blocksize)
            if d == '': break
            destfile.write(d)

    @uthreads.uthreaded
    def download(self, ctxt, srcfile, destfilename,
                 destperms=None, destuser=None, destgroup=None):
        # TODO add IStepHistory
        dest = open(destfilename, "w")
        if destperms:
            os.chmod(destfilename, destperms)
        if destuser or destgroup:
            # TODO: translate names to id's, supply -1, etc.
            os.chown(destfilename, destuser, destgroup)
        blocksize = 32768
        while 1:
            d = srcfile.read(blocksize)
            if d == '': break
            dest.write(d)

    ## shell commands

    @uthreads.uthreaded
    def shellCommand(self, ctxt, command, name=None):
        if name is None: name = command.split()[0]
        histelt = (yield ctxt.hist.newStep(name))
        print "running %r on slave %s (well, really on the master)" % (command, self.slavename)
        os.chdir(self.cwd)
        # TODO: use something more flexible than "system"!
        os.system(command)

class DummySlave(slaves.Slave):
    def __init__(self, name, password):
        slaves.Slave.__init__(self, name, password)
        self.envs = weakref.WeakValueDictionary()

    @uthreads.uthreaded
    def getSlaveEnvironment(self, name):
        # TODO: make this an exception, as it will probably happen often
        assert name not in self.envs, \
            "SlaveEnvironment on '%s' with name '%s' is already active" % (self.name, name)
        slenv = DummySlaveEnvironment(self.name, name)
        self.envs[name] = slenv
        return  slenv
