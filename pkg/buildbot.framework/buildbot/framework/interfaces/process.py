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

