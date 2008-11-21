# -*- python -*-
# ex: set syntax=python:

import re
from buildbot.resources.schedulers.dummysched import DummyScheduler

#srcmgr = addSourceManager(
#    DirectorySourceManager(
#        name="dir",
#        directory="/tmp/BB",
#        isImportant = re.compile(r".*\.tar\.gz$").match,
#        interval=1,
#    ))


sched = addScheduler(
    DummyScheduler(
        name="buildit",
    ))

#sl = addSlave(
#    Slave(
#        name="worker",
#        password="hi",
#    ))
