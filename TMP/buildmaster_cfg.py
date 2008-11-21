# -*- python -*-
# ex: set syntax=python:

import re
from buildbot import uthreads
from buildbot.resources.schedulers.dummysched import DummyScheduler

#srcmgr = addSourceManager(
#    DirectorySourceManager(
#        name="dir",
#        directory="/tmp/BB",
#        isImportant = re.compile(r".*\.tar\.gz$").match,
#        interval=1,
#    ))

def dostuff():
    print "hi"
    yield uthreads.sleep(1)
    print "hey"
    yield uthreads.sleep(1)
    print "yo"
    
sched = addScheduler(
    DummyScheduler(
        name="buildit",
        action=dostuff
    ))

#sl = addSlave(
#    Slave(
#        name="worker",
#        password="hi",
#    ))
