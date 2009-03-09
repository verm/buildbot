"""Interfaces for the history hierarchy"""

from zope.interface import Interface, Attribute
import uthreads

class IHistoryManager(Interface):
    """
    A history manager is the central repository for accessing and modifying
    history.  This object is the starting point for all history operations,
    and serves as the root of the history element tree.

    Navigation of this tree is via microthreaded functions so that data
    can be loaded from backend storage systems without blocking.
    """

    @uthreads.uthreaded
    def getElementByIdPath(path):
        """Get an arbitrary element by history element ID path.  Microthreaded function."""

    @uthreads.uthreaded
    def getProjectNames():
        """Get a list of all project names.  Microthreaded function."""

    @uthreads.uthreaded
    def getProject(name, create=False):
        """Get an IProjectHistory object, creating a new one if not found and
        create is True.  Microthreaded function."""

class IHistoryElt(Interface):
    """
    A generic history "element", which may be contained within another
    history element, and which may contain other history elements.  These
    elements structure the actions taken for a particular project into a
    tree, allowing users to "drill down" to see more detailed history.
    """

    historyEltId = Attribute("URL-safe name for the element")

    @uthreads.uthreaded
    def getParentElt():
        """Get this object's parent IHistoryElt.  Microthreaded function."""

    @uthreads.uthreaded
    def getChildElt(key):
        """Get the indicated child of this IHistoryElt; keys are arbitrary,
        short, URL-safe strings.  Microthreaded function."""

    @uthreads.uthreaded
    def getChildEltKeys():
        """Return a list of keys for child elements of this IHistoryElt.
        Microthreaded function."""

    @uthreads.uthreaded
    def getHistoryEltIdPath():
        """Return a tuple of strings which can be used to navigate from the
        buildmaster to this IHistoryElt.  The first item of the tuple names an
        IProjectHistory, and subsequent elements are keys to child elements.
        This tuple is intended to be serialized into a URL.  Microthreaded
        function.  """

    @uthreads.uthreaded
    def newBuild(name):
        """Create a new object providing IBuildHistory, possibly adjusting the
        name to be unique.  Microthreaded function."""

    @uthreads.uthreaded
    def newStep(name):
        """Create a new object providing IStepHistory, possibly adjusting the
        name to be unique.  Microthreaded function."""

class IProjectHistory(IHistoryElt):
    """
    A top-level container for all of the builds associated with a particular
    project.  A project has "shortcuts" to certain IHistoryElts that may be
    of interest to the user.
    """

    projectName = Attribute("Name of the project")

    # TODO: add methods

class IBuildHistory(IHistoryElt):
    """
    A build is an intermediate history element, mapping to the user's concept
    of a "build".  Note that builds may be children of other builds.
    """

    # TODO: add attributes - category, type
    # TODO: zero or more sourcestamps?
    # TODO: start/finish time?
    # TODO: status

class IStepHistory(IHistoryElt):
    """
    A step is an history element representing a single "operation" (from the
    user's perspective) in a build.  It may have logfiles, and may also have
    child history elements.
    """

    # TODO: blobs

    @uthreads.uthreaded
    def newLogfile(name):
        """Create a new object providing IHistoryLogfile.  Microthreaded function."""

class IHistoryLogfile(Interface):
    """
    Represents some textual output from a buildstep
    """

    @uthreads.uthreaded
    def getFilename():
        """get the filename of the logfile on disk"""

