# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

import os

from netsa.files import (acquire_pidfile_lock, examine_pidfile_lock,
                         release_pidfile_lock, get_temp_file_name)

class PidLockTest(unittest.TestCase):

    def test_pidfile_lock_1(self):
        lock_name = get_temp_file_name("test-1.pid")
        result = examine_pidfile_lock(lock_name)
        self.assertEqual(result, None)

    def test_pidfile_lock_2(self):
        lock_name = get_temp_file_name("test-2.pid")
        self.assertTrue(acquire_pidfile_lock(lock_name))
        result = examine_pidfile_lock(lock_name)
        self.assertFalse(result is None)
        (current_pid, is_running) = result
        self.assertEqual(is_running, True)
        self.assertEqual(current_pid, os.getpid())
        release_pidfile_lock(lock_name)
        result = examine_pidfile_lock(lock_name)
        self.assertEqual(result, None)
