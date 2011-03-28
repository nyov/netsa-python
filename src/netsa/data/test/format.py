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

import netsa.data.format
from netsa.data.format import *
from datetime import datetime, timedelta

def td_test(s, *args, **kwargs):
    args_str = ", ".join(["%r" % a for a in args] +
                         ["%s=%r" % (k, v) for (k, v) in kwargs.iteritems()])
    def test_generated(self):
        self.assertEqual(s, timedelta_iso(timedelta(*args, **kwargs)))
    test_generated.__doc__ = "timedelta_iso(timedelta(%s))" % args_str
    return test_generated

class FormatTest(unittest.TestCase):

    def setUp(self):
        self.dt_20100203T040506_007008 = datetime(
            2010, 2, 3, 4, 5, 6, 7008, tzinfo=netsa.data.times.utc)
        self.dt_20100203T040506_007008_0910 = datetime(
            2010, 2, 3, 4, 5, 6, 7008,
            tzinfo=netsa.data.times.tzinfo_fixed(9*60+10))

    def test_num_fixed(self):
        "num_fixed(1234)"
        self.assertEqual('1234.00', num_fixed(1234))
    def test_num_fixed_unit(self):
        "num_fixed(1234, 'm')"
        self.assertEqual('1234.00m', num_fixed(1234, 'm'))
    def test_num_fixed_unit_dec_fig_4(self):
        "num_fixed(1234, 'm', dec_fig=4)"
        self.assertEqual('1234.0000m', num_fixed(1234, 'm', dec_fig=4))
    def test_num_fixed_unit_dec_fig_0(self):
        "num_fixed(1234.5678, 'm', dec_fig=0)"
        self.assertEqual('1235m', num_fixed(1234.5678, 'm', dec_fig=0))
    def test_num_fixed_dec_fig_3_thou_comma(self):
        "num_fixed(123456789, dec_fig=3, thousands_sep=',')"
        self.assertEqual('123,456,789.000',
                         num_fixed(123456789, dec_fig=3, thousands_sep=","))
    def test_num_fixed_dec_fig_6_thou_comma(self):
        "num_fixed(123456789, dec_fig=6, thousands_sep=',')"
        self.assertEqual('123,456,789.000000',
                         num_fixed(123456789, dec_fig=6, thousands_sep=","))

    def test_num_exponent(self):
        "num_exponent(1234)"
        self.assertEqual('1.23e+3', num_exponent(1234))
    def test_num_exponent_unit(self):
        "num_exponent(1234, 'm')"
        self.assertEqual('1.23e+3m', num_exponent(1234, 'm'))
    def test_num_exponent_unit_sig_fig_4(self):
        "num_exponent(1234, 'm', sig_fig=4)"
        self.assertEqual('1.234e+3m', num_exponent(1234, 'm', sig_fig=4))
    def test_num_exponent_unit_sig_fig_6(self):
        "num_exponent(1234.5678, 'm', sig_fig=6)"
        self.assertEqual('1.23457e+3m', num_exponent(1234.5678, 'm', sig_fig=6))
    def test_num_exponent_sig_fig_2(self):
        "num_exponent(123456789, sig_fig=2)"
        self.assertEqual('1.2e+8', num_exponent(123456789, sig_fig=2))
    def test_num_exponent_sig_fig_6(self):
        "num_exponent(123456, sig_fig=6)"
        self.assertEqual('1.23456e+5', num_exponent(123456, sig_fig=6))
    def test_num_exponent_sig_fig_1(self):
        "num_exponent(123456, sig_fig=1)"
        self.assertEqual('1e+5', num_exponent(123456, sig_fig=1))
    def test_num_exponent_sig_fig_0(self):
        "num_exponent(123456, sig_fig=0)"
        self.assertEqual('0e+6', num_exponent(123456, sig_fig=0))

    def test_num_prefix(self):
        "num_prefix(1024)"
        self.assertEqual('1.02k', num_prefix(1024))
    def test_num_prefix_unit(self):
        "num_prefix(1024, 'b')"
        self.assertEqual('1.02kb', num_prefix(1024, 'b'))
    def test_num_prefix_unit_bin(self):
        "num_prefix(1024, 'b', use_binary=True)"
        self.assertEqual('1.00Kib', num_prefix(1024, 'b', use_binary=True))
    def test_num_prefix_unit_sig_fig_2(self):
        "num_prefix(12345, 'b', sig_fig=2)"
        self.assertEqual('12kb', num_prefix(12345, 'b', sig_fig=2))
    def test_num_prefix_unit_sig_fig_7(self):
        "num_prefix(12345, 'b', sig_fig=7)"
        self.assertEqual('12345.00b', num_prefix(12345, 'b', sig_fig=7))
    def test_num_prefix_unit_big(self):
        "num_prefix(12345678901234567890, 'b')"
        self.assertEqual('12.3Eb', num_prefix(12345678901234567890, 'b'))
    def test_num_prefix_unit_big_sig_fig_7(self):
        "num_prefix(12345678901234567890, 'b', sig_fig=7)"
        self.assertEqual('12345.68Pb',
                         num_prefix(12345678901234567890, 'b', sig_fig=7))
    def test_num_prefix_unit_bigger(self):
        "num_prefix(1234567890123456789012345, 's')"
        self.assertEqual('1.23e+24s',
                         num_prefix(1234567890123456789012345, 's'))
    def test_num_prefix_unit_small(self):
        "num_prefix(0.001, 's')"
        self.assertEqual('1.00ms',
                         num_prefix(0.001, 's'))
    def test_num_prefix_unit_small_bin(self):
        "num_prefix(0.001, 's', use_binary=True)"
        self.assertEqual('1.00ms',
                         num_prefix(0.001, 's'))

    def test_datetime_silk(self):
        "datetime_silk(t)"
        self.assertEqual('2010/02/03T04:05:06',
                         datetime_silk(self.dt_20100203T040506_007008))
    def test_datetime_silk_prec_year(self):
        "datetime_silk(t, precision=DATETIME_YEAR)"
        self.assertEqual('2010',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_YEAR))
    def test_datetime_silk_prec_month(self):
        "datetime_silk(t, precision=DATETIME_MONTH)"
        self.assertEqual('2010/02',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_MONTH))
    def test_datetime_silk_prec_day(self):
        "datetime_silk(t, precision=DATETIME_DAY)"
        self.assertEqual('2010/02/03',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_DAY))
    def test_datetime_silk_prec_hour(self):
        "datetime_silk(t, precision=DATETIME_HOUR)"
        self.assertEqual('2010/02/03T04',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_HOUR))
    def test_datetime_silk_prec_minute(self):
        "datetime_silk(t, precision=DATETIME_MINUTE)"
        self.assertEqual('2010/02/03T04:05',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_MINUTE))
    def test_datetime_silk_prec_second(self):
        "datetime_silk(t, precision=DATETIME_SECOND)"
        self.assertEqual('2010/02/03T04:05:06',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_SECOND))
    def test_datetime_silk_prec_msec(self):
        "datetime_silk(t, precision=DATETIME_MSEC)"
        self.assertEqual('2010/02/03T04:05:06.007',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_MSEC))
    def test_datetime_silk_prec_usec(self):
        "datetime_silk(t, precision=DATETIME_USEC)"
        self.assertEqual('2010/02/03T04:05:06.007000',
                         datetime_silk(self.dt_20100203T040506_007008,
                                       precision=DATETIME_USEC))
    def test_datetime_silk_day(self):
        "datetime_silk_day(t)"
        self.assertEqual('2010/02/03',
                         datetime_silk_day(self.dt_20100203T040506_007008))
    def test_datetime_silk_hour(self):
        "datetime_silk_hour(t)"
        self.assertEqual('2010/02/03T04',
                         datetime_silk_hour(self.dt_20100203T040506_007008))

    def test_datetime_iso(self):
        "datetime_iso(t)"
        self.assertEqual('2010-02-03T04:05:06',
                         datetime_iso(self.dt_20100203T040506_007008))
    def test_datetime_iso_prec_year(self):
        "datetime_iso(t, precision=DATETIME_YEAR)"
        self.assertEqual('2010',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_YEAR))
    def test_datetime_iso_prec_month(self):
        "datetime_iso(t, precision=DATETIME_MONTH)"
        self.assertEqual('2010-02',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_MONTH))
    def test_datetime_iso_prec_day(self):
        "datetime_iso(t, precision=DATETIME_DAY)"
        self.assertEqual('2010-02-03',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_DAY))
    def test_datetime_iso_prec_hour(self):
        "datetime_iso(t, precision=DATETIME_HOUR)"
        self.assertEqual('2010-02-03T04',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_HOUR))
    def test_datetime_iso_prec_minute(self):
        "datetime_iso(t, precision=DATETIME_MINUTE)"
        self.assertEqual('2010-02-03T04:05',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_MINUTE))
    def test_datetime_iso_prec_second(self):
        "datetime_iso(t, precision=DATETIME_SECOND)"
        self.assertEqual('2010-02-03T04:05:06',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_SECOND))
    def test_datetime_iso_prec_msec(self):
        "datetime_iso(t, precision=DATETIME_MSEC)"
        self.assertEqual('2010-02-03T04:05:06.007',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_MSEC))
    def test_datetime_iso_prec_usec(self):
        "datetime_iso(t, precision=DATETIME_USEC)"
        self.assertEqual('2010-02-03T04:05:06.007008',
                         datetime_iso(self.dt_20100203T040506_007008,
                                      precision=DATETIME_USEC))
    def test_datetime_iso_tz(self):
        "datetime_iso(t_with_tz)"
        self.assertEqual('2010-02-03T04:05:06+09:10',
                         datetime_iso(self.dt_20100203T040506_007008_0910))
    def test_datetime_iso_day(self):
        "datetime_iso_day(t)"
        self.assertEqual('2010-02-03',
                         datetime_iso_day(self.dt_20100203T040506_007008))

    def test_datetime_iso_basic(self):
        "datetime_iso_basic(t)"
        self.assertEqual('20100203T040506',
                         datetime_iso_basic(self.dt_20100203T040506_007008))
    def test_datetime_iso_basic_prec_year(self):
        "datetime_iso_basic(t, precision=DATETIME_YEAR)"
        self.assertEqual('2010',
                         datetime_iso_basic(self.dt_20100203T040506_007008,
                                            precision=DATETIME_YEAR))
    def test_datetime_iso_basic_prec_month(self):
        "datetime_iso_basic(t, precision=DATETIME_MONTH)"
        self.assertRaises(ValueError, datetime_iso_basic,
                          self.dt_20100203T040506_007008,
                          precision=DATETIME_MONTH)
    def test_datetime_iso_basic_prec_day(self):
        "datetime_iso_basic(t, precision=DATETIME_DAY)"
        self.assertEqual('20100203',
                         datetime_iso_basic(self.dt_20100203T040506_007008,
                                            precision=DATETIME_DAY))
    def test_datetime_iso_basic_prec_hour(self):
        "datetime_iso_basic(t, precision=DATETIME_HOUR)"
        self.assertEqual('20100203T04',
                         datetime_iso_basic(self.dt_20100203T040506_007008,
                                            precision=DATETIME_HOUR))
    def test_datetime_iso_basic_prec_minute(self):
        "datetime_iso_basic(t, precision=DATETIME_MINUTE)"
        self.assertEqual('20100203T0405',
                         datetime_iso_basic(self.dt_20100203T040506_007008,
                                            precision=DATETIME_MINUTE))
    def test_datetime_iso_basic_prec_second(self):
        "datetime_iso_basic(t, precision=DATETIME_SECOND)"
        self.assertEqual('20100203T040506',
                         datetime_iso_basic(self.dt_20100203T040506_007008,
                                            precision=DATETIME_SECOND))
    def test_datetime_iso_basic_prec_msec(self):
        "datetime_iso_basic(t, precision=DATETIME_MSEC)"
        self.assertEqual('20100203T040506.007',
                         datetime_iso_basic(self.dt_20100203T040506_007008,
                                            precision=DATETIME_MSEC))
    def test_datetime_iso_basic_prec_usec(self):
        "datetime_iso_basic(t, precision=DATETIME_USEC)"
        self.assertEqual('20100203T040506.007008',
                         datetime_iso_basic(self.dt_20100203T040506_007008,
                                            precision=DATETIME_USEC))
    def test_datetime_iso_basic_tz(self):
        "datetime_iso_basic(t_with_tz)"
        self.assertEqual(
            '20100203T040506+0910',
            datetime_iso_basic(self.dt_20100203T040506_007008_0910))

    test_timedelta_iso_00 = td_test("P0D",                       0,0,0,0,0,0,0)
    test_timedelta_iso_01 = td_test("P7D",                       0,0,0,0,0,0,1)
    test_timedelta_iso_02 = td_test("PT1H",                      0,0,0,0,0,1,0)
    test_timedelta_iso_03 = td_test("P7DT1H",                    0,0,0,0,0,1,1)
    test_timedelta_iso_04 = td_test("PT1M",                      0,0,0,0,1,0,0)
    test_timedelta_iso_05 = td_test("P7DT1M",                    0,0,0,0,1,0,1)
    test_timedelta_iso_06 = td_test("PT1H1M",                    0,0,0,0,1,1,0)
    test_timedelta_iso_07 = td_test("P7DT1H1M",                  0,0,0,0,1,1,1)
    test_timedelta_iso_08 = td_test("PT0.001000S",               0,0,0,1,0,0,0)
    test_timedelta_iso_09 = td_test("P7DT0.001000S",             0,0,0,1,0,0,1)
    test_timedelta_iso_0A = td_test("PT1H0.001000S",             0,0,0,1,0,1,0)
    test_timedelta_iso_0B = td_test("P7DT1H0.001000S",           0,0,0,1,0,1,1)
    test_timedelta_iso_0C = td_test("PT1M0.001000S",             0,0,0,1,1,0,0)
    test_timedelta_iso_0D = td_test("P7DT1M0.001000S",           0,0,0,1,1,0,1)
    test_timedelta_iso_0E = td_test("PT1H1M0.001000S",           0,0,0,1,1,1,0)
    test_timedelta_iso_0F = td_test("P7DT1H1M0.001000S",         0,0,0,1,1,1,1)
    test_timedelta_iso_10 = td_test("PT0.000001S",               0,0,1,0,0,0,0)
    test_timedelta_iso_11 = td_test("P7DT0.000001S",             0,0,1,0,0,0,1)
    test_timedelta_iso_12 = td_test("PT1H0.000001S",             0,0,1,0,0,1,0)
    test_timedelta_iso_13 = td_test("P7DT1H0.000001S",           0,0,1,0,0,1,1)
    test_timedelta_iso_14 = td_test("PT1M0.000001S",             0,0,1,0,1,0,0)
    test_timedelta_iso_15 = td_test("P7DT1M0.000001S",           0,0,1,0,1,0,1)
    test_timedelta_iso_16 = td_test("PT1H1M0.000001S",           0,0,1,0,1,1,0)
    test_timedelta_iso_17 = td_test("P7DT1H1M0.000001S",         0,0,1,0,1,1,1)
    test_timedelta_iso_18 = td_test("PT0.001001S",               0,0,1,1,0,0,0)
    test_timedelta_iso_19 = td_test("P7DT0.001001S",             0,0,1,1,0,0,1)
    test_timedelta_iso_1A = td_test("PT1H0.001001S",             0,0,1,1,0,1,0)
    test_timedelta_iso_1B = td_test("P7DT1H0.001001S",           0,0,1,1,0,1,1)
    test_timedelta_iso_1C = td_test("PT1M0.001001S",             0,0,1,1,1,0,0)
    test_timedelta_iso_1D = td_test("P7DT1M0.001001S",           0,0,1,1,1,0,1)
    test_timedelta_iso_1E = td_test("PT1H1M0.001001S",           0,0,1,1,1,1,0)
    test_timedelta_iso_1F = td_test("P7DT1H1M0.001001S",         0,0,1,1,1,1,1)
    test_timedelta_iso_20 = td_test("PT1S",                      0,1,0,0,0,0,0)
    test_timedelta_iso_21 = td_test("P7DT1S",                    0,1,0,0,0,0,1)
    test_timedelta_iso_22 = td_test("PT1H1S",                    0,1,0,0,0,1,0)
    test_timedelta_iso_23 = td_test("P7DT1H1S",                  0,1,0,0,0,1,1)
    test_timedelta_iso_24 = td_test("PT1M1S",                    0,1,0,0,1,0,0)
    test_timedelta_iso_25 = td_test("P7DT1M1S",                  0,1,0,0,1,0,1)
    test_timedelta_iso_26 = td_test("PT1H1M1S",                  0,1,0,0,1,1,0)
    test_timedelta_iso_27 = td_test("P7DT1H1M1S",                0,1,0,0,1,1,1)
    test_timedelta_iso_28 = td_test("PT1.001000S",               0,1,0,1,0,0,0)
    test_timedelta_iso_29 = td_test("P7DT1.001000S",             0,1,0,1,0,0,1)
    test_timedelta_iso_2A = td_test("PT1H1.001000S",             0,1,0,1,0,1,0)
    test_timedelta_iso_2B = td_test("P7DT1H1.001000S",           0,1,0,1,0,1,1)
    test_timedelta_iso_2C = td_test("PT1M1.001000S",             0,1,0,1,1,0,0)
    test_timedelta_iso_2D = td_test("P7DT1M1.001000S",           0,1,0,1,1,0,1)
    test_timedelta_iso_2E = td_test("PT1H1M1.001000S",           0,1,0,1,1,1,0)
    test_timedelta_iso_2F = td_test("P7DT1H1M1.001000S",         0,1,0,1,1,1,1)
    test_timedelta_iso_30 = td_test("PT1.000001S",               0,1,1,0,0,0,0)
    test_timedelta_iso_31 = td_test("P7DT1.000001S",             0,1,1,0,0,0,1)
    test_timedelta_iso_32 = td_test("PT1H1.000001S",             0,1,1,0,0,1,0)
    test_timedelta_iso_33 = td_test("P7DT1H1.000001S",           0,1,1,0,0,1,1)
    test_timedelta_iso_34 = td_test("PT1M1.000001S",             0,1,1,0,1,0,0)
    test_timedelta_iso_35 = td_test("P7DT1M1.000001S",           0,1,1,0,1,0,1)
    test_timedelta_iso_36 = td_test("PT1H1M1.000001S",           0,1,1,0,1,1,0)
    test_timedelta_iso_37 = td_test("P7DT1H1M1.000001S",         0,1,1,0,1,1,1)
    test_timedelta_iso_38 = td_test("PT1.001001S",               0,1,1,1,0,0,0)
    test_timedelta_iso_39 = td_test("P7DT1.001001S",             0,1,1,1,0,0,1)
    test_timedelta_iso_3A = td_test("PT1H1.001001S",             0,1,1,1,0,1,0)
    test_timedelta_iso_3B = td_test("P7DT1H1.001001S",           0,1,1,1,0,1,1)
    test_timedelta_iso_3C = td_test("PT1M1.001001S",             0,1,1,1,1,0,0)
    test_timedelta_iso_3D = td_test("P7DT1M1.001001S",           0,1,1,1,1,0,1)
    test_timedelta_iso_3E = td_test("PT1H1M1.001001S",           0,1,1,1,1,1,0)
    test_timedelta_iso_3F = td_test("P7DT1H1M1.001001S",         0,1,1,1,1,1,1)
    test_timedelta_iso_40 = td_test("P1D",                       1,0,0,0,0,0,0)
    test_timedelta_iso_41 = td_test("P8D",                       1,0,0,0,0,0,1)
    test_timedelta_iso_42 = td_test("P1DT1H",                    1,0,0,0,0,1,0)
    test_timedelta_iso_43 = td_test("P8DT1H",                    1,0,0,0,0,1,1)
    test_timedelta_iso_44 = td_test("P1DT1M",                    1,0,0,0,1,0,0)
    test_timedelta_iso_45 = td_test("P8DT1M",                    1,0,0,0,1,0,1)
    test_timedelta_iso_46 = td_test("P1DT1H1M",                  1,0,0,0,1,1,0)
    test_timedelta_iso_47 = td_test("P8DT1H1M",                  1,0,0,0,1,1,1)
    test_timedelta_iso_48 = td_test("P1DT0.001000S",             1,0,0,1,0,0,0)
    test_timedelta_iso_49 = td_test("P8DT0.001000S",             1,0,0,1,0,0,1)
    test_timedelta_iso_4A = td_test("P1DT1H0.001000S",           1,0,0,1,0,1,0)
    test_timedelta_iso_4B = td_test("P8DT1H0.001000S",           1,0,0,1,0,1,1)
    test_timedelta_iso_4C = td_test("P1DT1M0.001000S",           1,0,0,1,1,0,0)
    test_timedelta_iso_4D = td_test("P8DT1M0.001000S",           1,0,0,1,1,0,1)
    test_timedelta_iso_4E = td_test("P1DT1H1M0.001000S",         1,0,0,1,1,1,0)
    test_timedelta_iso_4F = td_test("P8DT1H1M0.001000S",         1,0,0,1,1,1,1)
    test_timedelta_iso_50 = td_test("P1DT0.000001S",             1,0,1,0,0,0,0)
    test_timedelta_iso_51 = td_test("P8DT0.000001S",             1,0,1,0,0,0,1)
    test_timedelta_iso_52 = td_test("P1DT1H0.000001S",           1,0,1,0,0,1,0)
    test_timedelta_iso_53 = td_test("P8DT1H0.000001S",           1,0,1,0,0,1,1)
    test_timedelta_iso_54 = td_test("P1DT1M0.000001S",           1,0,1,0,1,0,0)
    test_timedelta_iso_55 = td_test("P8DT1M0.000001S",           1,0,1,0,1,0,1)
    test_timedelta_iso_56 = td_test("P1DT1H1M0.000001S",         1,0,1,0,1,1,0)
    test_timedelta_iso_57 = td_test("P8DT1H1M0.000001S",         1,0,1,0,1,1,1)
    test_timedelta_iso_58 = td_test("P1DT0.001001S",             1,0,1,1,0,0,0)
    test_timedelta_iso_59 = td_test("P8DT0.001001S",             1,0,1,1,0,0,1)
    test_timedelta_iso_5A = td_test("P1DT1H0.001001S",           1,0,1,1,0,1,0)
    test_timedelta_iso_5B = td_test("P8DT1H0.001001S",           1,0,1,1,0,1,1)
    test_timedelta_iso_5C = td_test("P1DT1M0.001001S",           1,0,1,1,1,0,0)
    test_timedelta_iso_5D = td_test("P8DT1M0.001001S",           1,0,1,1,1,0,1)
    test_timedelta_iso_5E = td_test("P1DT1H1M0.001001S",         1,0,1,1,1,1,0)
    test_timedelta_iso_5F = td_test("P8DT1H1M0.001001S",         1,0,1,1,1,1,1)
    test_timedelta_iso_60 = td_test("P1DT1S",                    1,1,0,0,0,0,0)
    test_timedelta_iso_61 = td_test("P8DT1S",                    1,1,0,0,0,0,1)
    test_timedelta_iso_62 = td_test("P1DT1H1S",                  1,1,0,0,0,1,0)
    test_timedelta_iso_63 = td_test("P8DT1H1S",                  1,1,0,0,0,1,1)
    test_timedelta_iso_64 = td_test("P1DT1M1S",                  1,1,0,0,1,0,0)
    test_timedelta_iso_65 = td_test("P8DT1M1S",                  1,1,0,0,1,0,1)
    test_timedelta_iso_66 = td_test("P1DT1H1M1S",                1,1,0,0,1,1,0)
    test_timedelta_iso_67 = td_test("P8DT1H1M1S",                1,1,0,0,1,1,1)
    test_timedelta_iso_68 = td_test("P1DT1.001000S",             1,1,0,1,0,0,0)
    test_timedelta_iso_69 = td_test("P8DT1.001000S",             1,1,0,1,0,0,1)
    test_timedelta_iso_6A = td_test("P1DT1H1.001000S",           1,1,0,1,0,1,0)
    test_timedelta_iso_6B = td_test("P8DT1H1.001000S",           1,1,0,1,0,1,1)
    test_timedelta_iso_6C = td_test("P1DT1M1.001000S",           1,1,0,1,1,0,0)
    test_timedelta_iso_6D = td_test("P8DT1M1.001000S",           1,1,0,1,1,0,1)
    test_timedelta_iso_6E = td_test("P1DT1H1M1.001000S",         1,1,0,1,1,1,0)
    test_timedelta_iso_6F = td_test("P8DT1H1M1.001000S",         1,1,0,1,1,1,1)
    test_timedelta_iso_70 = td_test("P1DT1.000001S",             1,1,1,0,0,0,0)
    test_timedelta_iso_71 = td_test("P8DT1.000001S",             1,1,1,0,0,0,1)
    test_timedelta_iso_72 = td_test("P1DT1H1.000001S",           1,1,1,0,0,1,0)
    test_timedelta_iso_73 = td_test("P8DT1H1.000001S",           1,1,1,0,0,1,1)
    test_timedelta_iso_74 = td_test("P1DT1M1.000001S",           1,1,1,0,1,0,0)
    test_timedelta_iso_75 = td_test("P8DT1M1.000001S",           1,1,1,0,1,0,1)
    test_timedelta_iso_76 = td_test("P1DT1H1M1.000001S",         1,1,1,0,1,1,0)
    test_timedelta_iso_77 = td_test("P8DT1H1M1.000001S",         1,1,1,0,1,1,1)
    test_timedelta_iso_78 = td_test("P1DT1.001001S",             1,1,1,1,0,0,0)
    test_timedelta_iso_79 = td_test("P8DT1.001001S",             1,1,1,1,0,0,1)
    test_timedelta_iso_7A = td_test("P1DT1H1.001001S",           1,1,1,1,0,1,0)
    test_timedelta_iso_7B = td_test("P8DT1H1.001001S",           1,1,1,1,0,1,1)
    test_timedelta_iso_7C = td_test("P1DT1M1.001001S",           1,1,1,1,1,0,0)
    test_timedelta_iso_7D = td_test("P8DT1M1.001001S",           1,1,1,1,1,0,1)
    test_timedelta_iso_7E = td_test("P1DT1H1M1.001001S",         1,1,1,1,1,1,0)
    test_timedelta_iso_7F = td_test("P8DT1H1M1.001001S",         1,1,1,1,1,1,1)

    test_timedelta_iso_negd = td_test("-P1D", days=-1)
    test_timedelta_iso_negs = td_test("-PT1S", seconds=-1)
    test_timedelta_iso_d_negs = td_test("PT23H59M59S", days=1, seconds=-1)
    test_timedelta_iso_s_negd = td_test("-PT23H59M59S", days=-1, seconds=1)
