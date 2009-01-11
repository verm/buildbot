from zope.interface import Interface, Attribute
from buildbot import uthreads

class ISubscription(Interface):
    """
    A "thunk" representing a subscription to some event source;
    its only use is to cancel the subscription.
    """
    def cancel():
        """Cancel the subscription."""

class ISourceManager(Interface):
    """
    A source manager is responsible for:
     - monitoring a specific source-code repository, providing
       callbacks when the source changes.
     - producing a SourceStamp for the "current" state of the
       repository on demand
     - providing additional information about SourceStamps on
       demand (previous, blamelist, changes, affected files, etc.)

    All source manager classes must be subclasses of
    L{buildbot.framework.pools.PoolMember}.
    """

    def subscribeToChanges(callable):
        """
        Invoke the given callable in its own uthread with this
        L{ISourceManager} and an L{ISourceStamp} when any changes
        take place in the source-code repository::
            uthreads.spawn(callable(srcmanager, srcstamp))
        
        Returns an L{ISubscription}.
        """

    def getCurrentSourceStamp():
        """
        Get the L{ISourceStamp} for the current state of the
        repository.
        """

    # TODO: additional information

class ISourceStamp(Interface):
    """
    A SourceStamp represents, as accurately as possible, a specific
    "version" of the source code controlled by a L{ISourceManager}.
    The precise format depends on the version-control system in use
    by the L{ISourceManager}.
    """
    def getDescription():
        """
        Get a description of this SourceStamp that would allow a person
        to find the specified version.  The string may be arbitrarily long.
        """

    def getFilename():
        """
        Get a short string suitable for use in a filename that identifies
        this SourceStamp and has a minimal probability of clashing with
        any other SourceStamps.  Since that the SourceStamp is never 
        reconstructed from a filename, long SourceStamps can simply use a
        hash as the filename.
        """

class IScheduler(Interface):
    """
    A Scheduler starts builds.  It may do this by subscribing to a
    SourceManager, or by some kind of timer, or some other means.

    A scheduler's constructor should take, among other arguments:
     - name - scheduler name
     - action -- the function to call to start a build, and
     - project or context -- the context to pass to that function -- either an
       IProjectHistory provider or an IContext object.
    
    L{buildbot.framework.scheduler} provides convenient methods to
    implement a scheduler.
    """

##
# Slaves and remote commands

class ISlaveManager(Interface):
    """
    A SlaveManager manages the pool of available slaves.  There is usually only one
    SlaveManager, located at C{buildbot.buildmaster.slaves}.

    The SlaveManager is responsible for coordinating communication with remote
    slaves, for maintaining the list of available slaves and load-balancing
    between them, and for supplying slaves to build processes.

    A slave may be considered "unavailable" if it is known to the SlaveManager,
    but not currently ready to perform build actions, perhaps because it is not
    connected.  The load-balancing algorithm can also mark a slave as
    unavailable, for example if its load average is too high.  In general, Buildbot
    will wait for unavailable slaves.
    """

    @uthreads.uthreaded
    def find(filter=None, wait=True):
        """Find a slave to build on.  C{filter} is a function taking an
        L{ISlave} provider and returning True if the slave is acceptable.  If
        several slaves are acceptable, the current load-balancing algorithm
        will be applied.  If no slaves are acceptable, C{find} will raise
        C{NoAcceptableSlaves}.  If the selected slave is not available and
        C{wait} is true, this function blocks until an acceptable, available
        slave is found; if C{wait} is false, then it returns None. Microthreaded
        method."""

class ISlave(Interface):
    """
    A Slave manages the connection from a remote machine.
    """

    @uthreads.uthreaded
    def getSlaveEnvoronment(name):
        """Get an L{ISlaveSlaveEnvironment} provider with the given name.  The
        name is used to choose the initial working directory, and should not
        conflict with other, active slave environments.  It is not an error for
        the directory to exist already, but it should be created if
        necessary.  Microthreaded function"""

class ISlaveEnvironment(Interface):
    """
    A slave environment represents a particular set of conditions on a slave,
    including a working directory, environment variables, and so on.   It is
    the context in which the slave can execute commands.

    All of the methods on slave environments create a new L{IStepHistory}
    element to record the details of the operation.
    """

    ## filesystem operations

    @uthreads.uthreaded
    def chdir(ctxt, newdir, baseRelative=False):
        """Change the "current directory" for this slave environment.  If
        C{baseRelative} is true, then newdir is interpreted with respect to
        the initial/base directory.  Microthreaded function."""

    @uthreads.uthreaded
    def rename(ctxt, srcfilename, destfilename):
        """Use the L{os.rename} function to rename C{srcfilename} to
        C{destfilename}.  This is subject to the usual restrictions of
        L{os.rename} on the slave system.  Microthreaded function."""

    @uthreads.uthreaded
    def remove(ctxt, filename, recursive=False):
        """Remove C{filename}, optionally recursively removing whole
        directories.  Microthreaded function."""

    @uthreads.uthreaded
    def mkdir(ctxt, filename):
        """Create the directory C{filename}, including any intervening
        directories.  Microthreaded function."""

    ## environment

    @uthreads.uthreaded
    def getEnv(ctxt):
        """Return a dictionary containing all environment variables in the
        slave environment.  Microthreaded function."""

    @uthreads.uthreaded
    def setEnv(ctxt, **kwargs):
        """Update environment variables on the slave, e.g.,::
             slenv.setEnv(PATH="/usr/bin", HOME="/home/foo")

        Specifying a value of C{None} will unset the environment variable."""

    ## file transfers

    @uthreads.uthreaded
    def upload(ctxt, srcfilename, destfile):
        """Upload C{srcfilename} from the slave, writing the data to the
        file-like object C{destfile}.  Microthreaded function."""

    @uthreads.uthreaded
    def download(ctxt, srcfile, destfilename,
                 destperms=None, destuser=None, destgroup=None):
        """Download data from th file-like object C{srcfile} to the slave,
        writing the data to C{destfilename}.  If C{destperms}, C{destuser},
        and/or C{destgroup} are given, then they are applied to the resulting
        file.  Microthreaded function."""

    ## shell commands

    @uthreads.uthreaded
    def shellCommand(ctxt, command, name=None):
        """Run a command (L{buildbot.framework.interfaces.ICommand}) on
        the slave.  Results of the command are as-yet undefined.  Microthreaded
        function.
        
        If C{name} is specified, it is used as the name of the resulting
        L{IStepHistory}.
        """

class ICommand(Interface):
    """
    A command which can run on a buildslave, along with its immediate results.
    """

    # TODO temporary
    def run():
        """Do the thing; a microthreaded function"""

## Processing

class IContext(Interface):
    """
    A context object conveniently (and extensibly) encapsulates the current
    state of processing of a particular build.
    """

    parent = Attribute("""Parent context, or None if this is the top level""")
    hist = Attribute("""Current L{IHistoryElt} provider""")

    def subcontext(hist=None):
        """Create a shallow copy of this context object for use in a sub-step
        or sub-build.  Keyword arguments are used to override attributes in
        the subcontext."""

## History
#
# These interfaces represent the history of what Buildbot has done

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
