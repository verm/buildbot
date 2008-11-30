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

@newStep("say")
def say(context, what):
    print "SAY:", what

@newBuild("dostuff")
def dostuff(context):
    yield say(context, "hello")
    yield say(context, "cruel")
    yield say(context, "world")

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
