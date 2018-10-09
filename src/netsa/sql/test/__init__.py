# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

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
