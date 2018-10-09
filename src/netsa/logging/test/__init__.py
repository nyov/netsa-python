# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

from netsa import logging
from netsa.files import get_temp_file_name

class LoggingTest(unittest.TestCase):

    def setUp(self):
        self.logfileName = get_temp_file_name()
        logging.setProgramName("tester")
        logging.setLogFilename(self.logfileName)
        logging.root.setLevel(logging.INFO)
        logging.basicConfig()

    def test_logging_1(self):
        f = open(self.logfileName, 'w')
        f.close()
        logging.warning("something is very very wrong: %r", "WRONG")
        f = open(self.logfileName, 'r')
        s = f.read()
        f.close()
        self.assertTrue('WRONG' in s)
