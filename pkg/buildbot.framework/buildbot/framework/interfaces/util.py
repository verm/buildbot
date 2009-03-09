"""Interfaces for general utilities provided by the buildbot framework."""

from zope.interface import Interface, Attribute
import uthreads

class ISubscription(Interface):
    """
    A "thunk" representing a subscription to some event source;
    its only use is to cancel the subscription.
    """
    def cancel():
        """Cancel the subscription."""
