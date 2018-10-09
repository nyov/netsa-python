# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

import os
import stat

from netsa.files import get_temp_file_name, get_temp_file, get_temp_pipe_name

def _is_fifo(f):
    return stat.S_ISFIFO(stat.S_IFMT(os.stat(f)[stat.ST_MODE]))

class TempTest(unittest.TestCase):

    def test_get_temp_file_name_1(self):
        filename = get_temp_file_name()
        dirname = os.path.dirname(filename)
        self.assertTrue(os.path.isdir(dirname))
        self.assertFalse(os.path.exists(filename))

    def test_get_temp_file_name_2(self):
        filename = get_temp_file_name("test-a.txt")
        self.assertEqual(os.path.basename(filename), "test-a.txt")

    def test_get_temp_file_1(self):
        f1 = get_temp_file("test-b.txt", "w")
        self.assertEqual(os.path.basename(f1.name), "test-b.txt")
        f1.write("test content")
        f1.close()
        f2 = get_temp_file("test-b.txt", "r")
        self.assertEqual(os.path.basename(f2.name), "test-b.txt")
        text = f2.read()
        f2.close()
        self.assertEqual(text, "test content")

    def test_get_temp_pipe_name_1(self):
        filename = get_temp_pipe_name()
        self.assertTrue(_is_fifo(filename))

    def test_get_temp_pipe_name_2(self):
        filename = get_temp_pipe_name("test-c.fifo")
        self.assertEqual(os.path.basename(filename), "test-c.fifo")
        self.assertTrue(_is_fifo(filename))
