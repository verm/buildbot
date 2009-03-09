"""Interfaces for the master and objects it interacts with"""

from zope.interface import Interface, Attribute
import uthreads

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

