import os
import shutil

from zope.interface import implements, providedBy
from twisted.internet import reactor, defer
from twisted.python import log
from buildbot.framework import process, interfaces
import uthreads

from test import mock, base

class Context(base.TestCase):
    @uthreads.returns_deferred
    def setUp(self):
        self.histmgr = mock.DummyHistoryManager()
        self.project = yield self.histmgr.getProject("lolcode2asm", True)

    @uthreads.returns_deferred
    def test_subcontext(self):
        ctxt = process.Context(self.project)
        assert interfaces.IContext.providedBy(ctxt), "ctxt provides IContext"
        self.assertEqual(ctxt.hist, self.project, "context has correct history")
        assert ctxt.parent is None, "context has no parent"

        subhist = yield self.project.newBuild("mips")
        sub = ctxt.subcontext(hist=subhist)
        assert interfaces.IContext.providedBy(sub), "subcontext provides IContext"
        self.assertEqual(sub.hist, subhist, "subcontext has correct history")
        assert sub.parent is ctxt, "subcontext has original context as parent"

class BuildProcess(base.TestCase):
    @uthreads.returns_deferred
    def setUp(self):
        self.histmgr = mock.DummyHistoryManager()
        self.project = yield self.histmgr.getProject("lolcode2asm", True)

    @uthreads.returns_deferred
    def test_factory(self):

        class MyBP(process.BuildProcess):
            @uthreads.uthreaded
            def run(self, ctxt, **kwargs):
                self.args_when_run = kwargs

        ctxt = process.Context(self.project)

        bf = MyBP
        # TODO: this doesn't work yet -- apparently classProvides does
        # not apply to subclasses??
        #assert interfaces.IBuildProcessFactory.providedBy(bf), \
        #    "class provides IBF (got %s)" % (list(providedBy(bf)),)

        bf = bf(arg1=1)
        assert interfaces.IBuildProcessFactory.providedBy(bf), \
            "instance provides IBF (got %s)" % (list(providedBy(bf)),)

        bf = bf(arg2=2)
        assert interfaces.IBuildProcessFactory.providedBy(bf), \
            "child instance provides IBF (got %s)" % (list(providedBy(bf)),)

        bf = bf.spawn(ctxt, arg1=11, arg3=3)
        assert interfaces.IBuildProcess.providedBy(bf), \
            "spawned instance provides IB (got %s)" % (list(providedBy(bf)),)
        assert not interfaces.IBuildProcessFactory.providedBy(bf), \
            "..and not IBF"

        # TODO: use subscription interface
        bf._uthread.join()
        self.assertEqual(bf.args_when_run, dict(arg1=11, arg2=2, arg3=3),
            "args are collected correctly")
