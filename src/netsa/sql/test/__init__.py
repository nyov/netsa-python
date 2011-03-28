# Copyright 2008-2010 by Carnegie Mellon University

# @OPENSOURCE_HEADER_START@
# Use of the Network Situational Awareness Python support library and
# related source code is subject to the terms of the following licenses:
# 
# GNU Public License (GPL) Rights pursuant to Version 2, June 1991
# Government Purpose License Rights (GPLR) pursuant to DFARS 252.225-7013
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
import netsa.sql

class db_connect(unittest.TestCase):

    def test_bad_uri(self):
        """
        Check for the expected behavior when a database URI is
        unparsable.
        """
        def check():
            netsa.sql.db_connect("broken")
        self.assertRaises(netsa.sql.sql_invalid_uri_exception, check)

    def test_no_driver(self):
        """
        Check for the expected behavior when no driver is found for a
        URI scheme.
        """
        def check():
            netsa.sql.db_connect("no-such-scheme:stuff")
        self.assertRaises(netsa.sql.sql_no_driver_exception, check)

class db_query(unittest.TestCase):

    def setUp(self):
        self.test_query = netsa.sql.db_query(
            "select * from test%x where a = :a and b = :b and c = :a",
            x="select * from test where x = :a and b = :b and c = :a",
            y="select * from test where y = :a and b = :b",
            z="select * from test where z = :a")

    def test_base_sql(self):
        sql = self.test_query.get_variant_sql([])
        self.assertEqual(
            sql, "select * from test%x where a = :a and b = :b and c = :a")

    def test_base_variant_x(self):
        sql = self.test_query.get_variant_sql(['x'])
        self.assertEqual(
            sql, "select * from test where x = :a and b = :b and c = :a")
    
    def test_base_variant_yx(self):
        sql = self.test_query.get_variant_sql(['y', 'x'])
        self.assertEqual(
            sql, "select * from test where y = :a and b = :b")

    def test_base_variant_xyz(self):
        sql = self.test_query.get_variant_sql(['x', 'y', 'z'])
        self.assertEqual(
            sql, "select * from test where x = :a and b = :b and c = :a")

    def test_base_variant_zyx(self):
        sql = self.test_query.get_variant_sql(['z', 'y', 'x'])
        self.assertEqual(
            sql, "select * from test where z = :a")

    def test_base_variant_qrs(self):
        sql = self.test_query.get_variant_sql(['q', 'r', 's'])
        self.assertEqual(
            sql, "select * from test%x where a = :a and b = :b and c = :a")

    def test_base_variant_qxs(self):
        sql = self.test_query.get_variant_sql(['q', 'x', 's'])
        self.assertEqual(
            sql, "select * from test where x = :a and b = :b and c = :a")

    def test_qmark_sql(self):
        sql = self.test_query.get_variant_qmark_params(
            [], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test%x where a = ? and b = ? and c = ?",
                  [1, 2, 1]))

    def test_qmark_variant_zyx(self):
        sql = self.test_query.get_variant_qmark_params(
            ['z', 'y', 'x'], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test where z = ?", [1]))
    
    def test_numeric_sql(self):
        sql = self.test_query.get_variant_numeric_params(
                [], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test%x where a = :1 and b = :2 and c = :3",
                  [1, 2, 1]))

    def test_numeric_variant_zyx(self):
        sql = self.test_query.get_variant_numeric_params(
                ['z', 'y', 'x'], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test where z = :1", [1]))
    
    def test_named_sql(self):
        sql = self.test_query.get_variant_named_params(
                    [], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test%x where a = :a and b = :b and c = :a",
                  {'a': 1, 'b': 2, 'c': 3}))

    def test_named_variant_zyx(self):
        sql = self.test_query.get_variant_named_params(
                    ['z', 'y', 'x'], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test where z = :a",
                  {'a': 1, 'b': 2, 'c': 3}))

    def test_format_sql(self):
        sql = self.test_query.get_variant_format_params(
                    [], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test%%x where a = %s and b = %s and c = %s",
                  [1, 2, 1]))

    def test_format_variant_zyx(self):
        sql = self.test_query.get_variant_format_params(
                    ['z', 'y', 'x'], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test where z = %s", [1]))
    
    def test_pyformat_sql(self):
        sql = self.test_query.get_variant_pyformat_params(
                    [], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test%%x where a = %(a)s and b = %(b)s and "
                  "c = %(a)s", {'a': 1, 'b': 2, 'c': 3}))

    def test_pyformat_variant_zyx(self):
        sql = self.test_query.get_variant_pyformat_params(
                    ['z', 'y', 'x'], {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            sql, ("select * from test where z = %(a)s",
                  {'a': 1, 'b': 2, 'c': 3}))

__all__ = """

    db_connect
    db_query

""".split()
