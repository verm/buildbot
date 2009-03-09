"""Interfaces for processing builds"""

from zope.interface import Interface, Attribute
import uthreads

class IContext(Interface):
    """
    A context object conveniently (and extensibly) encapsulates the current
    state of processing of a particular build.
    """

    parent = Attribute("""Parent context, or None if this is the top level""")
    hist = Attribute("""Current L{IHistoryElt} provider""")

    def subcontext(hist=None):
        """Create a shallow copy of this context object for use in a sub-step
        or sub-build.  The keyword arguments listed in the signature are all
        optional, and can be used to override the eponymous attributes in the
        subcontext."""

class IBuildProcessFactory(Interface):
    """
    Most L{IBuildProcess} objects also double as factories.  This allows them
    to take keyword arguments at several points, combining the results.  The
    L{buildbot.frramework.process.BuildProcess} class takes care of these
    mechanics.  Note that this blurs the provider/implementer distinction.
    """

    def __call__(**kwargs):
        """Create a new L{IBuildProcessFactory} provider with the arguments of
        this object, updated with C{kwargs}."""

    def spawn(ctxt, **kwargs):
        """Begin the build process in earnest.  Returns a I{new} instance,
        updated with C{kwargs}.  The new object is already running, and
        provides L{IBuildProcess}.  Its history will be a child of that in
        C{ctxt}."""


class IBuildProcess(Interface):
    """
    An IBuildProcess directs a build.

    Users specify implementstions of this interface to schedulers, which spawn
    new instances in response to source-code changes.
    """

    args = Attribute("""Dictionary of all arguments for this build process""")

    # TODO: subscribers
    # TODO: arg checks

    @uthreads.uthreaded
    def run(ctxt, **kwargs):
        """Run the build; this method is overridden by users."""

    @uthreads.uthreaded
    def make_context(ctxt):
        """Make an L{IContext} object for a newly spawned build process, within
        the given project.  The default implementation calls L{make_history_name}."""

    def make_history_name(ctxt):
        # TODO uniqueness requirement?
        """Return a new name for a history element."""
