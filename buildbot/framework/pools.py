from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from twisted.application import service

from buildbot import uthreads

class PoolMember(service.Service):
    """
    A PoolMember is a service that resides in a ServicePool.
    Beyond the usual behaviors of a Twisted service, it has the
    capacity to "upgrade" itself when presented with a new version,
    e.g., from a configuration file.  ServicePool takes care of 
    managing this process.

    @ivar name: (inherited from Service)
    @ivar running: (inherited from Service)
    @ivar oldMember: is this member part of the "old" configuration?
    """
    def __init__(self, name):
        self.setName(name)
        self.isOldMember = False

    def replacePredecessor(self, predecessor):
        """
        This pool member is replacing a predecessor member with the
        same name, and should transition any state information from
        the predecessor.  The predecessor member is still running
        when this function is called, but will be stopped shortly
        afterward, and this member (self) will be started.

        This function is only called when the L{ServicePool}'s
        useNewMembers option is true.
        """

    def emulateNewMember(self, newmemb):
        """
        A new member has been provided with the same name as this one,
        but the L{ServicePool}'s useNewMembers is false, so the new
        member will be discarded.  Before that happens, this function
        should copy any new configuration settings to itself.

        This function is only called when the L{ServicePool}'s
        useNewMembers option is false.
        """

class ServicePool(service.MultiService):
    """
    A ServicePool tracks a set of PoolMember objects, and has
    the capacity to replace the pool with a new set of objects.
    It is used to support incremental upgrades to configuration.
    The PoolMember objects are child services.

    When an upgrade begins, the buildmaster calls markOld, which marks
    all existing members of the pool as "old".  The new configuration
    is loaded, one member at a time, with the following rules for
    each new member:

     - if an old member of the same name already exists, the results
       depend on useNewMembers.  If useNewMembers is true, then
       the pool invokes the new member's X{replacePredecessor} method,
       stops the old member, and starts the new.  Otherwise, the pool
       invokes the old member's X{emulateNewMember} method, then 
       discards the new member.

     - if a new member of the same name exists, that is an error

     - if no member exists with that name, it is added to the pool and
       started.

    When all new PoolMembers have been loaded the buildmaster calls
    removeOld, which removes any remaining old members of the pool.

    The choice of useNewMembers is based on the nature of the pool
    members.  If lots of other Python objects point to each member,
    then it is difficult to replace that member with a new object,
    so set useNewMembers to False.

    @ivar poolmembers: dict of current members of the pool
    """

    def __init__(self, useNewMembers):
        service.MultiService.__init__(self)
        self.useNewMembers = useNewMembers
        self.poolmembers = {}

    def markOld(self):
        """
        Mark all existing members as "old".
        """
        for member in self.poolmembers.itervalues():
            member.isOldMember = True

    def getMemberNames(self):
        """
        Get a list of member names.
        """
        return self.poolmembers.keys()

    def getMemberNamed(self, name):
        """
        Get the member with the given name.
        """
        return self.poolmembers[name]

    @uthreads.uthreaded
    def addMember(self, newmember):
        """
        Add a PoolMember to this pool.  The member should not be started, nor
        should it have a service parent.  Returns a deferred.
        """
        assert isinstance(newmember, PoolMember), "%s is not a PoolMember" % member

        name = newmember.name
        if name in self.poolmembers:
            existing = self.poolmembers[name]
            if existing.isOldMember:
                if self.useNewMembers:
                    newmember.replacePredecessor(existing)
                    del self.poolmembers[name]
                    yield self.removeService(existing)
                else:
                    existing.emulateNewMember(newmember)
                    existing.isOldMember = False
                    return # nothing more to do
            else:
                # TODO: raise configurationerror
                assert 0, "attempt to add two objects with the same name: %s and %s" % (existing, newmember)

        newmember.isOldMember = False
        self.poolmembers[name] = newmember
        self.addService(newmember)

    @uthreads.uthreaded
    def removeOld(self):
        """
        Remove any members of this pool that are still marked as "old".  Returns a deferred.
        """
        for name, member in self.poolmembers.items():
            if member.isOldMember:
                yield self.removeService(member)
                del self.poolmembers[name]
