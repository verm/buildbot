from zope.interface import implements
from twisted.python import log, components
from twisted.internet import defer, reactor
from buildbot.framework import interfaces
from buildbot import uthreads

##
# Useful decorators for process functions

def newBuild(buildName):
    """
    Decorate a build function to create a new IBuildHistory context when
    called.  Used like this::
      @newBuild("make-dist")
      def make_dist(context):
          # ...
    """
    def d(fn):
        def w(context, *args, **kwargs):
            context = context.newBuild(buildName)
            yield fn(context, *args, **kwargs)
        return w
    return d

def newStep(buildName):
    """
    Decorate a build function to create a new IStepHistory context when
    called.
    """
    def d(fn):
        def w(context, *args, **kwargs):
            context = context.newStep(buildName)
            yield fn(context, *args, **kwargs)
        return w
    return d

