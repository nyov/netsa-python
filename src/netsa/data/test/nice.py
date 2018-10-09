# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

from netsa.data.nice import *
from netsa.data.times import make_datetime

class NiceTest(unittest.TestCase):

    def test_nice_ticks_1(self):
        (a, b, i) = nice_ticks(1, 19)
        self.assertEqual(a, 0.0)
        self.assertEqual(b, 20.0)
        self.assertEqual(list(i), [0.0, 5.0, 10.0, 15.0, 20.0])

    def test_nice_ticks_2(self):
        (a, b, i) = nice_ticks(-9, 9)
        self.assertEqual(a, -10.0)
        self.assertEqual(b, 10.0)
        self.assertEqual(list(i), [-10.0, -5.0, 0.0, 5.0, 10.0])

    def test_nice_ticks_3(self):
        (a, b, i) = nice_ticks(1, 19, inside=True)
        self.assertEqual(a, 5.0)
        self.assertEqual(b, 15.0)
        self.assertEqual(list(i), [5.0, 10.0, 15.0])

    def test_nice_ticks_4(self):
        (a, b, i) = nice_ticks(-9, 9, inside=True)
        self.assertEqual(a, -5.0)
        self.assertEqual(b, 5.0)
        self.assertEqual(list(i), [-5.0, 0.0, 5.0])

    def test_nice_ticks_5(self):
        (a, b, i) = nice_ticks(1, 19, ticks=7)
        self.assertEqual(a, 0.0)
        self.assertEqual(b, 21.0)
        self.assertEqual(list(i), [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0])

    def test_nice_ticks_6(self):
        (a, b, i) = nice_ticks(-9, 9, ticks=7)
        self.assertEqual(a, -9.0)
        self.assertEqual(b, 9.0)
        self.assertEqual(list(i), [-9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0])

    def test_nice_ticks_7(self):
        (a, b, i) = nice_ticks(0, 0)
        self.assertEqual(a, -0.5)
        self.assertEqual(b, 0.5)
        self.assertEqual(list(i), [-0.5, -0.25, 0.0, 0.25, 0.5])

    def test_nice_ticks_8(self):
        (a, b, i) = nice_ticks(300, 300)
        self.assertEqual(a, 299.5)
        self.assertEqual(b, 300.5)
        self.assertEqual(list(i), [299.5, 299.75, 300.0, 300.25, 300.5])

    def test_nice_ticks_9(self):
        (a, b, i) = nice_ticks(1.2, 1.2)
        self.assertEqual(a, 1.0)
        self.assertEqual(b, 2.0)
        self.assertEqual(list(i), [1.0, 1.25, 1.5, 1.75, 2.0])

    def test_nice_ticks_10(self):
        (a, b, i) = nice_ticks(-1.2, -1.2)
        self.assertEqual(a, -2.0)
        self.assertEqual(b, -1.0)
        self.assertEqual(list(i), [-2.0, -1.75, -1.5, -1.25, -1.0])

    def test_nice_ticks_11(self):
        self.assertRaises(ValueError, nice_ticks, 10.0, 0.0)

    def test_nice_ticks_seq_1(self):
        self.assertEqual(list(nice_ticks_seq(1, 19)),
                         [0.0, 5.0, 10.0, 15.0, 20.0])

    def test_nice_ticks_seq_2(self):
        self.assertEqual(list(nice_ticks_seq(-9, 9)),
                         [-10.0, -5.0, 0.0, 5.0, 10.0])

    def test_nice_ticks_seq_3(self):
        self.assertEqual(list(nice_ticks_seq(1, 19, inside=True)),
                         [5.0, 10.0, 15.0])

    def test_nice_ticks_seq_4(self):
        self.assertEqual(list(nice_ticks_seq(-9, 9, inside=True)),
                         [-5.0, 0.0, 5.0])

    def test_nice_ticks_seq_5(self):
        self.assertEqual(list(nice_ticks_seq(1, 19, ticks=7)),
                         [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0])

    def test_nice_ticks_seq_6(self):
        self.assertEqual(list(nice_ticks_seq(-9, 9, ticks=7)),
                         [-9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0])

    def test_nice_ticks_seq_7(self):
        self.assertEqual(list(nice_ticks_seq(0, 0)),
                         [-0.5, -0.25, 0.0, 0.25, 0.5])

    def test_nice_ticks_seq_8(self):
        self.assertEqual(list(nice_ticks_seq(300, 300)),
                         [299.5, 299.75, 300.0, 300.25, 300.5])

    def test_nice_ticks_seq_9(self):
        self.assertEqual(list(nice_ticks_seq(1.2, 1.2)),
                         [1.0, 1.25, 1.5, 1.75, 2.0])

    def test_nice_ticks_seq_10(self):
        self.assertEqual(list(nice_ticks_seq(-1.2, -1.2)),
                         [-2.0, -1.75, -1.5, -1.25, -1.0])

    def test_nice_ticks_seq_11(self):
        self.assertRaises(ValueError, nice_ticks_seq, 10.0, 0.0)

    def test_nice_time_ticks_1(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-01-01'))
        self.assertEqual(a, make_datetime('2010-12-31T23:59:59.500'))
        self.assertEqual(b, make_datetime('2011-01-01T00:00:00.500'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2010-12-31T23:59:59.500',
                                    '2010-12-31T23:59:59.750',
                                    '2011-01-01T00:00:00.000',
                                    '2011-01-01T00:00:00.250',
                                    '2011-01-01T00:00:00.500']])

    def test_nice_time_ticks_2(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01T00:00:00.000'),
                                    make_datetime('2011-01-01T00:00:20.000'))
        self.assertEqual(a, make_datetime('2011-01-01T00:00:00.000'))
        self.assertEqual(b, make_datetime('2011-01-01T00:00:20.000'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00:00:00.000',
                                    '2011-01-01T00:00:05.000',
                                    '2011-01-01T00:00:10.000',
                                    '2011-01-01T00:00:15.000',
                                    '2011-01-01T00:00:20.000']])

    def test_nice_time_ticks_3(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01T00:00:00.000'),
                                    make_datetime('2011-01-01T00:00:30.000'))
        self.assertEqual(a, make_datetime('2011-01-01T00:00:00.000'))
        self.assertEqual(b, make_datetime('2011-01-01T00:00:30.000'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00:00:00.000',
                                    '2011-01-01T00:00:06.000',
                                    '2011-01-01T00:00:12.000',
                                    '2011-01-01T00:00:18.000',
                                    '2011-01-01T00:00:24.000',
                                    '2011-01-01T00:00:30.000']])

    def test_nice_time_ticks_4(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01T00:00:00.000'),
                                    make_datetime('2011-01-01T00:01:00.000'))
        self.assertEqual(a, make_datetime('2011-01-01T00:00:00.000'))
        self.assertEqual(b, make_datetime('2011-01-01T00:01:00.000'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00:00:00.000',
                                    '2011-01-01T00:00:15.000',
                                    '2011-01-01T00:00:30.000',
                                    '2011-01-01T00:00:45.000',
                                    '2011-01-01T00:01:00.000']])

    def test_nice_time_ticks_5(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01T00:00:00.000'),
                                    make_datetime('2011-01-01T00:10:00.000'))
        self.assertEqual(a, make_datetime('2011-01-01T00:00:00.000'))
        self.assertEqual(b, make_datetime('2011-01-01T00:10:00.000'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00:00:00.000',
                                    '2011-01-01T00:02:00.000',
                                    '2011-01-01T00:04:00.000',
                                    '2011-01-01T00:06:00.000',
                                    '2011-01-01T00:08:00.000',
                                    '2011-01-01T00:10:00.000']])

    def test_nice_time_ticks_6(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01T00:00:00.000'),
                                    make_datetime('2011-01-01T01:00:00.000'))
        self.assertEqual(a, make_datetime('2011-01-01T00:00:00.000'))
        self.assertEqual(b, make_datetime('2011-01-01T01:00:00.000'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00:00:00.000',
                                    '2011-01-01T00:15:00.000',
                                    '2011-01-01T00:30:00.000',
                                    '2011-01-01T00:45:00.000',
                                    '2011-01-01T01:00:00.000']])

    def test_nice_time_ticks_7(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01T00:00:00.000'),
                                    make_datetime('2011-01-01T14:00:00.000'))
        self.assertEqual(a, make_datetime('2011-01-01T00:00:00.000'))
        self.assertEqual(b, make_datetime('2011-01-01T15:00:00.000'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00:00:00.000',
                                    '2011-01-01T03:00:00.000',
                                    '2011-01-01T06:00:00.000',
                                    '2011-01-01T09:00:00.000',
                                    '2011-01-01T12:00:00.000',
                                    '2011-01-01T15:00:00.000']])

    def test_nice_time_ticks_8(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-01-02'))
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2011-01-02'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00', '2011-01-01T06',
                                    '2011-01-01T12', '2011-01-01T18',
                                    '2011-01-02T00']])

    def test_nice_time_ticks_9(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-01-03'))
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2011-01-03'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01T00', '2011-01-01T12',
                                    '2011-01-02T00', '2011-01-02T12',
                                    '2011-01-03T00']])

    def test_nice_time_ticks_10(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-01-14'))
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2011-01-16'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01', '2011-01-04', '2011-01-07',
                                    '2011-01-10', '2011-01-13', '2011-01-16']])

    def test_nice_time_ticks_11(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-01-14'))
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2011-01-16'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01', '2011-01-04', '2011-01-07',
                                    '2011-01-10', '2011-01-13', '2011-01-16']])

    def test_nice_time_ticks_12(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-02-24'))
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2011-03-02'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01', '2011-01-11', '2011-01-21',
                                    '2011-01-31', '2011-02-10', '2011-02-20',
                                    '2011-03-02']])

    def test_nice_time_ticks_13(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-05-07'))
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2011-06-01'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01', '2011-02-01', '2011-03-01',
                                    '2011-04-01', '2011-05-01', '2011-06-01']])

    def test_nice_time_ticks_14(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-12-31'), ticks=12)
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2012-01-01'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01', '2011-02-01', '2011-03-01',
                                    '2011-04-01', '2011-05-01', '2011-06-01',
                                    '2011-07-01', '2011-08-01', '2011-09-01',
                                    '2011-10-01', '2011-11-01', '2011-12-01',
                                    '2012-01-01']])

    def test_nice_time_ticks_15(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2011-12-01'), ticks=12)
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2011-12-01'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01', '2011-02-01', '2011-03-01',
                                    '2011-04-01', '2011-05-01', '2011-06-01',
                                    '2011-07-01', '2011-08-01', '2011-09-01',
                                    '2011-10-01', '2011-11-01', '2011-12-01']])

    def test_nice_time_ticks_16(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2013-01-01'))
        self.assertEqual(a, make_datetime('2011-01-01'))
        self.assertEqual(b, make_datetime('2013-01-01'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2011-01-01', '2011-07-01', '2012-01-01',
                                    '2012-07-01', '2013-01-01']])

    def test_nice_time_ticks_17(self):
        (a, b, i) = nice_time_ticks(make_datetime('2011-01-01'),
                                    make_datetime('2525-01-01'))
        self.assertEqual(a, make_datetime('2000-01-01'))
        self.assertEqual(b, make_datetime('2600-01-01'))
        self.assertEqual(list(i), [make_datetime(x) for x in
                                   ['2000-01-01', '2100-01-01', '2200-01-01',
                                    '2300-01-01', '2400-01-01', '2500-01-01',
                                    '2600-01-01']])
