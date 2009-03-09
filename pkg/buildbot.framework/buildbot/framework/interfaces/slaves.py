"""Interfaces for slaves and remote commands"""

from zope.interface import Interface, Attribute
import uthreads

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

