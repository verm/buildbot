"""
This is the central location for all symbols that are available in
buildbot configuration files.  The namespace of this module is copied
and supplied to the master configuration file when it is executed.

The following symbols will be added by the buildmaster when the config
is loaded:
 - masterdir
 - addSlave
 - addSourceManager
 - addScheduler
"""

# the top-level buildbot package is available here, mostly for the sake
# of buildbot.buildmaster

import buildbot

# Every user-visible class or function should be imported here.

from buildbot.framework.slaves import Slave
from buildbot.framework.process import buildStep, spawnsBuild
from buildbot.resources.history.ramhistory import RamHistoryManager
from buildbot.resources.schedulers.dummysched import DummyScheduler
