# -*- python -*-
# ex: set syntax=python:

import re
from buildbot import uthreads
from buildbot.resources.schedulers.dummysched import DummyScheduler
from buildbot.resources.history.ramhistory import RamHistoryManager
from buildbot.framework.process import newStep, newBuild

# TODO: addHistoryManager

history = RamHistoryManager()
project = history.getProject("stuffproj", create=True)

#srcmgr = addSourceManager(
#    DirectorySourceManager(
#        name="dir",
#        directory="/tmp/BB",
#        isImportant = re.compile(r".*\.tar\.gz$").match,
#        interval=1,
#    ))

@newStep("say-hi")
def dosayhi(context):
    print "hi"

@newStep("say-hey")
def dosayhey(context):
    print "hey"

@newBuild("dostuff")
def dostuff(context):
    yield dosayhi(context)
    yield dosayhey(context)

    print "history:"
    yield print_histelt(project)

def print_histelt(elt, indent=0):
    s = yield elt.getHistoryEltIdPath()
    print "/" + ("/".join((yield elt.getHistoryEltIdPath()))), "(%r)" % (elt,)
    for kidName in (yield elt.getChildEltKeys()):
        yield print_histelt((yield elt.getChildElt(kidName)))
    
sched = addScheduler(
    DummyScheduler(
        name="buildit",
        context=project,
        action=dostuff
    ))

#sl = addSlave(
#    Slave(
#        name="worker",
#        password="hi",
#    ))
