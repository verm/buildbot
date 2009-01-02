# -*- python -*-
# ex: set syntax=python:

import re
from buildbot import uthreads
from buildbot.resources.schedulers.dummysched import DummyScheduler
from buildbot.resources.history.ramhistory import RamHistoryManager

# create a history manager to store build history
history = addHistoryManager(
    RamHistoryManager()
    )

# and a project
project = history.getProject("stuffproj", create=True)

#srcmgr = addSourceManager(
#    DirectorySourceManager(
#        name="dir",
#        directory="/tmp/BB",
#        isImportant = re.compile(r".*\.tar\.gz$").match,
#        interval=1,
#    ))

@buildStep("say")
def say(ctxt, what):
    print "SAY:", what

@buildStep("complex_say")
def complex_say(ctxt, what):
    print "preparing.."
    yield say(ctxt, what)
    yield say(ctxt, what + "!!")
    print "cleaning up.."

@spawnsBuild("dostuff")
def dostuff(ctxt):
    yield say(ctxt, "hello")
    yield complex_say(ctxt, "cruel")
    yield say(ctxt, "world")

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
        project=project,
        action=dostuff
    ))

#sl = addSlave(
#    Slave(
#        name="worker",
#        password="hi",
#    ))
