# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

import netsa.json as json

class JsonTest(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(json.dumps({'c': 0, 'b': 0, 'a': 0}, sort_keys=True),
                         '{"a": 0, "b": 0, "c": 0}')

    def test_loads_1(self):
        self.assertEqual(json.loads('{"bar":["baz", null, 1.0, 2]}'),
                         {u'bar': [u'baz', None, 1.0, 2]})
