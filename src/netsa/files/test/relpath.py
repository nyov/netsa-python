# Copyright 2011 by Carnegie Mellon University

# @OPENSOURCE_HEADER_START@
# Use of the Network Situational Awareness Python support library and
# related source code is subject to the terms of the following licenses:
# 
# GNU Public License (GPL) Rights pursuant to Version 2, June 1991
# Government Purpose License Rights (GPLR) pursuant to DFARS 252.227.7013
# 
# NO WARRANTY
# 
# ANY INFORMATION, MATERIALS, SERVICES, INTELLECTUAL PROPERTY OR OTHER 
# PROPERTY OR RIGHTS GRANTED OR PROVIDED BY CARNEGIE MELLON UNIVERSITY 
# PURSUANT TO THIS LICENSE (HEREINAFTER THE "DELIVERABLES") ARE ON AN 
# "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY 
# KIND, EITHER EXPRESS OR IMPLIED AS TO ANY MATTER INCLUDING, BUT NOT 
# LIMITED TO, WARRANTY OF FITNESS FOR A PARTICULAR PURPOSE, 
# MERCHANTABILITY, INFORMATIONAL CONTENT, NONINFRINGEMENT, OR ERROR-FREE 
# OPERATION. CARNEGIE MELLON UNIVERSITY SHALL NOT BE LIABLE FOR INDIRECT, 
# SPECIAL OR CONSEQUENTIAL DAMAGES, SUCH AS LOSS OF PROFITS OR INABILITY 
# TO USE SAID INTELLECTUAL PROPERTY, UNDER THIS LICENSE, REGARDLESS OF 
# WHETHER SUCH PARTY WAS AWARE OF THE POSSIBILITY OF SUCH DAMAGES. 
# LICENSEE AGREES THAT IT WILL NOT MAKE ANY WARRANTY ON BEHALF OF 
# CARNEGIE MELLON UNIVERSITY, EXPRESS OR IMPLIED, TO ANY PERSON 
# CONCERNING THE APPLICATION OF OR THE RESULTS TO BE OBTAINED WITH THE 
# DELIVERABLES UNDER THIS LICENSE.
# 
# Licensee hereby agrees to defend, indemnify, and hold harmless Carnegie 
# Mellon University, its trustees, officers, employees, and agents from 
# all claims or demands made against them (and any related losses, 
# expenses, or attorney's fees) arising out of, or relating to Licensee's 
# and/or its sub licensees' negligent use or willful misuse of or 
# negligent conduct or willful misconduct regarding the Software, 
# facilities, or other rights or assistance granted by Carnegie Mellon 
# University under this License, including, but not limited to, any 
# claims of product liability, personal injury, death, damage to 
# property, or violation of any laws or regulations.
# 
# Carnegie Mellon University Software Engineering Institute authored 
# documents are sponsored by the U.S. Department of Defense under 
# Contract FA8721-05-C-0003. Carnegie Mellon University retains 
# copyrights in all material produced under this contract. The U.S. 
# Government retains a non-exclusive, royalty-free license to publish or 
# reproduce these documents, or allow others to do so, for U.S. 
# Government purposes only pursuant to the copyright license under the 
# contract clause at 252.227.7013.
# @OPENSOURCE_HEADER_END@

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
