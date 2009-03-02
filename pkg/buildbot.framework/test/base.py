import buildbot
from twisted.trial import unittest

class TestCase(unittest.TestCase):
    def tearDown(self):
        # delete any previous buildmaster object
        buildbot.buildmaster = None
