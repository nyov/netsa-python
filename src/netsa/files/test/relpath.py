# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

from netsa.files import relpath, is_relpath

class RelPathTest(unittest.TestCase):

    def test_relpath_1(self):
        rp = relpath("/asd/brf/cqe", "/asd/qzc/rvg/tol")
        self.assertEqual(rp, "../../../brf/cqe")

    def test_relpath_2(self):
        rp = relpath("/asd/brf/cqe/tol", "/asd/brf")
        self.assertEqual(rp, "cqe/tol")

    def test_relpath_3(self):
        rp = relpath("foo/bar/baz", "/asd/brf")
        self.assertEqual(rp, "foo/bar/baz")

    def test_relpath_4(self):
        rp = relpath("/etc/foobar", "/")
        self.assertEqual(rp, "etc/foobar")

    def test_relpath_5(self):
        rp = relpath("/", "/")
        self.assertEqual(rp, ".")

    def test_relpath_6(self):
        rp = relpath("/foo/bar/baz", "/foo/bar/baz")
        self.assertEqual(rp, ".")

    def test_relpath_7(self):
        rp = relpath("/foo/bar/", "/foo/baz/")
        self.assertEqual(rp, "../bar")

    def test_is_relpath_1(self):
        self.assertTrue(is_relpath("/foo/bar/baz/qux", "/foo/bar/baz"))

    def test_is_relpath_2(self):
        self.assertTrue(is_relpath("/foo/bar/baz/../../../qux", "/foo/bar/baz"))

    def test_is_relpath_3(self):
        self.assertTrue(is_relpath("/foo/bar/baz", "/"))

    def test_is_relpath_4(self):
        self.assertTrue(is_relpath("/", "/"))

    def test_is_relpath_5(self):
        self.assertFalse(is_relpath("/foo/bar/qux/baz", "/foo/bar/baz"))
