from zope.interface import implements
from twisted.python import log, components
from twisted.application import service
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
from buildbot import uthreads

class HistoryManager(service.Service):
    """
    Parent class for all history managers.  See
    L{buildbot.framework.interfaces.IHistoryManager} for requirements
    for subclasses.
    """
    def __init__(self, master, name):
        self.setName(name)
        self.setServiceParent(master)

class HistoryElt(object):
    """
    Base class for history elements.  Note that this class does not fully
    implement L{interfaces.IHistoryElt}, so it does not call C{implements()}
    for that interface.
    """
    @uthreads.uthreaded
    def uniqueName(self, name):
        """Generate a unqiue name for a child element by appending a dash and a
        number.  Microthreaded function."""
        kidNames = yield self.getChildEltKeys()
        if name not in kidNames:
            raise StopIteration(name)
        i = 1
        while 1:
            namenum = "%s-%d" % (name, i)
            if namenum not in kidNames:
                raise StopIteration(namenum)
            i += 1

