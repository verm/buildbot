"""
Testing stuff
"""

import os
import sys

from twisted.application import service, app
from twisted.internet import reactor

from buildbot.framework import master as master_mod

oneoh_base = os.path.dirname(__file__)
default_master_cfg = os.path.join(oneoh_base, "buildmaster_cfg.py")

# This ApplicationRunner is loosely based on that from twisted.application.app
class OneohRunner(app.ApplicationRunner):
    def preApplication(self):
        self.oldstdout = sys.stdout
        self.oldstderr = sys.stderr

    def postApplication(self):
        app.startApplication(self.application, False)
        self.startReactor(None, self.oldstdout, self.oldstderr)

    def run(self):
        self.preApplication()

        a = service.Application('buildmaster')
        m = master_mod.BuildMaster(oneoh_base, default_master_cfg)
        m.setServiceParent(a)
        self.application = a

        self.logger.start(self.application)

        self.postApplication()

        self.logger.stop()
    
def master():
    """
    Run a buildbot master.
    """
    
    config = app.ServerOptions()
    OneohRunner(config).run()
