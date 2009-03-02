from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces, history
from buildbot import uthreads

class RamHistoryManager(history.HistoryManager):
    """
    History manager that simply stores all history in RAM.  The history is not
    saved between runs of the buildmaster, and may consume arbitrary amounts of
    memory if left running for an extended period.
    """

    implements(interfaces.IHistoryManager)

    def __init__(self, name="history"):
        self.projects = {}

    @uthreads.uthreaded
    def getElementByIdPath(self, path):
        elt, path = self.projects[path[0]], path[1:]
        while path:
            elt, path = elt.getChildElt(path[0]), path[1:]
        return elt

    @uthreads.uthreaded
    def getProjectNames(self):
        return self.projects.keys()

    @uthreads.uthreaded
    def getProject(self, name, create=False):
        if create and not self.projects.has_key(name):
            self.projects[name] = ProjectHistory((name,))
        return self.projects[name]

class HistoryElt(history.HistoryElt):
    implements(interfaces.IHistoryElt)

    def __init__(self, historyEltIdPath):
        self.historyEltIdPath = historyEltIdPath
        self.childEltsKeys = []
        self.childElts = {}

    @uthreads.uthreaded
    def getParentElt(self):
        return self.historyEltIdPath[:-1]

    @uthreads.uthreaded
    def getChildElt(self, key):
        return self.childElts[key]

    @uthreads.uthreaded
    def getChildEltKeys(self):
        return self.childEltsKeys

    @uthreads.uthreaded
    def getHistoryEltIdPath(self):
        return self.historyEltIdPath

    @uthreads.uthreaded
    def newBuild(self, name):
        key = (yield self.uniqueName(name))
        n = BuildHistory(self.historyEltIdPath + (key,))
        self.childEltsKeys.append(key)
        self.childElts[key] = n
        raise StopIteration(n)

    @uthreads.uthreaded
    def newStep(self, name):
        key = (yield self.uniqueName(name))
        n = StepHistory(self.historyEltIdPath + (key,))
        self.childEltsKeys.append(key)
        self.childElts[key] = n
        raise StopIteration(n)

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

    @uthreads.uthreaded
    def newLogfile(self, name):
        assert not self.childElts.has_key(key)
        n = HistoryLogfile(self.historyEltIdPath + (key,))
        self.childElts[key] = n
        return n

class HistoryLogfile(HistoryElt):
    implements(interfaces.IHistoryLogfile)

    def __init__(self, eltidpath):
        HistoryElt.__init__(self, eltidpath)

    @uthreads.uthreaded
    def getFilename(self):
        pass # TODO!
