from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
from buildbot import uthreads

class RamHistoryManager(object):
    """
    History manager that simply stores all history in RAM.  The history is not
    saved between runs of the buildmaster, and may consume arbitrary amounts of
    memory if left running for an extended period.
    """

    implements(interfaces.IHistoryManager)

    def __init__(self):
        self.projects = {}

    def getElementByIdPath(self, path):
        elt, path = self.projects[path[0]], path[1:]
        while path:
            elt, path = elt.getChildElt(path[0]), path[1:]
        return elt

    def getProjectNames(self):
        return self.projects.keys()

    def getProject(self, name, create=False):
        if create and not self.projects.has_key(name):
            self.projects[name] = ProjectHistory((name,))
        return self.projects[name]

class HistoryElt(object):
    implements(interfaces.IHistoryElt)

    def __init__(self, historyEltIdPath):
        self.historyEltIdPath = historyEltIdPath
        self.childElts = {}

    def getParentElt(self):
        return self.historyEltIdPath[:-1]

    def getChildElt(self, key):
        return self.childElts[key]

    def getChildEltKeys(self):
        return self.childElts.keys()

    def getHistoryEltIdPath(self):
        return self.historyEltIdPath

    def newBuild(self, key):
        if self.childElts.has_key(key):
            raise KeyError, "%s already has a child named '%s'" % (self, key)
        n = BuildHistory(self.historyEltIdPath + (key,))
        self.childElts[key] = n
        return n

    def newStep(self, key):
        if self.childElts.has_key(key):
            raise KeyError, "%s already has a child named '%s'" % (self, key)
        n = StepHistory(self.historyEltIdPath + (key,))
        self.childElts[key] = n
        return n

class ProjectHistory(HistoryElt):
    implements(interfaces.IProjectHistory)

    def __init__(self, eltidpath):
        HistoryElt.__init__(self, eltidpath)
        self.projectName = eltidpath[:-1]

class BuildHistory(HistoryElt):
    implements(interfaces.IBuildHistory)

    def __init__(self, eltidpath):
        HistoryElt.__init__(self, eltidpath)

class StepHistory(HistoryElt):
    implements(interfaces.IStepHistory)

    def __init__(self, eltidpath):
        HistoryElt.__init__(self, eltidpath)

    def newLogfile(self, name):
        assert not self.childElts.has_key(key)
        n = HistoryLogfile(self.historyEltIdPath + (key,))
        self.childElts[key] = n
        return n

class HistoryLogfile(HistoryElt):
    implements(interfaces.IHistoryLogfile)

    def __init__(self, eltidpath):
        HistoryElt.__init__(self, eltidpath)

    def getFilename(self):
        pass # TODO!
