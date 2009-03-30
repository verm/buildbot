import os, sys
from zope.interface import implements
from twisted.python import log
from twisted.internet import defer, reactor, task
from buildbot.framework import sourcemanager, interfaces
from buildbot import uthreads

class DirectorySourceStamp(object):
    def __init__(self, srcmgr, filename):
        self.srcmgr = srcmgr
        self.filename = filename

class DirectorySourceManager(sourcemanager.SourceManager):
    implements(interfaces.ISourceManager)

    def __init__(self, master, name, directory):
        sourcemanager.SourceManager.__init__(self, master=master, name=name)

        if not os.path.exists(directory):
            raise RuntimeError("Directory '%s' does not exist" % directory)
        self.directory = directory
        self.dir_contents = set(os.listdir(directory))

        self.loop = task.LoopingCall(self.checkDir)

    def startService(self):
        self.loop.start(1)

    def stopService(self):
        self.loop.stop()

    def checkDir(self):
        dir_contents = set(os.listdir(self.directory))
        new_files = dir_contents - self.dir_contents
        self.dir_contents = dir_contents

        for f in new_files:
            log.msg("DirectorySourceManager: new file '%s'" % os.path.join(self.directory, f))
            ss = DirectorySourceStamp(self, f)
            self.sendNewSourceStamp(ss)
