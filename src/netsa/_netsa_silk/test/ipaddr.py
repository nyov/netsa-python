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

import unittest

import netsa._netsa_silk
from netsa._netsa_silk import IPAddr, IPv4Addr, IPv6Addr, has_IPv6Addr

def ipv6_enabled():
    return True

class IPAddrTest(unittest.TestCase):

    def test_v4_parse_type(self):
        self.assertEqual(
            type(IPAddr("123.4.56.78")),
            IPv4Addr)

    def test_v4_parse_1(self):
        self.assertEqual(
            IPAddr("123.4.56.78"),
            IPv4Addr("123.4.56.78"))

    def test_v4_parse_2(self):
        self.assertEqual(
            IPAddr(" 123.4.56.78 "),
            IPv4Addr("123.4.56.78"))

    def test_v4_parse_3(self):
        self.assertEqual(
            IPAddr("123.004.0056.00078"),
            IPv4Addr("123.4.56.78"))

    def test_v4_parse_4(self):
        self.assertEqual(
            IPAddr("12345678"),
            IPv4Addr("12345678"))

    def test_v4_str_1(self):
        self.assertEqual(
            str(IPAddr("123.4.56.78")),
            "123.4.56.78")

    def test_v4_str_2(self):
        self.assertEqual(
            str(IPAddr("123.004.56.78")),
            "123.4.56.78")

    def test_v4_pad_1(self):
        self.assertEqual(
            IPAddr("123.4.56.78").padded(),
            "123.004.056.078")

    def test_v4_pad_2(self):
        self.assertEqual(
            IPAddr("0.1.10.100").padded(),
            "000.001.010.100")

    def test_v4_int_1(self):
        self.assertEqual(
            int(IPAddr("0.0.0.0")),
            0)

    def test_v4_int_2(self):
        self.assertEqual(
            int(IPAddr("255.255.255.255")),
            0xFFFFFFFF)

    def test_v4_int_3(self):
        self.assertEqual(
            int(IPAddr("10.0.0.0")),
            0x0A000000)

    def test_v4_int_4(self):
        self.assertEqual(
            int(IPAddr("10.10.10.10")),
            0x0A0A0A0A)

    def test_v4_int_5(self):
        self.assertEqual(
            int(IPAddr("1234567890")),
            1234567890)

    def test_v4_int_6(self):
        self.assertEqual(
            int(IPAddr("167772160")),
            167772160)

    def test_int_v4_1(self):
        self.assertEqual(
            int(IPv4Addr(0)),
            0)

    def test_int_v4_2(self):
        self.assertEqual(
            int(IPv4Addr(4294967295)),
            4294967295)

    def test_int_v4_3(self):
        self.assertEqual(
            int(IPv4Addr(167772160)),
            167772160)

    def test_int_v4_4(self):
        self.assertRaises(ValueError, IPv4Addr, -1)

    def test_int_v4_5(self):
        self.assertRaises(ValueError, IPv4Addr, 0x100000000)

    def test_str_v4_1(self):
        self.assertRaises(ValueError, IPAddr, "010.000.000.000x")

    def test_str_v4_2(self):
        self.assertRaises(ValueError, IPAddr, "010.000.000.000a")

    def test_str_v4_3(self):
        self.assertRaises(ValueError, IPAddr, "010.000.000.000|")

    def test_str_v4_4(self):
        self.assertRaises(ValueError, IPAddr, '       10.0.0.0:80')

    def test_str_v4_5(self):
        self.assertRaises(ValueError, IPAddr, '10.0.0.0     .')

    def test_str_v4_6(self):
        self.assertRaises(ValueError, IPAddr, '     167772160|')

    def test_str_v4_7(self):
        self.assertRaises(ValueError, IPAddr, '')

    def test_str_v4_8(self):
        self.assertRaises(ValueError, IPAddr, '  ')

    def test_str_v4_9(self):
        self.assertRaises(ValueError, IPAddr, '10..10.10.10')

    def test_str_v4_10(self):
        self.assertRaises(ValueError, IPAddr, '  -167772160')

    def test_str_v4_11(self):
        self.assertRaises(ValueError, IPAddr, '  -167772160|')

    def test_str_v4_12(self):
        self.assertRaises(ValueError, IPAddr, '  167772160.')

    def test_str_v4_13(self):
        self.assertRaises(ValueError, IPAddr, '256.256.256.256')

    def test_str_v4_14(self):
        self.assertRaises(ValueError, IPAddr, '10.')

    def test_str_v4_15(self):
        self.assertRaises(ValueError, IPAddr, '10.x.x.x')

    def test_str_v4_16(self):
        self.assertRaises(ValueError, IPAddr, '.10.10.10.10')

    def test_str_v4_17(self):
        self.assertRaises(ValueError, IPAddr, '10.10.10.10.')

    def test_str_v4_18(self):
        self.assertRaises(ValueError, IPAddr, '10.10|10.10')

    def test_str_v4_19(self):
        self.assertRaises(ValueError, IPAddr, '10 . 10 . 10 . 10')

    def test_v6_parse_type(self):
        self.assertEqual(
            type(IPAddr("123:4::56:78")),
            IPv6Addr)

    def test_v6_parse_1(self):
        self.assertEqual(
            IPAddr("123:4::56:78"),
            IPv6Addr("123:4::56:78"))

    def test_v6_parse_2(self):
        self.assertEqual(
            IPAddr("  123:4::56:78  "),
            IPv6Addr("123:4::56:78"))

    def test_v6_parse_3(self):
        self.assertEqual(
            IPAddr("::56:78"),
            IPv6Addr("::56:78"))

    def test_v6_parse_4(self):
        self.assertEqual(
            IPAddr("::"),
            IPv6Addr("::"))

    def test_v6_parse_5(self):
        self.assertEqual(
            IPAddr("123:004::0056:00078"),
            IPv6Addr("123:4::56:78"))

    def test_v6_parse_6(self):
        self.assertEqual(
            IPAddr("::123.4.56.78"),
            IPv6Addr("::123.4.56.78"))

    def test_v6_parse_7(self):
        self.assertEqual(
            IPAddr("abc:d::ef:12"),
            IPv6Addr("abc:d::ef:12"))

    def test_v6_parse_8(self):
        self.assertEqual(
            IPAddr("ABC:D::EF:12"),
            IPv6Addr("abc:d::ef:12"))

    def test_v6_parse_9(self):
        self.assertRaises(ValueError, IPv6Addr, ' 0 : : :: 0')

    def test_v6_str_1(self):
        self.assertEqual(
            str(IPAddr("123:4::56:78")),
            "123:4::56:78")

    def test_v6_str_2(self):
        self.assertEqual(
            str(IPAddr("0:0:0:0:0:0:0:0")),
            "::")

    def test_v6_str_3(self):
        self.assertEqual(
            str(IPAddr("0:0:0:0:0:0:0:1")),
            "::1")

    def test_v6_str_4(self):
        self.assertEqual(
            str(IPAddr("::fefe:123.4.56.78")),
            "::fefe:7b04:384e")

    def test_v6_str_5(self):
        self.assertEqual(
            str(IPAddr("::123.4.56.78")),
            "::123.4.56.78")

    def test_v6_str_6(self):
        self.assertEqual(
            str(IPAddr("::ffff:123.4.56.78")),
            "::ffff:123.4.56.78")

    def test_v6_str_7(self):
        self.assertEqual(
            str(IPAddr("ABC:D::EF:12")),
            "abc:d::ef:12")

    def test_v6_str_8(self):
        self.assertEqual(
            str(IPAddr("1:0:2:0:0:0:3:0")),
            "1:0:2::3:0")

    def test_v6_str_9(self):
        self.assertEqual(
            str(IPAddr("1:2:3:4:0:6:7:8")),
            "1:2:3:4:0:6:7:8")

    def test_v6_pad_1(self):
        self.assertEqual(
            IPAddr("123:4::56:78").padded(),
            "0123:0004:0000:0000:0000:0000:0056:0078")

    def test_v6_pad_2(self):
        self.assertEqual(
            IPAddr("0:0:0:0:0:0:0:0").padded(),
            "0000:0000:0000:0000:0000:0000:0000:0000")

    def test_v6_pad_3(self):
        self.assertEqual(
            IPAddr("0:0:0:0:0:0:0:1").padded(),
            "0000:0000:0000:0000:0000:0000:0000:0001")

    def test_v6_pad_4(self):
        self.assertEqual(
            IPAddr("::fefe:123.4.56.78").padded(),
            "0000:0000:0000:0000:0000:fefe:7b04:384e")

    def test_v6_pad_5(self):
        self.assertEqual(
            IPAddr("::123.4.56.78").padded(),
            "0000:0000:0000:0000:0000:0000:7b04:384e")

    def test_v6_pad_6(self):
        self.assertEqual(
            IPAddr("::ffff:123.4.56.78").padded(),
            "0000:0000:0000:0000:0000:ffff:7b04:384e")

    def test_v6_pad_7(self):
        self.assertEqual(
            IPAddr("ABC:D::EF:12").padded(),
            "0abc:000d:0000:0000:0000:0000:00ef:0012")

    def test_v6_pad_8(self):
        self.assertEqual(
            IPAddr("1:0:2:0:0:0:3:0").padded(),
            "0001:0000:0002:0000:0000:0000:0003:0000")

    def test_v6_pad_9(self):
        self.assertEqual(
            IPAddr("1:2:3:4:0:6:7:8").padded(),
            "0001:0002:0003:0004:0000:0006:0007:0008")

    def test_v6_int_1(self):
        self.assertEqual(
            int(IPAddr("::")),
            0)

    def test_v6_int_2(self):
        self.assertEqual(
            int(IPAddr("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")),
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

    def test_v6_int_3(self):
        self.assertEqual(
            int(IPAddr("abc:d::ef:12")),
            0x0ABC000D000000000000000000EF0012)

    def test_v6_int_4(self):
        self.assertEqual(
            int(IPAddr("1011:1213:1415:1617:2021:2223:36.37.38.39")),
            0x10111213141516172021222324252627)

    def test_int_v6_1(self):
        self.assertEqual(
            int(IPv6Addr(0)),
            0)

    def test_int_v6_2(self):
        self.assertEqual(
            int(IPv6Addr(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)),
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

    def test_int_v6_3(self):
        self.assertEqual(
            int(IPv6Addr(0x10101010101010101010101010101010)),
            0x10101010101010101010101010101010)

    def test_int_v6_4(self):
        self.assertRaises(ValueError, IPv6Addr, -1)

    def test_int_v6_5(self):
        self.assertRaises(ValueError,
                          IPv6Addr, 0x100000000000000000000000000000000)

    def test_str_v6_1(self):
        self.assertRaises(ValueError, IPAddr, ": :")

    def test_str_v6_2(self):
        self.assertRaises(ValueError, IPAddr, "0::0::0")

    def test_str_v6_3(self):
        self.assertRaises(ValueError, IPAddr, "10000:1:2:3::")

    def test_str_v6_4(self):
        self.assertRaises(ValueError, IPAddr, '1:2:3:4:5:6:7')

    def test_str_v6_5(self):
        self.assertRaises(ValueError, IPAddr, '10:')

    def test_str_v6_6(self):
        self.assertRaises(ValueError, IPAddr, '1:2:3:-4::')

    def test_str_v6_7(self):
        self.assertRaises(ValueError, IPAddr, '10:10.10:10::')

    def test_str_v6_8(self):
        self.assertRaises(ValueError, IPAddr, '::10:10:10:10:STUFF')

    def test_str_v6_9(self):
        self.assertRaises(ValueError, IPAddr, ':::1')

    def test_str_v6_10(self):
        self.assertRaises(ValueError, IPAddr, '10:x:x:x:x:x:x:x')

    def test_str_v6_11(self):
        self.assertRaises(ValueError, IPAddr, '1:2:3:4:5:6:7:8:9')

    def test_str_v6_12(self):
        self.assertRaises(ValueError, IPAddr, '10:10:10:10:')

    def test_str_v6_13(self):
        self.assertRaises(ValueError, IPAddr, '|0:0|0:0:0:0:0:0')

    def test_str_v6_14(self):
        self.assertRaises(ValueError, IPAddr, '::ffff:-1')

    def test_str_v6_15(self):
        self.assertRaises(ValueError, IPAddr, '::ffff:10000')

    def test_str_v6_16(self):
        self.assertRaises(ValueError, IPAddr, '::ffff:1.2.3.4.')

    def test_str_v6_17(self):
        self.assertRaises(ValueError, IPAddr, '::ffff:256.1.1.1')

    def test_str_v6_18(self):
        self.assertRaises(ValueError, IPAddr, '10.10|10.10')

    def test_str_v6_19(self):
        self.assertRaises(ValueError, IPAddr, '10 . 10 . 10 . 10')

    def test_ip_bad_1(self):
        self.assertRaises(TypeError, IPAddr, 2.4)

    def test_ip_bad_2(self):
        self.assertRaises(TypeError, IPAddr, None)

    def test_ip_bad_3(self):
        self.assertRaises(TypeError, IPAddr, ['1.2.3.4'])

    def test_ip_bad_4(self):
        self.assertRaises(TypeError, IPAddr, ('1.2.3.4',))

    def test_v6_bad_1(self):
        self.assertRaises(ValueError, IPv6Addr, '1.2.3.4')

    def test_ip_v4(self):
        self.assertEqual(IPv4Addr(0), IPAddr(IPv4Addr(0)))

    def test_v4_ip_1(self):
        self.assertEqual(IPv4Addr(0), IPv4Addr(IPAddr("0.0.0.0")))

    def test_v4_ip_2(self):
        self.assertEqual(IPv4Addr(0), IPv4Addr(IPAddr("::ffff:0.0.0.0")))

    def test_ip_v6(self):
        self.assertEqual(IPv6Addr(0), IPAddr(IPv6Addr(0)))

    def test_v6_ip_1(self):
        self.assertEqual(IPv6Addr("::ffff:0.0.0.0"),
                         IPv6Addr(IPAddr("0.0.0.0")))

    def test_v6_ip_2(self):
        self.assertEqual(IPv6Addr("2000::cdef"),
                         IPv6Addr(IPAddr("2000::cdef")))

    def test_has_IPv6Addr(self):
        self.assertTrue(has_IPv6Addr())

    def test_v4_eq(self):
        self.assertTrue(IPv4Addr(0) == IPv4Addr(0))

    def test_v4_lt(self):
        self.assertTrue(IPv4Addr(0) < IPv4Addr(256))

    def test_v4_le_1(self):
        self.assertTrue(IPv4Addr(0) <= IPv4Addr(256))

    def test_v4_le_2(self):
        self.assertTrue(IPv4Addr(256) <= IPv4Addr(256))

    def test_v4_gt(self):
        self.assertTrue(IPv4Addr(256) > IPv4Addr(0))

    def test_v4_ge_1(self):
        self.assertTrue(IPv4Addr(256) >= IPv4Addr(0))

    def test_v4_ge_2(self):
        self.assertTrue(IPv4Addr(0) >= IPv4Addr(0))

    def test_v4_cmp_1(self):
        self.assertEqual(cmp(IPv4Addr(128), IPv4Addr(128)), 0)

    def test_v4_cmp_2(self):
        self.assertEqual(cmp(IPv4Addr(0), IPv4Addr(128)), -1)

    def test_v4_cmp_3(self):
        self.assertEqual(cmp(IPv4Addr(128), IPv4Addr(0)), 1)

    def test_v6_eq(self):
        self.assertTrue(IPv6Addr(0) == IPv6Addr(0))

    def test_v6_lt(self):
        self.assertTrue(IPv6Addr(0) < IPv6Addr(256))

    def test_v6_le_1(self):
        self.assertTrue(IPv6Addr(0) <= IPv6Addr(0))

    def test_v6_le_2(self):
        self.assertTrue(IPv6Addr(256) <= IPv6Addr(256))

    def test_v6_gt(self):
        self.assertTrue(IPv6Addr(256) > IPv6Addr(0))

    def test_v6_ge_1(self):
        self.assertTrue(IPv6Addr(256) >= IPv6Addr(0))

    def test_v6_ge_2(self):
        self.assertTrue(IPv6Addr(0) >= IPv6Addr(0))

    def test_v6_cmp_1(self):
        self.assertEqual(cmp(IPv6Addr(128), IPv6Addr(128)), 0)

    def test_v6_cmp_2(self):
        self.assertEqual(cmp(IPv6Addr(0), IPv6Addr(128)), -1)

    def test_v6_cmp_3(self):
        self.assertEqual(cmp(IPv6Addr(128), IPv6Addr(0)), 1)

    def test_v4_v6_cmp_1(self):
        self.assertEqual(cmp(IPv6Addr(128), IPv4Addr(128)), -1)

    def test_v4_v6_cmp_2(self):
        self.assertEqual(cmp(IPv6Addr("::1.2.3.4"),
                             IPv4Addr("1.2.3.4")), -1)

    def test_v4_v6_cmp_3(self):
        self.assertEqual(cmp(IPv6Addr("::ffff:1.2.3.4"),
                             IPv4Addr("1.2.3.4")), 0)

    def test_ip_is_ipv6_1(self):
        self.assertTrue(IPAddr("::ffff:1.2.3.4").is_ipv6())

    def test_ip_is_ipv6_2(self):
        self.assertTrue(IPAddr("::1.2.3.4").is_ipv6())

    def test_ip_is_ipv6_3(self):
        self.assertTrue(IPAddr("2000::cdef").is_ipv6())

    def test_ip_is_ipv6_4(self):
        self.assertFalse(IPAddr("1.2.3.4").is_ipv6())

    def test_v4_octets(self):
        self.assertEqual(IPv4Addr("1.2.3.4").octets(), (1, 2, 3, 4))

    def test_v6_octets(self):
        self.assertEqual(
            IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").octets(),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0))

    def test_v4_mask_1(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask(IPv4Addr("255.255.0.0")),
            IPv4Addr("1.2.0.0"))

    def test_v4_mask_2(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask(IPv4Addr("0.0.255.255")),
            IPv4Addr("0.0.3.4"))

    def test_v4_mask_3(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask(IPv4Addr("0.255.255.0")),
            IPv4Addr("0.2.3.0"))

    def test_v6_mask_1(self):
        self.assertEqual(
            IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask(
                IPv6Addr("ffff:ffff:ffff:ffff::")),
            IPv6Addr("0102:0304:0506:0708::"))

    def test_v6_mask_2(self):
        self.assertEqual(
            IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask(
                IPv6Addr("::ffff:ffff:ffff:ffff")),
            IPv6Addr("::090a:0b0c:0d0e:0f00"))

    def test_v6_mask_3(self):
        self.assertEqual(
            IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask(
                IPv6Addr("ffff:ffff::ffff:ffff")),
            IPv6Addr("0102:0304::0d0e:0f00"))

    def test_v4_v6_mask_1(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask(IPv6Addr('::ffff:255.255.0.0')),
            IPv4Addr("1.2.0.0"))

    def test_v4_v6_mask_2(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask(IPv6Addr('::255.255.0.0')),
            IPv4Addr("1.2.0.0"))

    def test_v4_v6_mask_3(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask(IPv6Addr('::abcd:ef12:255.255.0.0')),
            IPv4Addr("1.2.0.0"))

    def test_v6_v4_mask_1(self):
        self.assertEqual(
            IPv6Addr("::ffff:1.2.3.4").mask(IPv4Addr("255.255.0.0")),
            IPv6Addr("::ffff:1.2.0.0"))

    def test_v6_v4_mask_2(self):
        self.assertEqual(
            IPv6Addr("::abcd:ef12:1.2.3.4").mask(IPv4Addr("255.255.0.0")),
            IPv6Addr("::ef12:1.2.0.0"))

    def test_v4_mask_prefix_1(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask_prefix(8),
            IPv4Addr("1.0.0.0"))

    def test_v4_mask_prefix_2(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask_prefix(16),
            IPv4Addr("1.2.0.0"))

    def test_v4_mask_prefix_3(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask_prefix(24),
            IPv4Addr("1.2.3.0"))

    def test_v4_mask_prefix_4(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask_prefix(32),
            IPv4Addr("1.2.3.4"))

    def test_v4_mask_prefix_5(self):
        self.assertEqual(
            IPv4Addr("1.2.3.4").mask_prefix(0),
            IPv4Addr("0.0.0.0"))

    def test_v6_mask_prefix_1(self):
        self.assertEqual(
          IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask_prefix(32),
          IPv6Addr("0102:0304::"))

    def test_v6_mask_prefix_2(self):
        self.assertEqual(
          IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask_prefix(64),
          IPv6Addr("0102:0304:0506:0708::"))

    def test_v6_mask_prefix_3(self):
        self.assertEqual(
          IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask_prefix(96),
          IPv6Addr("0102:0304:0506:0708:090a:0b0c::"))

    def test_v6_mask_prefix_4(self):
        self.assertEqual(
          IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask_prefix(128),
          IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00"))

    def test_v6_mask_prefix_5(self):
        self.assertEqual(
          IPv6Addr("0102:0304:0506:0708:090a:0b0c:0d0e:0f00").mask_prefix(0),
          IPv6Addr("::"))

    def test_silk_IPAddrConstruction(self):
        a = IPAddr("0.0.0.0")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("0.0.0.0")
        self.assertEqual(a, b)
        a = IPAddr("255.255.255.255")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("255.255.255.255")
        self.assertEqual(a, b)
        a = IPAddr("10.0.0.0")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("10.0.0.0")
        self.assertEqual(a, b)
        a = IPAddr("10.10.10.10")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("10.10.10.10")
        self.assertEqual(a, b)
        a = IPAddr("10.11.12.13")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("10.11.12.13")
        self.assertEqual(a, b)
        a = IPAddr(" 10.0.0.0")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr(" 10.0.0.0")
        self.assertEqual(a, b)
        a = IPAddr("10.0.0.0 ")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("10.0.0.0 ")
        self.assertEqual(a, b)
        a = IPAddr("  10.0.0.0  ")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("  10.0.0.0  ")
        self.assertEqual(a, b)
        a = IPAddr("010.000.000.000")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("010.000.000.000")
        self.assertEqual(a, b)
        a = IPAddr("4294967295")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("4294967295")
        self.assertEqual(a, b)
        a = IPAddr("167772160")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("167772160")
        self.assertEqual(a, b)
        a = IPAddr("168430090")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("168430090")
        self.assertEqual(a, b)
        a = IPAddr("168496141")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("168496141")
        self.assertEqual(a, b)
        a = IPAddr("167772160")
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr("167772160")
        self.assertEqual(a, b)
        a = IPAddr(IPAddr("0.0.0.0"))
        self.assertEqual(type(a), IPv4Addr)
        b = IPv4Addr(IPAddr("0.0.0.0"))
        self.assertEqual(a, b)
        if ipv6_enabled():
            a = IPAddr("0:0:0:0:0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")
            self.assertEqual(a, b)
            a = IPAddr("10:0:0:0:0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("10:0:0:0:0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("10:10:10:10:10:10:10:10")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("10:10:10:10:10:10:10:10")
            self.assertEqual(a, b)
            a = IPAddr("1010:1010:1010:1010:1010:1010:1010:1010")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("1010:1010:1010:1010:1010:1010:1010:1010")
            self.assertEqual(a, b)
            a = IPAddr("1011:1213:1415:1617:2021:2223:2425:2627")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("1011:1213:1415:1617:2021:2223:2425:2627")
            self.assertEqual(a, b)
            a = IPAddr("f0ff:f2f3:f4f5:f6f7:202f:2223:2425:2627")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("f0ff:f2f3:f4f5:f6f7:202f:2223:2425:2627")
            self.assertEqual(a, b)
            a = IPAddr("f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")
            self.assertEqual(a, b)
            a = IPAddr("     f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("     f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")
            self.assertEqual(a, b)
            a = IPAddr("f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7     ")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7     ")
            self.assertEqual(a, b)
            a = IPAddr("   f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7  ")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("   f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7  ")
            self.assertEqual(a, b)
            a = IPAddr("::")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::")
            self.assertEqual(a, b)
            a = IPAddr("0::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0")
            self.assertEqual(a, b)
            a = IPAddr("0:0::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0::0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0::0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0::0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0::0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0:0::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0:0::0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0::0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0::0:0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0::0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0::0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0::0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0::0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0:0::0:0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0::0:0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0::0:0:0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0:0:0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0::0:0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0:0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0::0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0::0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0::0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0:0")
            self.assertEqual(a, b)
            a = IPAddr("::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0:0:0:0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0:0:0:0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0:0:0::")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0:0:0::")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0:0::0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0:0::0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0::")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0::")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0::")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0::")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0::")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0::")
            self.assertEqual(a, b)
            a = IPAddr("0:0::")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0::")
            self.assertEqual(a, b)
            a = IPAddr("0::")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0::0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0::0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0::0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0::0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0::0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0::0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0::0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0::0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0::0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("::0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("::0:0:0:0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("::0:0:0:0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0::0:0:0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0::0:0:0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0::0:0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0::0:0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0::0:0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0::0:0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0::0:0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0::0:0.0.0.0")
            self.assertEqual(a, b)
            a = IPAddr("0:0:0:0:0::0.0.0.0")
            self.assertEqual(type(a), IPv6Addr)
            b = IPv6Addr("0:0:0:0:0::0.0.0.0")
            self.assertEqual(a, b)
        else:
            self.assertRaises(NotImplementedError, IPAddr, '::')
            self.assertRaises(NotImplementedError, IPv6Addr, '::')
        
    def test_silk_IPAddrString(self):
        self.assertEqual(str(IPAddr("0.0.0.0")), "0.0.0.0")
        self.assertEqual(str(IPAddr("255.255.255.255")), "255.255.255.255")
        self.assertEqual(str(IPAddr("10.0.0.0")), "10.0.0.0")
        self.assertEqual(str(IPAddr("10.10.10.10")), "10.10.10.10")
        self.assertEqual(str(IPAddr("10.11.12.13")), "10.11.12.13")
        self.assertEqual(IPAddr("0.0.0.0").padded(), "000.000.000.000")
        self.assertEqual(IPAddr("255.255.255.255").padded(), "255.255.255.255")
        self.assertEqual(IPAddr("10.0.0.0").padded(), "010.000.000.000")
        self.assertEqual(IPAddr("10.10.10.10").padded(), "010.010.010.010")
        self.assertEqual(IPAddr("10.11.12.13").padded(), "010.011.012.013")
        if ipv6_enabled():
            self.assertEqual(str(IPAddr("0:0:0:0:0:0:0:0")), "::")
            self.assertEqual(
                str(IPAddr("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")),
                "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")
            self.assertEqual(str(IPAddr("10:0:0:0:0:0:0:0")), "10::")
            self.assertEqual(str(IPAddr("10:10:10:10:10:10:10:10")),
                             "10:10:10:10:10:10:10:10")
            self.assertEqual(
                    str(IPAddr("1010:1010:1010:1010:1010:1010:1010:1010")),
                    "1010:1010:1010:1010:1010:1010:1010:1010")
            self.assertEqual(
                str(IPAddr("1011:1213:1415:1617:2021:2223:2425:2627")),
                "1011:1213:1415:1617:2021:2223:2425:2627")
            self.assertEqual(
                str(IPAddr("f0ff:f2f3:f4f5:f6f7:202f:2223:2425:2627")),
                "f0ff:f2f3:f4f5:f6f7:202f:2223:2425:2627")
            self.assertEqual(
                str(IPAddr("f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")),
                "f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")
            self.assertEqual(str(IPAddr("1234::5678")), "1234::5678")
            self.assertEqual(IPAddr("0:0:0:0:0:0:0:0").padded(),
                             "0000:0000:0000:0000:0000:0000:0000:0000")
            self.assertEqual(
                IPAddr("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff").padded(),
                "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")
            self.assertEqual(IPAddr("10:0:0:0:0:0:0:0").padded(),
                             "0010:0000:0000:0000:0000:0000:0000:0000")
            self.assertEqual(IPAddr("10:10:10:10:10:10:10:10").padded(),
                             "0010:0010:0010:0010:0010:0010:0010:0010")
            self.assertEqual(
                IPAddr("1010:1010:1010:1010:1010:1010:1010:1010").padded(),
                    "1010:1010:1010:1010:1010:1010:1010:1010")
            self.assertEqual(
                IPAddr("1011:1213:1415:1617:2021:2223:2425:2627").padded(),
                "1011:1213:1415:1617:2021:2223:2425:2627")
            self.assertEqual(
                IPAddr("f0ff:f2f3:f4f5:f6f7:202f:2223:2425:2627").padded(),
                "f0ff:f2f3:f4f5:f6f7:202f:2223:2425:2627")
            self.assertEqual(
                IPAddr("f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7").padded(),
                "f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")
            self.assertEqual(IPAddr("1234::5678").padded(),
                             "1234:0000:0000:0000:0000:0000:0000:5678")

    def test_silk_IPAddrInt(self):
        self.assertEqual(int(IPAddr("0.0.0.0")), 0)
        self.assertEqual(int(IPAddr("255.255.255.255")), 4294967295)
        self.assertEqual(int(IPAddr("10.0.0.0")), 167772160)
        self.assertEqual(int(IPAddr("10.10.10.10")), 168430090)
        self.assertEqual(int(IPAddr("10.11.12.13")), 168496141)
        self.assertEqual(int(IPAddr(" 10.0.0.0")), 167772160)
        self.assertEqual(int(IPAddr("10.0.0.0 ")), 167772160)
        self.assertEqual(int(IPAddr("  10.0.0.0  ")), 167772160)
        self.assertEqual(int(IPAddr("010.000.000.000")), 167772160)
        self.assertEqual(int(IPAddr("4294967295")), 4294967295)
        self.assertEqual(int(IPAddr("167772160")), 167772160)
        self.assertEqual(int(IPAddr("168430090")), 168430090)
        self.assertEqual(int(IPAddr("168496141")), 168496141)
        self.assertEqual(int(IPAddr("167772160")), 167772160)
        if ipv6_enabled():
            self.assertEqual(int(IPAddr("0:0:0:0:0:0:0:0")), 0)
            self.assertEqual(int(IPAddr(
                        "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")),
                             0xffffffffffffffffffffffffffffffff)
            self.assertEqual(int(IPAddr("10:0:0:0:0:0:0:0")),
                             0x00100000000000000000000000000000)
            self.assertEqual(int(IPAddr("10:10:10:10:10:10:10:10")),
                             0x00100010001000100010001000100010)
            self.assertEqual(int(IPAddr(
                        "1010:1010:1010:1010:1010:1010:1010:1010")),
                             0x10101010101010101010101010101010)
            self.assertEqual(int(IPAddr(
                        "1011:1213:1415:1617:2021:2223:2425:2627")),
                             0x10111213141516172021222324252627)
            self.assertEqual(int(IPAddr(
                        "f0ff:f2f3:f4f5:f6f7:202f:2223:2425:2627")),
                             0xf0fff2f3f4f5f6f7202f222324252627)
            self.assertEqual(int(IPAddr(
                        "f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7")),
                             0xf0fffaf3f4f5f6f7a0afaaa3a4a5a6a7)
            self.assertEqual(int(IPAddr("::")), 0)
            self.assertEqual(int(IPAddr("0::0")), 0)
            self.assertEqual(int(IPAddr("0:0::0")), 0)
            self.assertEqual(int(IPAddr("0:0:0::0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0::0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0::0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0:0::0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0::0:0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0::0:0:0")), 0)
            self.assertEqual(int(IPAddr("0:0:0::0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("0:0::0:0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("0::0:0:0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("0::0:0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("0::0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("0::0:0:0")), 0)
            self.assertEqual(int(IPAddr("0::0:0")), 0)
            self.assertEqual(int(IPAddr("::0")), 0)
            self.assertEqual(int(IPAddr("::0:0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0:0:0:0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0:0:0::")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0:0::0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0::")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0::")), 0)
            self.assertEqual(int(IPAddr("0:0:0::")), 0)
            self.assertEqual(int(IPAddr("0:0::")), 0)
            self.assertEqual(int(IPAddr("0::")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0::0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0::0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0:0::0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0::0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0::0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("::0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("::0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("::0:0:0:0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0::0:0:0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0::0:0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0:0::0:0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0::0:0.0.0.0")), 0)
            self.assertEqual(int(IPAddr("0:0:0:0:0::0.0.0.0")), 0)
            self.assertEqual(int(IPAddr(
                        "ffff:ffff:ffff:ffff:ffff:ffff:255.255.255.255")),
                             0xffffffffffffffffffffffffffffffff)
            self.assertEqual(int(IPAddr(
                        "1010:1010:1010:1010:1010:1010:16.16.16.16")),
                             0x10101010101010101010101010101010)
            self.assertEqual(int(IPAddr(
                        "1011:1213:1415:1617:2021:2223:36.37.38.39")),
                             0x10111213141516172021222324252627)

    def test_silk_IPAddrFromInt(self):
        self.assertEqual(int(IPv4Addr(0)), 0)
        self.assertEqual(int(IPv4Addr(4294967295)), 4294967295)
        self.assertEqual(int(IPv4Addr(167772160)), 167772160)
        self.assertEqual(int(IPv4Addr(168430090)), 168430090)
        self.assertEqual(int(IPv4Addr(168496141)), 168496141)
        self.assertEqual(int(IPv4Addr(167772160)), 167772160)
        self.assertRaises(ValueError, IPv4Addr, -1)
        self.assertRaises(ValueError, IPv4Addr, 0x100000000)
        if ipv6_enabled():
            self.assertEqual(int(IPv6Addr(0xffffffffffffffffffffffffffffffff)),
                             0xffffffffffffffffffffffffffffffff)
            self.assertEqual(int(IPv6Addr(0x10101010101010101010101010101010)),
                             0x10101010101010101010101010101010)
            self.assertEqual(int(IPv6Addr(0x10111213141516172021222324252627)),
                             0x10111213141516172021222324252627)
            self.assertRaises(ValueError, IPv6Addr, -1)
            self.assertRaises(ValueError, IPv6Addr,
                              0x100000000000000000000000000000000)
        else:
            self.assertRaises(NotImplementedError, IPv6Addr, 0)

    def test_silk_IPAddrBadStrings(self):
        if ipv6_enabled():
            badipv6 = ValueError
        else:
            badipv6 = NotImplementedError
        self.assertRaises(ValueError, IPAddr, "010.000.000.000x")
        self.assertRaises(ValueError, IPAddr, "010.000.000.000a")
        self.assertRaises(ValueError, IPAddr, "010.000.000.000|")
        self.assertRaises(badipv6, IPAddr, "       10.0.0.0:80")
        self.assertRaises(ValueError, IPAddr, "10.0.0.0       .")
        self.assertRaises(ValueError, IPAddr, "      167772160|")
        self.assertRaises(ValueError, IPAddr, "    10.10.10.10.10  ")
        self.assertRaises(ValueError, IPAddr, "")
        self.assertRaises(ValueError, IPAddr, "  ")
        self.assertRaises(ValueError, IPAddr, "     -167772160")
        self.assertRaises(ValueError, IPAddr, "     -167772160|")
        self.assertRaises(ValueError, IPAddr, "      167772160.")
        self.assertRaises(ValueError, IPAddr, " 256.256.256.256")
        self.assertRaises(ValueError, IPAddr, "  10.")
        self.assertRaises(ValueError, IPAddr, "  10.x.x.x  ")
        self.assertRaises(ValueError, IPAddr, "  .10.10.10.10  ")
        self.assertRaises(ValueError, IPAddr, "  10..10.10.10  ")
        self.assertRaises(ValueError, IPAddr, "  10.10..10.10  ")
        self.assertRaises(ValueError, IPAddr, "  10.10.10..10  ")
        self.assertRaises(ValueError, IPAddr, "  10.10.10.10.  ")
        self.assertRaises(badipv6, IPAddr, "  10.10:10.10   ")
        self.assertRaises(ValueError, IPAddr,
                          "10.0.0.98752938745983475983475039248759")
        self.assertRaises(ValueError, IPAddr, "10.0|0.0")
        self.assertRaises(ValueError, IPAddr, " 10.  0.  0.  0")
        self.assertRaises(ValueError, IPAddr, "10 .   0.  0.  0")
        self.assertRaises(badipv6, IPAddr, " -10:0:0:0:0:0:0:0")
        self.assertRaises(badipv6, IPAddr, " 10000:0:0:0:0:0:0:0")
        self.assertRaises(badipv6, IPAddr, " 0:0:0:0:0:0:0:10000")
        self.assertRaises(badipv6, IPAddr, "  10:")
        self.assertRaises(badipv6, IPAddr, "0:0:0:0:0:0:0")
        self.assertRaises(badipv6, IPAddr, "  10:10.10:10::")
        self.assertRaises(badipv6, IPAddr, "  :10:10:10:10::")
        self.assertRaises(badipv6, IPAddr, "  ::10:10:10:10:STUFF")
        self.assertRaises(badipv6, IPAddr, "  ::10:10:10:10:")
        self.assertRaises(badipv6, IPAddr, "  10:10:10:::10")
        self.assertRaises(badipv6, IPAddr, "  10::10:10::10")
        self.assertRaises(badipv6, IPAddr, "  10:10::10::10")
        self.assertRaises(badipv6, IPAddr, "  10::10::10:10")
        self.assertRaises(badipv6, IPAddr, "  10:x:x:x:x:x:x:x  ")
        self.assertRaises(badipv6, IPAddr,
                          "f0ff:faf3:f4f5:f6f7:a0af:aaa3:a4a5:a6a7:ffff")
        self.assertRaises(badipv6, IPAddr,
                          ("11:12:13:14:15:16:17:"
                           "98752938745983475983475039248759"))
        self.assertRaises(badipv6, IPAddr, "10:0|0:0:0:0:0:0")
        self.assertRaises(badipv6, IPAddr,
                          " 10:  0:  0:  0: 10: 10: 10: 10")
        self.assertRaises(badipv6, IPAddr, "10 :10:10:10:10:10:10:10")
        self.assertRaises(badipv6, IPAddr, ":10:10:10:10:10:10:10:10")
        self.assertRaises(badipv6, IPAddr, "0:0:0:0:0:0:0:0:0.0.0.0")
        self.assertRaises(badipv6, IPAddr, "0:0:0:0:0:0:0:0.0.0.0")
        self.assertRaises(badipv6, IPAddr, "::0.0.0.0:0")
        self.assertRaises(badipv6, IPAddr, "0::0.0.0.0:0")
        self.assertRaises(badipv6, IPAddr, "0::0.0.0.0.0")
        self.assertRaises(ValueError, IPv4Addr, "::")
        if ipv6_enabled():
            self.assertRaises(ValueError, IPv6Addr, "0.0.0.0")
        else:
            self.assertRaises(NotImplementedError, IPv6Addr, "0.0.0.0")


    def test_silk_IPAddrBadTypes(self):
        self.assertRaises(TypeError, IPAddr, 2.4)

    def test_silk_IPAddrOrdering(self):
        self.assert_(IPv4Addr(0) == IPv4Addr(IPv4Addr(0)))
        self.assert_(IPv4Addr(0) <  IPv4Addr(256))
        self.assert_(IPv4Addr(256) >  IPv4Addr(0))
        self.assert_(IPv4Addr(256) != IPv4Addr(0))
        self.assert_(IPv4Addr(0xffffffff) == IPv4Addr(0xffffffff))
        if ipv6_enabled():
            self.assert_(IPv6Addr(0xffffffff) < IPAddr("ffff::"))
            self.assert_(IPv6Addr(0xffffffff) != IPAddr("255.255.255.255"))
            self.assert_(IPAddr("255.255.255.255") >
                         IPAddr("::255.255.255.255"))
            self.assert_(IPAddr("0.0.0.0") == IPAddr("::ffff:0.0.0.0"))
            self.assert_(IPAddr("0.0.0.0") < IPAddr("::ffff:0.0.0.1"))

    def test_silk_IPAddrIPv6(self):
        if ipv6_enabled():
            self.assert_(IPAddr("::").is_ipv6())
            self.assert_(IPAddr("::ffff:0.0.0.1").is_ipv6())
        self.assert_(not IPAddr("0.0.0.0").is_ipv6())
        self.assert_(not IPAddr("0.0.0.1").is_ipv6())

    def test_silk_IPAddrConvert(self):
        a = IPAddr("0.0.0.0")
        self.assertEqual(a, IPv4Addr(a))
        self.assertEqual(a, a.to_ipv4())
        if ipv6_enabled():
            b = IPAddr("::")
            c = IPAddr("::ffff:0.0.0.0")
            self.assertEqual(b, IPv6Addr(b))
            self.assertEqual(c, IPv6Addr(c))
            self.assertEqual(c, IPv6Addr(a))
            self.assertEqual(c, a.to_ipv6())
            self.assertEqual(a, IPv4Addr(c))
            self.assertEqual(a, c.to_ipv6())
            self.assertRaises(ValueError, IPv4Addr, b)
            self.assertEqual(None, b.to_ipv4())
        else:
            self.assertRaises(NotImplementedError, a.to_ipv6)
            self.assertRaises(NotImplementedError, IPv6Addr, a)

    def test_silk_IPAddrOctets(self):
        a = IPAddr("10.11.12.13")
        self.assertEqual(a.octets(), (10, 11, 12, 13))
        if ipv6_enabled():
            a = IPAddr("2001:db8:10:11::12:13")
            self.assertEqual(a.octets(), (0x20, 0x01, 0x0d, 0xb8,
                                          0x00, 0x10, 0x00, 0x11,
                                          0x00, 0x00, 0x00, 0x00,
                                          0x00, 0x12, 0x00, 0x13))

    def test_silk_IPAddrMasking(self):
        a = IPAddr("10.11.12.13")
        self.assertEqual(a, a.mask_prefix(32))
        self.assertEqual(IPAddr("0.0.0.0"), a.mask_prefix(0))
        self.assertRaises(ValueError, a.mask_prefix, 33)
        b = IPAddr("0.0.0.0")
        self.assertEqual(b, a.mask(b))
        self.assertEqual(b, b.mask(a))
        self.assertEqual(b, b.mask(b))
        b = IPAddr("255.255.255.0")
        c = IPAddr("10.11.12.0")
        self.assertEqual(c, a.mask(b))
        self.assertEqual(c, a.mask_prefix(24))
        self.assertEqual(c, c.mask(b))
        self.assertEqual(c, c.mask_prefix(24))
        b = IPAddr("255.255.0.0")
        c = IPAddr("10.11.0.0")
        self.assertEqual(c, a.mask(b))
        self.assertEqual(c, a.mask_prefix(16))
        self.assertEqual(c, c.mask(b))
        self.assertEqual(c, c.mask_prefix(16))
        if ipv6_enabled():
            a = IPAddr("2001:db8:10:11::12:13")
            self.assertEqual(a, a.mask_prefix(128))
            self.assertEqual(IPAddr("::"), a.mask_prefix(0))
            self.assertRaises(ValueError, a.mask_prefix, 129)
            b = IPAddr("::")
            self.assertEqual(b, a.mask(b))
            self.assertEqual(b, b.mask(a))
            self.assertEqual(b, b.mask(b))
            b = IPAddr("ffff:ffff:ffff:ffff:ffff:ffff:ffff:0")
            c = IPAddr("2001:db8:10:11::12:0")
            self.assertEqual(c, a.mask(b))
            self.assertEqual(c, a.mask_prefix(112))
            self.assertEqual(c, c.mask(b))
            self.assertEqual(c, c.mask_prefix(112))
            b = IPAddr("ffff:ffff:ffff:ffff::")
            c = IPAddr("2001:db8:10:11::")
            self.assertEqual(c, a.mask(b))
            self.assertEqual(c, a.mask_prefix(64))
            self.assertEqual(c, c.mask(b))
            self.assertEqual(c, c.mask_prefix(64))
            # Mixed IPv4 and IPv6
            a = IPAddr("::FFFF:10.11.12.13")
            self.assertEqual(a, a.mask_prefix(128))
            b = IPAddr("::FFFF:0.0.0.0")
            self.assertEqual(b, a.mask(b))
            self.assertEqual(b, b.mask(a))
            self.assertEqual(b, b.mask(b))
            b = IPAddr("255.255.255.0")
            c = IPAddr("::FFFF:10.11.12.0")
            self.assertEqual(c, a.mask(b))
            self.assertEqual(c, a.mask_prefix(120))
            self.assertEqual(c, c.mask(b))
            self.assertEqual(c, c.mask_prefix(120))
            b = IPAddr("255.255.0.0")
            c = IPAddr("::FFFF:10.11.0.0")
            self.assertEqual(c, a.mask(b))
            self.assertEqual(c, a.mask_prefix(112))
            self.assertEqual(c, c.mask(b))
            self.assertEqual(c, c.mask_prefix(112))
