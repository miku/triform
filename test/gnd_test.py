# coding: utf-8

"""
Rudimentary Tests.
"""

import unittest
import luigi
import os
from triform.gnd import GNDExtract
from gluish.task import MockTask

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

class GNDTest(unittest.TestCase):
    """ Test some GND classes. """

    def test_gnd_extract(self):
        compressed = os.path.join(FIXTURES, 'gnddump.nt.gz')
        uncompressed = os.path.join(FIXTURES, 'gnddump.nt')
        mock = MockTask(fixture=compressed)

        task = GNDExtract()
        task.requires = lambda: mock
        luigi.build([task], local_scheduler=True)
        
        with task.output().open() as handle:
            with open(uncompressed) as fh:
                self.assertEquals(handle.read(), fh.read())
