"""Interfaces for handling source cod."""

from zope.interface import Interface, Attribute
import uthreads

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

