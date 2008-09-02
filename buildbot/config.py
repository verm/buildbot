"""
This is the central location for all symbols that are available in
buildbot configuration files.  The namespace of this module is copied
and supplied to the master configuration file when it is executed.

The following symbols will be added by the buildmaster when the config
is loaded:
 - basedir
 - buildmaster
 - addSlave
 - addSourceManager
 - addScheduler
"""

# Every user-visible class or function should be imported here.
