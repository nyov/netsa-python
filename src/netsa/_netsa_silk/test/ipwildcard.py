# Copyright 2008-2013 by Carnegie Mellon University

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

import operator
import unittest

import netsa._netsa_silk
from netsa._netsa_silk import IPAddr, IPv4Addr, IPv6Addr, IPWildcard

def ipv6_enabled():
    return True

class IPWildcardTest(unittest.TestCase):

    def test_parse_1(self):
        IPWildcard('1.2.3.0/24')

    def test_parse_2(self):
        IPWildcard('ff80::/16')

    def test_parse_3(self):
        IPWildcard('1.2.3.4')

    def test_parse_4(self):
        IPWildcard('::FFFF:0102:0304')

    def test_parse_5(self):
        IPWildcard('16909056')

    def test_parse_6(self):
        IPWildcard('16909056/24')

    def test_parse_7(self):
        IPWildcard('1.2.3.x')

    def test_parse_8(self):
        IPWildcard('1:2:3:4:5:6:7:x')

    def test_parse_9(self):
        IPWildcard('1.2,3.4,5.6,7')

    def test_parse_10(self):
        IPWildcard('1.2.3.0-255')

    def test_parse_11(self):
        IPWildcard('::2-4')

    def test_parse_12(self):
        IPWildcard('1-2:3-4:5-6:7-8:9-a:b-c:d-e:0-ffff')

    def test_x_in_ipv6(self):
        self.assertEqual(len(list(IPWildcard('2000::x'))), 65536)

    def test_iter_1(self):
        self.assertEqual([IPAddr(x) for x in ['1.2.3.4', '1.2.3.5', '1.2.3.6']],
                         list(IPWildcard('1.2.3.4-6')))

    def test_iter_2(self):
        self.assertEqual([IPAddr(x) for x in ['2000::1', '2000::2', '2000::3']],
                         list(IPWildcard('2000::1-3')))

    def test_in_1(self):
        self.assertTrue('1.2.3.4' in IPWildcard('1.2.3.x'))

    def test_in_2(self):
        self.assertFalse('1.2.4.3' in IPWildcard('1.2.3.x'))

    def test_in_3(self):
        self.assertRaises(ValueError, operator.contains,
                          IPWildcard('1.2.3.x'), '1x2x3x4')

    def test_in_4(self):
        self.assertTrue(IPAddr('1.2.3.4') in IPWildcard('1.2.3.x'))

    def test_in_5(self):
        self.assertFalse(IPAddr('1.2.4.3') in IPWildcard('1.2.3.x'))

    def test_in_6(self):
        self.assertTrue('2000::1' in IPWildcard('2000::x:x'))

    def test_in_7(self):
        self.assertFalse('2001::1' in IPWildcard('2000::x:x'))

    def test_in_8(self):
        self.assertTrue('1.2.3.4' in IPWildcard('::ffff:1.2.3.x'))

    def test_in_9(self):
        self.assertTrue('::ffff:1.2.3.4' in IPWildcard('1.2.3.x'))

    def test_str_1(self):
        self.assertEqual(str(IPWildcard('1.2.3.x')), '1.2.3.x')

    def test_str_2(self):
        self.assertEqual(str(IPWildcard('2000::1')), '2000::1')

    def test_is_ipv6_1(self):
        self.assertFalse(IPWildcard('1.2.3.4').is_ipv6())

    def test_is_ipv6_2(self):
        self.assertTrue(IPWildcard('2000::1').is_ipv6())

    def test_is_ipv6_3(self):
        self.assertTrue(IPWildcard('::ffff:1.2.3.4').is_ipv6())

    def test_silk_IPWildcardConstruction(self):
        IPWildcard("0.0.0.0")
        IPWildcard("255.255.255.255")
        IPWildcard("     255.255.255.255")
        IPWildcard("255.255.255.255     ")
        IPWildcard("   255.255.255.255  ")
        IPWildcard("0.0.0.0/31")
        IPWildcard("255.255.255.254-255")
        IPWildcard("3,2,1.4.5.6")
        IPWildcard("0.0.0.1,31,51,71,91,101,121,141,161,181,211,231,251")
        IPWildcard("0,255.0,255.0,255.0,255")
        IPWildcard("1.1.128.0/22")
        IPWildcard("128.x.0.0")
        IPWildcard("128.0-255.0.0")
        IPWildcard("128.0,128-255,1-127.0.0")
        IPWildcard("128.0,128,129-253,255-255,254,1-127.0.0")
        IPWildcard("128.0,128-255,1-127.0.0  ")
        IPWildcard("  128.0,128-255,1-127.0.0  ")
        IPWildcard("  128.0,128-255,,1-127.0.0  ")
        IPWildcard(IPWildcard("0.0.0.0"))
        if ipv6_enabled():
            IPWildcard("0:0:0:0:0:0:0:0")
            IPWildcard("::")
            IPWildcard("::0.0.0.0")
            IPWildcard("1:2:3:4:5:6:7:8")
            IPWildcard("1:203:405:607:809:a0b:c0d:e0f")
            IPWildcard("1:203:405:607:809:a0b:12.13.14.15")
            IPWildcard("::FFFF")
            IPWildcard("::FFFF:FFFF")
            IPWildcard("::0.0.255.255")
            IPWildcard("::255.255.255.255")
            IPWildcard("FFFF::")
            IPWildcard("0,FFFF::0,FFFF")
            IPWildcard("::FFFF:0,10.0.0.0,10")
            IPWildcard("::FFFF:0.0,160.0,160.0")
            IPWildcard("0:0:0:0:0:0:0:0/127")
            IPWildcard("::/127")
            IPWildcard("0:0:0:0:0:0:0:0/110")
            IPWildcard("0:0:0:0:0:0:0:0/95")
            IPWildcard("0:ffff::0/127")
            IPWildcard("0:ffff::0.0.0.0,1")
            IPWildcard("0:ffff::0.0.0.0-10")
            IPWildcard("0:ffff::0.0.0.x")
            IPWildcard("::ffff:0:0:0:0:0:0/110")
            IPWildcard("0:ffff::/112")
            IPWildcard("0:ffff:0:0:0:0:0:x")
            IPWildcard("0:ffff:0:0:0:0:0:x")
            IPWildcard("0:ffff:0:0:0:0:0:0-ffff")
            IPWildcard("0:ffff:0:0:0:0:0.0.x.x")
            IPWildcard("0:ffff:0:0:0:0:0.0.0-255.128-254,0-126,255,127")
            IPWildcard("0:ffff:0:0:0:0:0.0.128-254,0-126,255,127.x")
            IPWildcard("0:ffff:0:0:0:0:0.0.0.0/112")
            IPWildcard("0:ffff:0:0:0:0:0.0,1.x.x")
            IPWildcard("0:ffff:0:0:0:0:0:0-10,10-20,24,23,22,21,25-ffff")
            IPWildcard("0:ffff::x")
            IPWildcard("0:ffff:0:0:0:0:0:aaab-ffff,aaaa-aaaa,0-aaa9")
            IPWildcard("0:ffff:0:0:0:0:0:ff00/120")
            IPWildcard("0:ffff:0:0:0:0:0:ffff/120")
            IPWildcard("::ff00:0/104")
            IPWildcard("::x")
            IPWildcard("x::")
            IPWildcard("x::10.10.10.10")
            IPWildcard(IPWildcard("::"))

    def test_silk_IPWildcardBadStrings(self):
        self.assertRaises(ValueError, IPWildcard, "0.0.0.0/33")
        self.assertRaises(ValueError, IPWildcard, "0.0.0.2-0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0.256")
        self.assertRaises(ValueError, IPWildcard, "0.0.256.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0256.0")
        self.assertRaises(ValueError, IPWildcard, "0.256.0.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0.0.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.x.0/31")
        self.assertRaises(ValueError, IPWildcard, "0.0.x.0:0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0,1.0/31")
        self.assertRaises(ValueError, IPWildcard, "0.0.0-1.0/31")
        self.assertRaises(ValueError, IPWildcard, "0.0.0-1-.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0--1.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0.0 junk")
        self.assertRaises(ValueError, IPWildcard, "0.0.-0-1.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.-1.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0..0")
        self.assertRaises(ValueError, IPWildcard, ".0.0.0.0")
        self.assertRaises(ValueError, IPWildcard, "0.0.0.0.")
        self.assertRaises(ValueError, IPWildcard, "1-FF::/16")
        self.assertRaises(ValueError, IPWildcard, "1,2::/16")
        self.assertRaises(ValueError, IPWildcard, "1::2::3")
        self.assertRaises(ValueError, IPWildcard, ":1::")
        self.assertRaises(ValueError, IPWildcard, ":1:2:3:4:5:6:7:8")
        self.assertRaises(ValueError, IPWildcard, "1:2:3:4:5:6:7:8:")
        self.assertRaises(ValueError, IPWildcard, "1:2:3:4:5:6:7.8.9:10")
        self.assertRaises(ValueError, IPWildcard, "1:2:3:4:5:6:7:8.9.10.11")
        self.assertRaises(ValueError, IPWildcard, ":")
        self.assertRaises(ValueError, IPWildcard, "1:2:3:4:5:6:7")
        self.assertRaises(ValueError, IPWildcard, "1:2:3:4:5:6:7/16")
        self.assertRaises(ValueError, IPWildcard, "FFFFF::")
        self.assertRaises(ValueError, IPWildcard, "::FFFFF")
        self.assertRaises(ValueError, IPWildcard, "1:FFFFF::7:8")
        self.assertRaises(ValueError, IPWildcard, "1:AAAA-FFFF0::")
        self.assertRaises(ValueError, IPWildcard, "FFFFF-AAAA::")
        self.assertRaises(ValueError, IPWildcard, "FFFF-AAAA::")
        self.assertRaises(ValueError, IPWildcard, "2-1::")
        self.assertRaises(ValueError, IPWildcard, "1:FFFF-0::")
        self.assertRaises(ValueError, IPWildcard, "1::FFFF-AAAA")
        self.assertRaises(ValueError, IPWildcard, ":::")
        self.assertRaises(ValueError, IPWildcard, "1:2:3:$::")
        self.assertRaises(ValueError, IPWildcard, "1.2.3.4:ffff::")
        self.assertRaises(ValueError, IPWildcard, "x")

    def test_silk_IPWildcardContainment(self):
        wild = IPWildcard("0.0.0.0")
        self.assert_(IPAddr("0.0.0.0") in wild)
        self.assert_(IPAddr("0.0.0.1") not in wild)
        self.assert_("0.0.0.0" in wild)
        self.assert_("0.0.0.1" not in wild)
        wild = IPWildcard("0.0.0.0/31")
        self.assert_(IPAddr("0.0.0.0") in wild)
        self.assert_(IPAddr("0.0.0.1") in wild)
        self.assert_(IPAddr("0.0.0.2") not in wild)
        self.assert_("0.0.0.0" in wild)
        self.assert_("0.0.0.1" in wild)
        self.assert_("0.0.0.2" not in wild)
        wild = IPWildcard("255.255.255.254-255")
        self.assert_(IPAddr("255.255.255.254") in wild)
        self.assert_(IPAddr("255.255.255.255") in wild)
        self.assert_(IPAddr("255.255.255.253") not in wild)
        self.assert_("255.255.255.254" in wild)
        self.assert_("255.255.255.255" in wild)
        self.assert_("255.255.255.253" not in wild)
        wild = IPWildcard("3,2,1.4.5.6")
        self.assert_(IPAddr("1.4.5.6") in wild)
        self.assert_(IPAddr("2.4.5.6") in wild)
        self.assert_(IPAddr("3.4.5.6") in wild)
        self.assert_(IPAddr("4.4.5.6") not in wild)
        self.assert_("1.4.5.6" in wild)
        self.assert_("2.4.5.6" in wild)
        self.assert_("3.4.5.6" in wild)
        self.assert_("4.4.5.6" not in wild)
        wild = IPWildcard("0,255.0,255.0,255.0,255")
        self.assert_(IPAddr("0.0.0.0") in wild)
        self.assert_(IPAddr("0.0.0.255") in wild)
        self.assert_(IPAddr("0.0.255.0") in wild)
        self.assert_(IPAddr("0.255.0.0") in wild)
        self.assert_(IPAddr("255.0.0.0") in wild)
        self.assert_(IPAddr("255.255.0.0") in wild)
        self.assert_(IPAddr("255.0.255.0") in wild)
        self.assert_(IPAddr("255.0.0.255") in wild)
        self.assert_(IPAddr("0.255.0.255") in wild)
        self.assert_(IPAddr("0.255.255.0") in wild)
        self.assert_(IPAddr("0.0.255.255") in wild)
        self.assert_(IPAddr("0.255.255.255") in wild)
        self.assert_(IPAddr("255.0.255.255") in wild)
        self.assert_(IPAddr("255.255.0.255") in wild)
        self.assert_(IPAddr("255.255.255.0") in wild)
        self.assert_(IPAddr("255.255.255.255") in wild)
        self.assert_(IPAddr("255.255.255.254") not in wild)
        self.assert_(IPAddr("255.255.254.255") not in wild)
        self.assert_(IPAddr("255.254.255.255") not in wild)
        self.assert_(IPAddr("254.255.255.255") not in wild)
        self.assert_("0.0.0.0" in wild)
        self.assert_("0.0.0.255" in wild)
        self.assert_("0.0.255.0" in wild)
        self.assert_("0.255.0.0" in wild)
        self.assert_("255.0.0.0" in wild)
        self.assert_("255.255.0.0" in wild)
        self.assert_("255.0.255.0" in wild)
        self.assert_("255.0.0.255" in wild)
        self.assert_("0.255.0.255" in wild)
        self.assert_("0.255.255.0" in wild)
        self.assert_("0.0.255.255" in wild)
        self.assert_("0.255.255.255" in wild)
        self.assert_("255.0.255.255" in wild)
        self.assert_("255.255.0.255" in wild)
        self.assert_("255.255.255.0" in wild)
        self.assert_("255.255.255.255" in wild)
        self.assert_("255.255.255.254" not in wild)
        self.assert_("255.255.254.255" not in wild)
        self.assert_("255.254.255.255" not in wild)
        self.assert_("254.255.255.255" not in wild)
        if ipv6_enabled():
            wild = IPWildcard("::")
            self.assert_(IPAddr("::") in wild)
            self.assert_(IPAddr("::1") not in wild)
            self.assert_("::" in wild)
            self.assert_("::1" not in wild)
            wild = IPWildcard("::/127")
            self.assert_(IPAddr("::") in wild)
            self.assert_(IPAddr("::1") in wild)
            self.assert_(IPAddr("::2") not in wild)
            self.assert_("::" in wild)
            self.assert_("::1" in wild)
            self.assert_("::2" not in wild)
            wild = IPWildcard("0:ffff::0.0.0.0,1")
            self.assert_(IPAddr("0:ffff::0.0.0.0") in wild)
            self.assert_(IPAddr("0:ffff::0.0.0.1") in wild)
            self.assert_(IPAddr("0:ffff::0.0.0.2") not in wild)
            self.assert_("0:ffff::0.0.0.0" in wild)
            self.assert_("0:ffff::0.0.0.1" in wild)
            self.assert_("0:ffff::0.0.0.2" not in wild)
            wild = IPWildcard("0:ffff:0:0:0:0:0.253-254.125-126,255.x")
            self.assert_(IPAddr("0:ffff::0.253.125.1") in wild)
            self.assert_(IPAddr("0:ffff::0.254.125.2") in wild)
            self.assert_(IPAddr("0:ffff::0.253.126.3") in wild)
            self.assert_(IPAddr("0:ffff::0.254.126.4") in wild)
            self.assert_(IPAddr("0:ffff::0.253.255.5") in wild)
            self.assert_(IPAddr("0:ffff::0.254.255.6") in wild)
            self.assert_(IPAddr("0:ffff::0.255.255.7") not in wild)
            self.assert_("0:ffff::0.253.125.1" in wild)
            self.assert_("0:ffff::0.254.125.2" in wild)
            self.assert_("0:ffff::0.253.126.3" in wild)
            self.assert_("0:ffff::0.254.126.4" in wild)
            self.assert_("0:ffff::0.253.255.5" in wild)
            self.assert_("0:ffff::0.254.255.6" in wild)
            self.assert_("0:ffff::0.255.255.7" not in wild)
            wild = IPWildcard("0.0.0.0")
            self.assert_("::ffff:0:0" in wild)
            self.assert_("::" not in wild)
            wild = IPWildcard("::ffff:0:0")
            self.assert_("0.0.0.0" in wild)
            wild = IPWildcard("::")
            self.assert_("0.0.0.0" not in wild)

    def test_silk_IPWildcardIteration(self):
        self.assertEqual(set(IPWildcard("0.0.0.0")), set([IPAddr("0.0.0.0")]))
        self.assertEqual(set(IPWildcard("0.0.0.0/31")),
                         set(IPAddr(x) for x in ["0.0.0.0", "0.0.0.1"]))
        self.assertEqual(set(IPWildcard("255.255.255.254-255")),
                         set(IPAddr(x) for x in ["255.255.255.254",
                                                 "255.255.255.255"]))
        self.assertEqual(set(IPWildcard("3,2,1.4.5.6")),
                         set(IPAddr(x) for x in ["1.4.5.6",
                                                 "2.4.5.6",
                                                 "3.4.5.6"]))
        self.assertEqual(set(IPWildcard("0,255.0,255.0,255.0,255")),
                         set(IPAddr(x) for x in ["0.0.0.0",
                                                 "0.0.0.255",
                                                 "0.0.255.0",
                                                 "0.255.0.0",
                                                 "255.0.0.0",
                                                 "255.255.0.0",
                                                 "255.0.255.0",
                                                 "255.0.0.255",
                                                 "0.255.0.255",
                                                 "0.255.255.0",
                                                 "0.0.255.255",
                                                 "0.255.255.255",
                                                 "255.0.255.255",
                                                 "255.255.0.255",
                                                 "255.255.255.0",
                                                 "255.255.255.255"]))
        if ipv6_enabled():
            self.assertEqual(set(IPWildcard("::")), set([IPAddr("::")]))
            self.assertEqual(set(IPWildcard("::/127")),
                             set(IPAddr(x) for x in ["::0", "::1"]))
            self.assertEqual(set(IPWildcard("0:ffff::0.0.0.0,1")),
                             set(IPAddr(x) for x in
                                 ["0:ffff::0", "0:ffff::1"]))
            self.assertEqual(set(IPWildcard(
                        "0:ffff::0.253-254.125-126,255.1")),
                             set(IPAddr(x) for x in ["0:ffff::0.253.125.1",
                                                     "0:ffff::0.253.126.1",
                                                     "0:ffff::0.253.255.1",
                                                     "0:ffff::0.254.125.1",
                                                     "0:ffff::0.254.126.1",
                                                     "0:ffff::0.254.255.1"]))

    def test_silk_IPWildcardIsIPv6(self):
        wild = IPWildcard("0.0.0.0")
        self.assertEqual(wild.is_ipv6(), False)
        wild = IPWildcard("0.0.0.0/31")
        self.assertEqual(wild.is_ipv6(), False)
        wild = IPWildcard("255.255.255.254-255")
        self.assertEqual(wild.is_ipv6(), False)
        wild = IPWildcard("3,2,1.4.5.6")
        self.assertEqual(wild.is_ipv6(), False)
        wild = IPWildcard("0,255.0,255.0,255.0,255")
        self.assertEqual(wild.is_ipv6(), False)
        if ipv6_enabled():
            wild = IPWildcard("::")
            self.assertEqual(wild.is_ipv6(), True)
            wild = IPWildcard("::/127")
            self.assertEqual(wild.is_ipv6(), True)
            wild = IPWildcard("0:ffff::0.0.0.0,1")
            self.assertEqual(wild.is_ipv6(), True)
            wild = IPWildcard("0:ffff:0:0:0:0:0.253-254.125-126,255.x")
            self.assertEqual(wild.is_ipv6(), True)
