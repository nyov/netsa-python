# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

from datetime import datetime, timedelta

import netsa.data.times
from netsa.data.times import make_datetime, bin_datetime, make_timedelta

class TimesTest(unittest.TestCase):

    def setUp(self):
        self.dt_20100203 = datetime(
            2010, 2, 3, tzinfo=netsa.data.times.utc)
        self.dt_20100203T040000 = datetime(
            2010, 2, 3, 4, tzinfo=netsa.data.times.utc)
        self.dt_20100203T040500 = datetime(
            2010, 2, 3, 4, 5, tzinfo=netsa.data.times.utc)
        self.dt_20100203T040506 = datetime(
            2010, 2, 3, 4, 5, 6, tzinfo=netsa.data.times.utc)
        self.dt_20100203T040506_007 = datetime(
            2010, 2, 3, 4, 5, 6, 7000, tzinfo=netsa.data.times.utc)
        self.dt_20100203T040506_007008 = datetime(
            2010, 2, 3, 4, 5, 6, 7008, tzinfo=netsa.data.times.utc)
        self.dt_20100203T040506_007008_09 = datetime(
            2010, 2, 3, 4, 5, 6, 7008,
            tzinfo=netsa.data.times.tzinfo_fixed(9*60))
        self.dt_20100203T040506_007008_0910 = datetime(
            2010, 2, 3, 4, 5, 6, 7008,
            tzinfo=netsa.data.times.tzinfo_fixed(9*60+10))
        self.dt_20100203T040505 = datetime(
            2010, 2, 3, 4, 5, 5, tzinfo=netsa.data.times.utc)
        self.dt_20100203T030000 = datetime(
            2010, 2, 3, 3, 0, 0, tzinfo=netsa.data.times.utc)
        self.dt_20100128T000000 = datetime(
            2010, 1, 28, 0, 0, 0, tzinfo=netsa.data.times.utc)
        self.dt_20100129T000000 = datetime(
            2010, 1, 29, 0, 0, 0, tzinfo=netsa.data.times.utc)
        self.dt_20100201T000000 = datetime(
            2010, 2, 1, 0, 0, 0, tzinfo=netsa.data.times.utc)
        self.dt_20100101T000000 = datetime(
            2010, 1, 1, 0, 0, 0, tzinfo=netsa.data.times.utc)
    def test_make_datetime_int_epoch(self):
        "make_datetime(0)"
        self.assertEqual(
            netsa.data.times.DT_EPOCH,
            make_datetime(0))
    def test_make_datetime_int_20100203T040506(self):
        "make_datetime(1265169906)"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime(1265169906))
    def test_make_datetime_long_20100203T040506(self):
        "make_datetime(1265169906L)"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime(1265169906L))
    def test_make_datetime_iso_day(self):
        "make_datetime('2010-02-03')"
        self.assertEqual(
            self.dt_20100203,
            make_datetime('2010-02-03'))
    def test_make_datetime_iso_hour(self):
        "make_datetime('2010-02-03T04')"
        self.assertEqual(
            self.dt_20100203T040000,
            make_datetime('2010-02-03T04'))
    def test_make_datetime_iso_minute(self):
        "make_datetime('2010-02-03T04:05')"
        self.assertEqual(
            self.dt_20100203T040500,
            make_datetime('2010-02-03T04:05'))
    def test_make_datetime_iso_second(self):
        "make_datetime('2010-02-03T04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('2010-02-03T04:05:06'))
    def test_make_datetime_iso_second_space(self):
        "make_datetime('2010-02-03 04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('2010-02-03 04:05:06'))
    def test_make_datetime_iso_msec(self):
        "make_datetime('2010-02-03T04:05:06.007')"
        self.assertEqual(
            self.dt_20100203T040506_007,
            make_datetime('2010-02-03T04:05:06.007'))
    def test_make_datetime_iso_usec(self):
        "make_datetime('2010-02-03T04:05:06.007008')"
        self.assertEqual(
            self.dt_20100203T040506_007008,
            make_datetime('2010-02-03T04:05:06.007008'))
    def test_make_datetime_iso_usec_tzhour(self):
        "make_datetime('2010-02-03T04:05:06.007008+09')"
        self.assertEqual(
            self.dt_20100203T040506_007008_09,
            make_datetime('2010-02-03T04:05:06.007008+09'))
    def test_make_datetime_iso_usec_tzminute(self):
        "make_datetime('2010-02-03T04:05:06.007008+09:10')"
        self.assertEqual(
            self.dt_20100203T040506_007008_0910,
            make_datetime('2010-02-03T04:05:06.007008+09:10'))
    def test_make_datetime_silk_day(self):
        "make_datetime('2010/02/03')"
        self.assertEqual(
            self.dt_20100203,
            make_datetime('2010/02/03'))
    def test_make_datetime_silk_hour(self):
        "make_datetime('2010/02/03T04')"
        self.assertEqual(
            self.dt_20100203T040000,
            make_datetime('2010/02/03T04'))
    def test_make_datetime_silk_minute(self):
        "make_datetime('2010/02/03T04:05')"
        self.assertEqual(
            self.dt_20100203T040500,
            make_datetime('2010/02/03T04:05'))
    def test_make_datetime_silk_second(self):
        "make_datetime('2010/02/03T04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('2010/02/03T04:05:06'))
    def test_make_datetime_silk_second_space(self):
        "make_datetime('2010/02/03 04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('2010/02/03 04:05:06'))
    def test_make_datetime_silk_second_colon(self):
        "make_datetime('2010/02/03:04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('2010/02/03:04:05:06'))
    def test_make_datetime_silk_msec(self):
        "make_datetime('2010/02/03:T04:05:06.007')"
        self.assertEqual(
            self.dt_20100203T040506_007,
            make_datetime('2010/02/03T04:05:06.007'))
    def test_make_datetime_silk_old_day(self):
        "make_datetime('02/03/2010')"
        self.assertEqual(
            self.dt_20100203,
            make_datetime('02/03/2010'))
    def test_make_datetime_silk_old_hour(self):
        "make_datetime('02/03/2010:04')"
        self.assertEqual(
            self.dt_20100203T040000,
            make_datetime('02/03/2010:04'))
    def test_make_datetime_silk_old_minute(self):
        "make_datetime('02/03/2010:04:05')"
        self.assertEqual(
            self.dt_20100203T040500,
            make_datetime('02/03/2010:04:05'))
    def test_make_datetime_silk_old_second_T(self):
        "make_datetime('02/03/2010T04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('02/03/2010T04:05:06'))
    def test_make_datetime_silk_old_second_space(self):
        "make_datetime('02/03/2010 04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('02/03/2010 04:05:06'))
    def test_make_datetime_silk_old_second(self):
        "make_datetime('02/03/2010:04:05:06')"
        self.assertEqual(
            self.dt_20100203T040506,
            make_datetime('02/03/2010:04:05:06'))
    def test_make_datetime_silk_old_msec(self):
        "make_datetime('02/03/2010:04:05:06.007')"
        self.assertEqual(
            self.dt_20100203T040506_007,
            make_datetime('02/03/2010:04:05:06.007'))
    def test_make_datetime_mxDateTime(self):
        "make_datetime(mx.DateTime.DateTime(2010, 2, 3, 4, 5, 6))"
        if netsa.data.times.mxDateTime_support:
            from mx import DateTime
            self.assertEqual(
                self.dt_20100203T040506,
                DateTime.DateTime(2010, 2, 3, 4, 5, 6))
    def test_bin_datetime_1_seconds(self):
        "bin_datetime(timedelta(seconds=1), ...)"
        self.assertEqual(
            bin_datetime(timedelta(seconds=1),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T040506)
    def test_bin_datetime_5_seconds(self):
        "bin_datetime(timedelta(seconds=5), ...)"
        self.assertEqual(
            bin_datetime(timedelta(seconds=5),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T040505)
    def test_bin_datetime_30_seconds(self):
        "bin_datetime(timedelta(seconds=30), ...)"
        self.assertEqual(
            bin_datetime(timedelta(seconds=30),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T040500)
    def test_bin_datetime_1_minutes(self):
        "bin_datetime(timedelta(minutes=1), ...)"
        self.assertEqual(
            bin_datetime(timedelta(minutes=1),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T040500)
    def test_bin_datetime_5_minutes(self):
        "bin_datetime(timedelta(minutes=5), ...)"
        self.assertEqual(
            bin_datetime(timedelta(minutes=5),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T040500)
    def test_bin_datetime_30_minutes(self):
        "bin_datetime(timedelta(minutes=30), ...)"
        self.assertEqual(
            bin_datetime(timedelta(minutes=30),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T040000)
    def test_bin_datetime_1_hours(self):
        "bin_datetime(timedelta(hours=1), ...)"
        self.assertEqual(
            bin_datetime(timedelta(hours=1),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T040000)
    def test_bin_datetime_3_hours(self):
        "bin_datetime(timedelta(hours=3), ...)"
        self.assertEqual(
            bin_datetime(timedelta(hours=3),
                         self.dt_20100203T040506_007008),
            self.dt_20100203T030000)
    def test_bin_datetime_1_days(self):
        "bin_datetime(timedelta(days=1), ...)"
        self.assertEqual(
            bin_datetime(timedelta(days=1),
                         self.dt_20100203T040506_007008),
            self.dt_20100203)
    def test_bin_datetime_7_days(self):
        "bin_datetime(timedelta(days=1), ...)"
        self.assertEqual(
            bin_datetime(timedelta(days=7),
                         self.dt_20100203T040506_007008),
            self.dt_20100128T000000)
    def test_bin_datetime_7_days_alt_z(self):
        "bin_datetime(timedelta(days=1), ..., z=DT_EPOCH+timedelta(days=1))"
        self.assertEqual(
            bin_datetime(timedelta(days=7),
                         self.dt_20100203T040506_007008,
                         z=netsa.data.times.DT_EPOCH+timedelta(days=1)),
            self.dt_20100129T000000)
    def test_bin_datetime_month(self):
        "bin_datetime('month', ...)",
        self.assertEqual(
            bin_datetime("month",
                         self.dt_20100203T040506_007008),
            self.dt_20100201T000000)
    def test_bin_datetime_year(self):
        "bin_datetime('year', ...)",
        self.assertEqual(
            bin_datetime("year",
                         self.dt_20100203T040506_007008),
            self.dt_20100101T000000)

    def test_make_timedelta_1(self):
        self.assertEqual(make_timedelta(timedelta(0)), timedelta(0))

    def test_make_timedelta_2(self):
        self.assertEqual(make_timedelta(timedelta(2427)), timedelta(2427))

    def test_make_timedelta_3(self):
        self.assertEqual(make_timedelta('P1Y'), timedelta(days=365))

    def test_make_timedelta_4(self):
        self.assertEqual(make_timedelta('P1M'), timedelta(days=30))

    def test_make_timedelta_5(self):
        self.assertEqual(make_timedelta('P1D'), timedelta(days=1))

    def test_make_timedelta_6(self):
        self.assertEqual(make_timedelta('PT1H'), timedelta(hours=1))

    def test_make_timedelta_7(self):
        self.assertEqual(make_timedelta('PT1M'), timedelta(minutes=1))

    def test_make_timedelta_8(self):
        self.assertEqual(make_timedelta('PT1S'), timedelta(seconds=1))

    def test_make_timedelta_9(self):
        self.assertEqual(make_timedelta('PT0.001S'), timedelta(milliseconds=1))

    def test_make_timedelta_10(self):
        self.assertEqual(
            make_timedelta('P1Y1M1DT1H1M1.001S'),
            timedelta(days=396, hours=1, minutes=1, seconds=1, milliseconds=1))
