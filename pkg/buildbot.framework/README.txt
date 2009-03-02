Framework
=========

The buildbot framework is the central architecture, with support for remote
slaves, scheduling builds, recording build results, and so on.  By itself, it
is not particularly useful.  To make this module useful, you will also need,
at least, ``buildbot.resources.core``.
