# coding: utf-8

"""
Rudimentary Tests.
"""

from gluish.path import unlink
from gluish.task import MockTask
from triform.gnd import GNDExtract, GNDSameAs
import luigi
import os
import tempfile
import unittest

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

class GNDExtractTest(GNDExtract):
    def requires(self):
        compressed = os.path.join(FIXTURES, 'gnddump.nt.gz')
        return MockTask(fixture=compressed)

    def output(self):
        return luigi.LocalTarget(path=self.path(digest=True))

class GNDSameAsTest(GNDSameAs):
    def requires(self):
        return MockTask(fixture=os.path.join(FIXTURES, 'sameas.nt'))

    def output(self):
        return luigi.LocalTarget(path=self.path(digest=True))

class GNDTest(unittest.TestCase):
    """ Test some GND classes. """

    @classmethod
    def setUpClass(cls):
        for task in (GNDExtractTest, GNDSameAs):
            unlink(task().requires().output().path)
            unlink(task().output().path)

    def test_gnd_extract(self):
        task = GNDExtractTest()
        luigi.build([task], local_scheduler=True)
        with task.output().open() as handle:
            with open(os.path.join(FIXTURES, 'gnddump.nt')) as fh:
                self.assertEquals(handle.read(), fh.read())

    def test_gnd_sameas(self):
        task = GNDSameAsTest()
        luigi.build([task], local_scheduler=True)
        with task.output().open() as handle:
            with open(os.path.join(FIXTURES, 'sameas.n3')) as fh:
                self.assertEquals(handle.read(), fh.read())
