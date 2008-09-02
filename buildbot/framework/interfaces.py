from zope.interface import Interface

class ISubscription(Interface):
    """
    A "thunk" representing a subscription to some event source;
    its only use is to cancel the subscription.
    """
    def cancel(self):
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

    def subscribeToChanges(self, callable):
        """
        Invoke the given callable in its own uthread with this
        L{ISourceManager} and an L{ISourceStamp} when any changes
        take place in the source-code repository::
            uthreads.spawn(callable(srcmanager, srcstamp))
        
        Returns an L{ISubscription}.
        """

    def getCurrentSourceStamp(self):
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
    def getDescription(self):
        """
        Get a description of this SourceStamp that would allow a person
        to find the specified version.  The string may be arbitrarily long.
        """

    def getFilename(self):
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
    """

class ISlave(Interface):
    """
    A Slave manages the connection from a remote machine.
    """

    def runCommand(self, command):
        """Run a command (L{buildbot.framework.interfaces.ICommand}) on
        the slave.  Returns a deferred which fires when the command
        completes, or fails if a Python exception occurs.  The command
        is responsible for collecting any more detailed information."""

class ICommand(Interface):
    """
    A command which can run on a buildslave, along with its immediate results.
    """

    # TODO temporary
    def run(self):
        """Do the thing; a microthreaded function"""
