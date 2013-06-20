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
import sys

def op_iand(x, y): x &= y; return x
def op_ior(x, y): x |= y; return x
def op_isub(x, y): x -= y; return x
def op_ixor(x, y): x ^= y; return x

import netsa._netsa_silk
from netsa._netsa_silk import IPAddr, IPv4Addr, IPv6Addr, ip_set, IPWildcard

def ipv6_enabled():
    return True

IPSet = ip_set

class IPSetTest(unittest.TestCase):

    def test_cons_1(self):
        self.assertEqual(ip_set(), ip_set())

    def test_cons_2(self):
        self.assertEqual(ip_set([]), ip_set())

    def test_cons_7(self):
        self.assertEqual(ip_set(['1.2.3.4']), ip_set([IPv4Addr('1.2.3.4')]))

    def test_cons_3(self):
        self.assertEqual(ip_set(('1.2.3.4',)), ip_set([IPv4Addr('1.2.3.4')]))

    def test_cons_4(self):
        self.assertEqual(ip_set(set(['1.2.3.4'])),
                         ip_set([IPv4Addr('1.2.3.4')]))

    def test_cons_5(self):
        self.assertRaises(TypeError, ip_set, set([1]))

    def test_cons_6(self):
        self.assertEqual(ip_set([IPWildcard('128.2.1.0-5'),
                                 IPWildcard('128.2.1.2-10')]),
                         ip_set(['128.2.1.0', '128.2.1.1', '128.2.1.2',
                                 '128.2.1.3', '128.2.1.4', '128.2.1.5',
                                 '128.2.1.6', '128.2.1.7', '128.2.1.8',
                                 '128.2.1.9', '128.2.1.10']))

    def test_len_1(self):
        self.assertEqual(len(ip_set()), 0)

    def test_len_2(self):
        self.assertEqual(len(ip_set(["1.2.3.4", "5.6.7.8"])), 2)

    def test_cardinality_1(self):
        self.assertEqual(ip_set().cardinality(), 0)

    def test_cardinality_2(self):
        self.assertEqual(ip_set(['1.2.3.4', '5.6.7.8']).cardinality(), 2)

    def test_in_1(self):
        self.assertTrue(IPAddr('1.2.3.4') in ip_set([IPAddr('1.2.3.4')]))

    def test_in_2(self):
        self.assertTrue(IPAddr('1.2.3.4') in ip_set(['1.2.3.4']))

    def test_in_3(self):
        self.assertTrue('1.2.3.4' in ip_set(['1.2.3.4']))

    def test_in_4(self):
        self.assertRaises(TypeError, operator.contains, ip_set(['1.2.3.4']), 1)

    def test_eq_1(self):
        self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8']) ==
                        ip_set(['5.6.7.8', '1.2.3.4']))

    def test_eq_2(self):
        self.assertFalse(ip_set(['2.3.4.5', '5.6.7.8']) ==
                         ip_set(['1.2.3.4', '5.6.7.8']))

    def test_eq_3(self):
        self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8']) ==
                         set(['5.6.7.8', '1.2.3.4']))

    def test_eq_4(self):
        self.assertFalse(ip_set(['2.3.4.5', '5.6.7.8']) ==
                         set(['1.2.3.4', '5.6.7.8']))

    def test_ne_1(self):
        self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8']) !=
                         ip_set(['5.6.7.8', '1.2.3.4']))

    def test_ne_2(self):
        self.assertTrue(ip_set(['2.3.4.5', '5.6.7.8']) !=
                        ip_set(['1.2.3.4', '5.6.7.8']))

    def test_ne_3(self):
        self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8']) !=
                        set(['5.6.7.8', '1.2.3.4']))

    def test_ne_4(self):
        self.assertTrue(ip_set(['2.3.4.5', '5.6.7.8']) !=
                        set(['1.2.3.4', '5.6.7.8']))

    def test_isdisjoint_1(self):
        if sys.version_info >= (2, 6):
            self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8'])
                            .isdisjoint(ip_set(['2.3.4.5', '6.7.8.9'])))

    def test_isdisjoint_2(self):
        if sys.version_info >= (2, 6):
            self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8'])
                             .isdisjoint(ip_set(['1.2.3.4', '6.7.8.9'])))

    def test_isdisjoint_3(self):
        if sys.version_info >= (2, 6):
            self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8'])
                            .isdisjoint(['2.3.4.5', '6.7.8.9']))

    def test_isdisjoint_4(self):
        if sys.version_info >= (2, 6):
            self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8'])
                            .isdisjoint(['1.2.3.4', '6.7.8.9']))

    def test_isdisjoint_5(self):
        if sys.version_info >= (2, 6):
            self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8'])
                            .isdisjoint([IPWildcard('0.0.0.0'),
                                         IPWildcard('2.0.0.x')]))

    def test_issubset_1(self):
        self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8'])
                        .issubset(frozenset([IPAddr('5.6.7.8'),
                                             IPAddr('1.2.3.4')])))

    def test_issubset_2(self):
        self.assertTrue(ip_set(['5.6.7.8'])
                        .issubset(set(['5.6.7.8', '1.2.3.4'])))

    def test_issubset_3(self):
        self.assertTrue(ip_set()
                        .issubset(['5.6.7.8', '1.2.3.4']))

    def test_issubset_4(self):
        self.assertFalse(ip_set(['5.6.7.8', '2.3.4.5'])
                         .issubset(('5.6.7.8', '1.2.3.4')))

    def test_issubset_5(self):
        self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8'])
                         .issubset([IPWildcard('0.0.0.0'),
                                    IPWildcard('2.0.0.x')]))

    def test_le_1(self):
        self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8']) <=
                        ip_set(['5.6.7.8', '1.2.3.4']))

    def test_le_2(self):
        self.assertRaises(TypeError, operator.le,
                          ip_set(['5.6.7.8']), set(['5.6.7.8', '1.2.3.4']))

    def test_le_3(self):
        self.assertTrue(ip_set() <=
                        ip_set(['5.6.7.8', '1.2.3.4']))

    def test_le_4(self):
        self.assertFalse(ip_set(['5.6.7.8', '2.3.4.5']) <=
                         ip_set(['5.6.7.8', '1.2.3.4']))

    def test_le_5(self):
        self.assertRaises(TypeError, operator.le,
                          ip_set(['1.2.3.4', '5.6.7.8']),
                          [IPWildcard('0.0.0.0'),
                           IPWildcard('2.0.0.x')])

    def test_lt_1(self):
        self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8']) <
                        ip_set(['5.6.7.8', '1.2.3.4']))

    def test_lt_2(self):
        self.assertRaises(TypeError, operator.lt,
                          ip_set(['5.6.7.8']), set(['5.6.7.8', '1.2.3.4']))

    def test_lt_3(self):
        self.assertTrue(ip_set() <
                        ip_set(['5.6.7.8', '1.2.3.4']))

    def test_lt_4(self):
        self.assertFalse(ip_set(['5.6.7.8', '2.3.4.5']) <
                         ip_set(['5.6.7.8', '1.2.3.4']))

    def test_lt_5(self):
        self.assertRaises(TypeError, operator.lt,
                          ip_set(['1.2.3.4', '5.6.7.8']),
                          [IPWildcard('0.0.0.0'),
                           IPWildcard('2.0.0.x')])

    def test_issuperset_1(self):
        self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8'])
                        .issuperset(frozenset([IPAddr('5.6.7.8'),
                                               IPAddr('1.2.3.4')])))

    def test_issuperset_2(self):
        self.assertTrue(ip_set(['5.6.7.8', '1.2.3.4'])
                        .issuperset(set(['5.6.7.8'])))

    def test_issuperset_3(self):
        self.assertTrue(ip_set(['5.6.7.8', '1.2.3.4'])
                        .issuperset([]))

    def test_issuperset_4(self):
        self.assertFalse(ip_set(['5.6.7.8', '2.3.4.5'])
                         .issuperset(('5.6.7.8', '1.2.3.4')))

    def test_issuperset_5(self):
        self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8'])
                         .issuperset([IPWildcard('0.0.0.0'),
                                      IPWildcard('2.0.0.x')]))

    def test_ge_1(self):
        self.assertTrue(ip_set(['1.2.3.4', '5.6.7.8']) >=
                        ip_set(['5.6.7.8', '1.2.3.4']))

    def test_ge_2(self):
        self.assertRaises(TypeError, operator.ge,
                          ip_set(['5.6.7.8', '1.2.3.4']), set(['5.6.7.8']))

    def test_ge_3(self):
        self.assertTrue(ip_set(['5.6.7.8', '1.2.3.4']) >=
                        ip_set())

    def test_ge_4(self):
        self.assertFalse(ip_set(['5.6.7.8', '2.3.4.5']) >=
                         ip_set(['5.6.7.8', '1.2.3.4']))

    def test_ge_5(self):
        self.assertRaises(TypeError, operator.ge,
                          ip_set(['1.2.3.4', '5.6.7.8']),
                          [IPWildcard('0.0.0.0'),
                           IPWildcard('2.0.0.x')])

    def test_gt_1(self):
        self.assertFalse(ip_set(['1.2.3.4', '5.6.7.8']) >
                         ip_set(['5.6.7.8', '1.2.3.4']))

    def test_gt_2(self):
        self.assertRaises(TypeError, operator.gt,
                          ip_set(['5.6.7.8', '1.2.3.4']), set(['5.6.7.8']))

    def test_gt_3(self):
        self.assertTrue(ip_set(['5.6.7.8', '1.2.3.4']) >
                        ip_set())

    def test_gt_4(self):
        self.assertFalse(ip_set(['5.6.7.8', '2.3.4.5']) >
                         ip_set(['5.6.7.8', '1.2.3.4']))

    def test_gt_5(self):
        self.assertRaises(TypeError, operator.gt,
                          ip_set(['1.2.3.4', '5.6.7.8']),
                          [IPWildcard('0.0.0.0'),
                           IPWildcard('2.0.0.x')])

    def test_union_1(self):
        self.assertEqual(ip_set(['1.2.3.4']).union(
                             ip_set(['1.2.3.4', '5.6.7.8'])),
                         ip_set(['1.2.3.4', '5.6.7.8']))

    def test_union_2(self):
        self.assertEqual(ip_set(['1.2.3.4']).union(
                             set(['1.2.3.4', '5.6.7.8'])),
                         ip_set(['1.2.3.4', '5.6.7.8']))

    def test_union_3(self):
        self.assertEqual(ip_set(['1.2.3.4']).union(['1.2.3.4', '5.6.7.8']),
                         ip_set(['1.2.3.4', '5.6.7.8']))

    def test_union_4(self):
        self.assertTrue(ip_set(['1.2.3.4']).union([IPWildcard('5.6.7.8')]),
                         ip_set(['1.2.3.4', '5.6.7.8']))

    def test_union_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4']).union(ip_set())),
                         [IPAddr('1.2.3.4')])

    def test_or_1(self):
        self.assertEqual(ip_set(['1.2.3.4']) | ip_set(['1.2.3.4', '5.6.7.8']),
                         ip_set(['1.2.3.4', '5.6.7.8']))

    def test_or_2(self):
        self.assertRaises(TypeError, operator.or_,
                          ip_set(['1.2.3.4']), set(['1.2.3.4', '5.6.7.8']))

    def test_or_3(self):
        self.assertRaises(TypeError, operator.or_,
                          ip_set(['1.2.3.4']), (['1.2.3.4', '5.6.7.8']))

    def test_or_4(self):
        self.assertRaises(TypeError, operator.or_,
                          ip_set(['1.2.3.4']), ([IPWildcard('5.6.7.8')]))

    def test_or_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4']) | ip_set()),
                         [IPAddr('1.2.3.4')])

    def test_intersection_1(self):
        self.assertEqual(ip_set(['1.2.3.4']).intersection(
                             ip_set(['1.2.3.4', '5.6.7.8'])),
                         ip_set(['1.2.3.4']))

    def test_intersection_2(self):
        self.assertEqual(ip_set(['1.2.3.4']).intersection(
                             set(['1.2.3.4', '5.6.7.8'])),
                         ip_set(['1.2.3.4']))

    def test_intersection_3(self):
        self.assertEqual(ip_set(['1.2.3.4']).intersection(
                             ['1.2.3.4', '5.6.7.8']),
                         ip_set(['1.2.3.4']))

    def test_intersection_4(self):
        self.assertEqual(ip_set(['1.2.3.4']).intersection(
                             [IPWildcard('5.6.7.8')]),
                         ip_set([]))

    def test_intersection_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4']).intersection(ip_set())),
                         [])

    def test_and_1(self):
        self.assertEqual(ip_set(['1.2.3.4']) & ip_set(['1.2.3.4', '5.6.7.8']),
                         ip_set(['1.2.3.4']))

    def test_and_2(self):
        self.assertRaises(TypeError, operator.and_,
                          ip_set(['1.2.3.4']), set(['1.2.3.4', '5.6.7.8']))

    def test_and_3(self):
        self.assertRaises(TypeError, operator.and_,
                          ip_set(['1.2.3.4']), (['1.2.3.4', '5.6.7.8']))

    def test_and_4(self):
        self.assertRaises(TypeError, operator.and_,
                          ip_set(['1.2.3.4']), [IPWildcard('5.6.7.8')])

    def test_and_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4']) & ip_set()),
                         [])

    def test_difference_1(self):
        self.assertEqual(ip_set(['1.2.3.4', '2.3.4.5']).difference(
                             ip_set(['1.2.3.4', '5.6.7.8'])),
                         ip_set(['2.3.4.5']))

    def test_difference_2(self):
        self.assertEqual(ip_set(['1.2.3.4', '2.3.4.5']).difference(
                             set(['1.2.3.4', '5.6.7.8'])),
                         ip_set(['2.3.4.5']))

    def test_difference_3(self):
        self.assertEqual(ip_set(['1.2.3.4', '2.3.4.5']).difference(
                             ['1.2.3.4', '5.6.7.8']),
                         ip_set(['2.3.4.5']))

    def test_difference_4(self):
        self.assertEqual(ip_set(['1.2.3.4']).difference(
                             [IPWildcard('5.6.7.8')]),
                         ip_set(['1.2.3.4']))

    def test_difference_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4']).difference(ip_set())),
                         [IPAddr('1.2.3.4')])

    def test_sub_1(self):
        self.assertEqual(ip_set(['1.2.3.4', '2.3.4.5']) -
                         ip_set(['1.2.3.4', '5.6.7.8']),
                         ip_set(['2.3.4.5']))

    def test_sub_2(self):
        self.assertRaises(TypeError, operator.sub,
                          ip_set(['1.2.3.4', '2.3.4.5']),
                          set(['1.2.3.4', '5.6.7.8']))

    def test_sub_3(self):
        self.assertRaises(TypeError, operator.sub,
                          ip_set(['1.2.3.4', '2.3.4.5']),
                          ['1.2.3.4', '5.6.7.8'])

    def test_sub_4(self):
        self.assertRaises(TypeError, operator.sub,
                          ip_set(['1.2.3.4']), [IPWildcard('5.6.7.8')])

    def test_sub_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4']) - ip_set()),
                         [IPAddr('1.2.3.4')])

    def test_symmetric_difference_1(self):
        self.assertEqual(
            ip_set(['1.2.3.4', '2.3.4.5']).symmetric_difference(
                ip_set(['1.2.3.4', '5.6.7.8'])),
            ip_set(['2.3.4.5', '5.6.7.8']))

    def test_symmetric_difference_2(self):
        self.assertEqual(
            ip_set(['1.2.3.4', '2.3.4.5']).symmetric_difference(
                set(['1.2.3.4', '5.6.7.8'])),
            ip_set(['2.3.4.5', '5.6.7.8']))

    def test_symmetric_difference_3(self):
        self.assertEqual(
            ip_set(['1.2.3.4', '2.3.4.5']).symmetric_difference(
                ['1.2.3.4', '5.6.7.8']),
            ip_set(['2.3.4.5', '5.6.7.8']))

    def test_symmetric_difference_4(self):
        self.assertEqual(ip_set(['1.2.3.4']).symmetric_difference(
                             [IPWildcard('5.6.7.8')]),
                         ip_set(['1.2.3.4', '5.6.7.8']))

    def test_symmetric_difference_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4'])
                              .symmetric_difference(ip_set())),
                         [IPAddr('1.2.3.4')])

    def test_xor_1(self):
        self.assertEqual(ip_set(['1.2.3.4', '2.3.4.5']) ^
                         ip_set(['1.2.3.4', '5.6.7.8']),
                         ip_set(['2.3.4.5', '5.6.7.8']))

    def test_xor_2(self):
        self.assertRaises(TypeError, operator.xor,
                          ip_set(['1.2.3.4', '2.3.4.5']),
                          set(['1.2.3.4', '5.6.7.8']))

    def test_xor_3(self):
        self.assertRaises(TypeError, operator.xor,
                          ip_set(['1.2.3.4', '2.3.4.5']),
                          ['1.2.3.4', '5.6.7.8'])

    def test_xor_4(self):
        self.assertRaises(TypeError, operator.xor,
                          ip_set(['1.2.3.4']), [IPWildcard('5.6.7.8')])

    def test_xor_5(self):
        self.assertEqual(list(ip_set(['1.2.3.4']) ^ ip_set()),
                         [IPAddr('1.2.3.4')])

    def test_copy_1(self):
        self.assertEqual(ip_set(['1.2.3.4']).copy(),
                         ip_set(['1.2.3.4']))

    def test_copy_2(self):
        self.assertTrue(isinstance(ip_set(['1.2.3.4']).copy(), ip_set))

    def test_update_1(self):
        s = ip_set(['1.2.3.4'])
        s.update(ip_set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['1.2.3.4', '5.6.7.8']))

    def test_update_2(self):
        s = ip_set(['1.2.3.4'])
        s.update(set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['1.2.3.4', '5.6.7.8']))

    def test_update_3(self):
        s = ip_set(['1.2.3.4'])
        s.update(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['1.2.3.4', '5.6.7.8']))

    def test_update_4(self):
        s = ip_set(['1.2.3.4'])
        s.update([IPWildcard('1.2.3.4'), IPWildcard('5.6.7.8')])
        self.assertEqual(s, ip_set(['1.2.3.4', '5.6.7.8']))

    def test_ior_1(self):
        s = ip_set(['1.2.3.4'])
        s |= ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['1.2.3.4', '5.6.7.8']))

    def test_ior_2(self):
        s = ip_set(['1.2.3.4'])
        self.assertRaises(TypeError, op_ior,
                          s, set(['1.2.3.4', '5.6.7.8']))

    def test_ior_3(self):
        s = ip_set(['1.2.3.4'])
        if sys.version_info >= (2, 5):
            self.assertRaises(TypeError, op_ior,
                              s, ['1.2.3.4', '5.6.7.8'])

    def test_intersection_update_1(self):
        s = ip_set(['1.2.3.4'])
        s.intersection_update(ip_set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['1.2.3.4']))

    def test_intersection_update_2(self):
        s = ip_set(['1.2.3.4'])
        s.intersection_update(set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['1.2.3.4']))

    def test_intersection_update_3(self):
        s = ip_set(['1.2.3.4'])
        s.intersection_update(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['1.2.3.4']))

    def test_intersection_update_4(self):
        s = ip_set(['1.2.3.4'])
        s.intersection_update([IPWildcard('1.2.3.4'), IPWildcard('5.6.7.8')])
        self.assertEqual(s, ip_set(['1.2.3.4']))

    def test_iand_1(self):
        s = ip_set(['1.2.3.4'])
        s &= ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['1.2.3.4']))

    def test_iand_2(self):
        s = ip_set(['1.2.3.4'])
        self.assertRaises(TypeError, op_iand,
                          s, set(['1.2.3.4', '5.6.7.8']))

    def test_iand_3(self):
        s = ip_set(['1.2.3.4'])
        self.assertRaises(TypeError, op_iand,
                          s, ['1.2.3.4', '5.6.7.8'])

    def test_difference_update_1(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.difference_update(ip_set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['2.3.4.5']))

    def test_difference_update_2(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.difference_update(set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['2.3.4.5']))

    def test_difference_update_3(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.difference_update(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['2.3.4.5']))

    def test_difference_update_4(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.difference_update([IPWildcard('1.2.3.4'), IPWildcard('5.6.7.8')])
        self.assertEqual(s, ip_set(['2.3.4.5']))

    def test_isub_1(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s -= ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['2.3.4.5']))

    def test_isub_2(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        self.assertRaises(TypeError, op_isub,
                          s, set(['1.2.3.4', '5.6.7.8']))

    def test_isub_3(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        self.assertRaises(TypeError, op_isub,  s, ['1.2.3.4', '5.6.7.8'])

    def test_symmetric_difference_update_1(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.symmetric_difference_update(ip_set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['2.3.4.5', '5.6.7.8']))

    def test_symmetric_difference_update_2(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.symmetric_difference_update(set(['1.2.3.4', '5.6.7.8']))
        self.assertEqual(s, ip_set(['2.3.4.5', '5.6.7.8']))

    def test_symmetric_difference_update_3(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.symmetric_difference_update(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['2.3.4.5', '5.6.7.8']))

    def test_symmetric_difference_update_4(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s.symmetric_difference_update([IPWildcard('1.2.3.4'),
                                       IPWildcard('5.6.7.8')])
        self.assertEqual(s, ip_set(['2.3.4.5', '5.6.7.8']))

    def test_ixor_1(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        s ^= ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertEqual(s, ip_set(['2.3.4.5', '5.6.7.8']))

    def test_ixor_2(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        self.assertRaises(TypeError, op_ixor,
                          s, set(['1.2.3.4', '5.6.7.8']))

    def test_ixor_3(self):
        s = ip_set(['1.2.3.4', '2.3.4.5'])
        self.assertRaises(TypeError, op_ixor, s, ['1.2.3.4', '5.6.7.8'])

    def test_add_1(self):
        s = ip_set()
        s.add(IPAddr('1.2.3.4'))
        self.assertEqual(s, ip_set(['1.2.3.4']))

    def test_add_2(self):
        s = ip_set()
        s.add("1.2.3.4")
        self.assertEqual(s, ip_set(['1.2.3.4']))

    def test_add_3(self):
        s = ip_set()
        self.assertRaises(TypeError, s.add, 1)

    def test_add_4(self):
        s = ip_set()
        self.assertRaises(TypeError, s.add, 'foobar')

    def test_remove_1(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        s.remove(IPAddr('1.2.3.4'))
        self.assertEqual(s, ip_set(['5.6.7.8']))

    def test_remove_2(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        s.remove('1.2.3.4')
        self.assertEqual(s, ip_set(['5.6.7.8']))

    def test_remove_3(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertRaises(TypeError, s.remove, 1)

    def test_remove_4(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertRaises(TypeError, s.remove, "foobar")

    def test_remove_5(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertRaises(KeyError, s.remove, '1.2.3.5')

    def test_discard_1(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        s.discard(IPAddr('1.2.3.4'))
        self.assertEqual(s, ip_set(['5.6.7.8']))

    def test_discard_2(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        s.discard('1.2.3.4')
        self.assertEqual(s, ip_set(['5.6.7.8']))

    def test_discard_3(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertRaises(TypeError, s.discard, 1)

    def test_discard_4(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        self.assertRaises(TypeError, s.discard, "foobar")

    def test_discard_5(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        s.discard('1.2.3.5')
        self.assertEqual(s, ip_set(['1.2.3.4', '5.6.7.8']))

    def test_pop_1(self):
        s = ip_set(['1.2.3.4'])
        v = s.pop()
        self.assertEquals(s, ip_set())
        self.assertEquals(v, IPAddr('1.2.3.4'))

    def test_pop_2(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        v = s.pop()
        self.assertEquals(len(s), 1)
        self.assertTrue(v in [IPAddr('1.2.3.4'), IPAddr('5.6.7.8')])
        self.assertTrue(v not in s)

    def test_pop_3(self):
        s = ip_set()
        self.assertRaises(KeyError, s.pop)

    def test_clear(self):
        s = ip_set(['1.2.3.4', '5.6.7.8'])
        s.clear()
        self.assertEquals(s, ip_set())

    def test_cidr_iter_1(self):
        s = ip_set([IPWildcard('1.2.3.x')])
        s2 = set(s.cidr_iter())
        self.assertEqual(s2, set([(IPAddr('1.2.3.0'), 24)]))

    def test_cidr_iter_2(self):
        s = ip_set([IPWildcard('1.2.3.128-255'),
                    IPWildcard('1.2.4.0-128')])
        s2 = set(s.cidr_iter())
        self.assertEqual(s2, set([(IPAddr('1.2.3.128'), 25),
                                  (IPAddr('1.2.4.0'), 25),
                                  (IPAddr('1.2.4.128'), 32)]))

    def test_iter_1(self):
        s = ip_set(['1.2.3.4', '5.6.7.8', '9.10.11.12'])
        self.assertEqual(sorted(list(s)),
                         [IPAddr(x) for x in
                          ['1.2.3.4', '5.6.7.8', '9.10.11.12']])

    def test_iter_2(self):
        s = ip_set(['1.2.3.4', '5.6.7.8', '9.10.11.12'])
        s = s.copy()
        self.assertEqual(sorted(list(s)),
                         [IPAddr(x) for x in
                          ['1.2.3.4', '5.6.7.8', '9.10.11.12']])

    def test_iter_3(self):
        s = ip_set(['1.2.3.4', '5.6.7.8', '9.10.11.12'])
        s = s.union([])
        self.assertEqual(sorted(list(s)),
                         [IPAddr(x) for x in
                          ['1.2.3.4', '5.6.7.8', '9.10.11.12']])

    def test_silk_IPSetConstruction(self):
        IPSet()
        IPSet(["1.2.3.4"])
        IPSet(["1.2.3.4", "5.6.7.8"])
        IPSet(IPAddr(x) for x in ["1.2.3.4"])
        IPSet(IPAddr(x) for x in ["1.2.3.4", "5.6.7.8"])
        IPSet(["1.2.3.4", IPAddr("5.6.7.8")])
        if ipv6_enabled():
            IPSet(["2001:db8:1:2::3:4"])
            IPSet(["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            IPSet(IPAddr(x) for x in ["2001:db8:1:2::3:4"])
            IPSet(IPAddr(x) for x in ["2001:db8:1:2::3:4",
                                      "2001:db8:5:6::7:8"])
            IPSet(["2001:db8:1:2::3:4", IPAddr("2001:db8:5:6::7:8")])

    def test_silk_IPSetSupportsIPv6(self):
        self.assertEqual(IPSet.supports_ipv6(), ipv6_enabled())
        s = IPSet()
        self.assertEqual(s.supports_ipv6(), ipv6_enabled())

    def test_silk_IPSetAddAndIn(self):
        s = IPSet()
        s.add("1.2.3.4")
        self.assertEqual("1.2.3.4" in s, True)
        self.assertEqual("0.0.0.0" not in s, True)
        self.assertEqual(IPAddr("1.2.3.4") in s, True)
        self.assertEqual(IPAddr("0.0.0.0") not in s, True)
        s.add(IPAddr("5.6.7.8"))
        self.assertEqual("1.2.3.4" in s, True)
        self.assertEqual("5.6.7.8" in s, True)
        self.assertEqual("0.0.0.0" not in s, True)
        self.assertEqual(IPAddr("1.2.3.4") in s, True)
        self.assertEqual(IPAddr("5.6.7.8") in s, True)
        self.assertEqual(IPAddr("0.0.0.0") not in s, True)
        self.assertRaises(TypeError, s.add, 0)
        if ipv6_enabled():
            s = IPSet()
            s.add("2001:db8:1:2::3:4")
            self.assertEqual("2001:db8:1:2::3:4" in s, True)
            self.assertEqual("2001:db8:0:0::0:0" not in s, True)
            self.assertEqual(IPAddr("2001:db8:1:2::3:4") in s, True)
            self.assertEqual(IPAddr("2001:db8:0:0::0:0") not in s, True)
            s.add(IPAddr("2001:db8:5:6::7:8"))
            self.assertEqual("2001:db8:1:2::3:4" in s, True)
            self.assertEqual("2001:db8:5:6::7:8" in s, True)
            self.assertEqual("2001:db8:0:0::0:0" not in s, True)
            self.assertEqual(IPAddr("2001:db8:1:2::3:4") in s, True)
            self.assertEqual(IPAddr("2001:db8:5:6::7:8") in s, True)
            self.assertEqual(IPAddr("2001:db8:0:0::0:0") not in s, True)
            self.assertRaises(TypeError, s.add, 0)

    def test_silk_IPSetIPPromotion(self):
        if not ipv6_enabled():
            return
        s = IPSet()
        s.add("1.2.3.4")
        s.add("2001:db8:1:2::3:4")
        self.assertEqual("1.2.3.4" in s, True)
        self.assertEqual("0.0.0.0" not in s, True)
        self.assertEqual(IPAddr("1.2.3.4") in s, True)
        self.assertEqual(IPAddr("0.0.0.0") not in s, True)
        self.assertEqual("2001:db8:1:2::3:4" in s, True)
        self.assertEqual("2001:db8:0:0::0:0" not in s, True)
        self.assertEqual(IPAddr("2001:db8:1:2::3:4") in s, True)
        self.assertEqual(IPAddr("2001:db8:0:0::0:0") not in s, True)
        self.assertEqual("::ffff:1.2.3.4" in s, True)
        self.assertEqual("::ffff:0.0.0.0" not in s, True)
        self.assertEqual(IPAddr("::ffff:1.2.3.4") in s, True)
        self.assertEqual(IPAddr("::ffff:0.0.0.0") not in s, True)

    def test_silk_IPSetCopy(self):
        s1 = IPSet()
        s2 = s1
        s3 = s1.copy()
        self.assert_(s1 == s2 == s3)
        self.assert_(s1 is s2)
        self.assert_(s1 is not s3)
        s1.add("1.2.3.4")
        s1.add("5.6.7.8")
        s3 = s1.copy()
        self.assert_(s1 == s2 == s3)
        self.assert_(s1 is s2)
        self.assert_(s1 is not s3)
        if ipv6_enabled():
            s1 = IPSet()
            # force set to be IPv6
            s1.add("::")
            s1.remove("::")
            s2 = s1
            s3 = s1.copy()
            self.assert_(s1 == s2 == s3)
            self.assert_(s1 is s2)
            self.assert_(s1 is not s3)
            s1.add("2001:db8:1:2::3:4")
            s1.add("2001:db8:5:6::7:8")
            s3 = s1.copy()
            self.assert_(s1 == s2 == s3)
            self.assert_(s1 is s2)
            self.assert_(s1 is not s3)

    def test_silk_IPSetRemove(self):
        s = IPSet()
        s.add("1.2.3.4")
        s.add("5.6.7.8")
        self.assert_("1.2.3.4" in s)
        self.assert_("5.6.7.8" in s)
        s.remove("1.2.3.4")
        self.assert_("1.2.3.4" not in s)
        self.assert_("5.6.7.8" in s)
        s.remove("5.6.7.8")
        self.assert_("1.2.3.4" not in s)
        self.assert_("5.6.7.8" not in s)
        self.assertRaises(KeyError, s.remove, "1.2.3.4")
        if ipv6_enabled():
            s = IPSet()
            s.add("2001:db8:1:2::3:4")
            s.add("2001:db8:5:6::7:8")
            self.assert_("2001:db8:1:2::3:4" in s)
            self.assert_("2001:db8:5:6::7:8" in s)
            s.remove("2001:db8:1:2::3:4")
            self.assert_("2001:db8:1:2::3:4" not in s)
            self.assert_("2001:db8:5:6::7:8" in s)
            s.remove("2001:db8:5:6::7:8")
            self.assert_("2001:db8:1:2::3:4" not in s)
            self.assert_("2001:db8:5:6::7:8" not in s)
            self.assertRaises(KeyError, s.remove, "2001:db8:1:2::3:4")

    def test_silk_IPSetDiscard(self):
        s = IPSet()
        s.add("1.2.3.4")
        s.add("5.6.7.8")
        self.assert_("1.2.3.4" in s)
        self.assert_("5.6.7.8" in s)
        s.discard("1.2.3.4")
        self.assert_("1.2.3.4" not in s)
        self.assert_("5.6.7.8" in s)
        s.discard("5.6.7.8")
        self.assert_("1.2.3.4" not in s)
        self.assert_("5.6.7.8" not in s)
        s.discard("1.2.3.4")
        self.assert_("1.2.3.4" not in s)
        self.assert_("5.6.7.8" not in s)
        if ipv6_enabled():
            s = IPSet()
            s.add("2001:db8:1:2::3:4")
            s.add("2001:db8:5:6::7:8")
            self.assert_("2001:db8:1:2::3:4" in s)
            self.assert_("2001:db8:5:6::7:8" in s)
            s.discard("2001:db8:1:2::3:4")
            self.assert_("2001:db8:1:2::3:4" not in s)
            self.assert_("2001:db8:5:6::7:8" in s)
            s.discard("2001:db8:5:6::7:8")
            self.assert_("2001:db8:1:2::3:4" not in s)
            self.assert_("2001:db8:5:6::7:8" not in s)
            s.discard("2001:db8:1:2::3:4")
            self.assert_("2001:db8:1:2::3:4" not in s)
            self.assert_("2001:db8:5:6::7:8" not in s)

    def test_silk_IPSetClear(self):
        s = IPSet()
        s.add("1.2.3.4")
        s.add("5.6.7.8")
        self.assert_("1.2.3.4" in s)
        self.assert_("5.6.7.8" in s)
        s.clear()
        self.assert_("1.2.3.4" not in s)
        self.assert_("5.6.7.8" not in s)
        if ipv6_enabled():
            s = IPSet()
            s.add("2001:db8:1:2::3:4")
            s.add("2001:db8:5:6::7:8")
            self.assert_("2001:db8:1:2::3:4" in s)
            self.assert_("2001:db8:5:6::7:8" in s)
            s.clear()
            self.assert_("2001:db8:1:2::3:4" not in s)
            self.assert_("2001:db8:5:6::7:8" not in s)

    def test_silk_IPSetLenAndCard(self):
        s = IPSet()
        self.assertEqual(len(s), 0)
        self.assertEqual(s.cardinality(), 0)
        s.add("1.2.3.4")
        s.add("5.6.7.8")
        self.assertEqual(len(s), 2)
        self.assertEqual(s.cardinality(), 2)
        s.remove("1.2.3.4")
        self.assertEqual(len(s), 1)
        self.assertEqual(s.cardinality(), 1)
        if ipv6_enabled():
            s = IPSet()
            # force set to be IPv6
            s.add("::")
            s.remove("::")
            self.assertEqual(len(s), 0)
            self.assertEqual(s.cardinality(), 0)
            s.add("2001:db8:1:2::3:4")
            s.add("2001:db8:5:6::7:8")
            self.assertEqual(len(s), 2)
            self.assertEqual(s.cardinality(), 2)
            s.remove("2001:db8:1:2::3:4")
            self.assertEqual(len(s), 1)
            self.assertEqual(s.cardinality(), 1)

    def test_silk_IPSetSubsetSuperset(self):
        s1 = IPSet()
        s2 = IPSet()
        self.assert_(s1.issubset(s2))
        self.assert_(s2.issubset(s1))
        self.assert_(s1.issuperset(s2))
        self.assert_(s2.issuperset(s1))
        self.assert_(s1 <= s2)
        self.assert_(s2 <= s1)
        self.assert_(s1 >= s2)
        self.assert_(s2 >= s1)
        s1.add("1.2.3.4")
        s1.add("5.6.7.8")
        s2.add("5.6.7.8")
        self.assertEqual(s1.issubset(s2), False)
        self.assertEqual(s2.issubset(s1), True)
        self.assertEqual(s1.issuperset(s2), True)
        self.assertEqual(s2.issuperset(s1), False)
        self.assertEqual(s1 <= s2, False)
        self.assertEqual(s2 <= s1, True)
        self.assertEqual(s1 >= s2, True)
        self.assertEqual(s2 >= s1, False)
        self.assertEqual(s2.issubset(["1.2.3.4", "5.6.7.8"]), True)
        self.assertEqual(s2.issubset(["1.2.3.4"]), False)
        self.assertEqual(s1.issuperset(["1.2.3.4"]), True)
        self.assertEqual(s1.issuperset(["1.2.3.4", "0.0.0.0"]), False)
        self.assertRaises(TypeError, operator.le, s2, ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, operator.ge, s1, ["1.2.3.4"])
        if ipv6_enabled():
            s1 = IPSet()
            s2 = IPSet()
            # force sets to be IPv6
            s1.add("::")
            s1.remove("::")
            s2.add("::")
            s2.remove("::")
            self.assert_(s1.issubset(s2))
            self.assert_(s2.issubset(s1))
            self.assert_(s1.issuperset(s2))
            self.assert_(s2.issuperset(s1))
            self.assert_(s1 <= s2)
            self.assert_(s2 <= s1)
            self.assert_(s1 >= s2)
            self.assert_(s2 >= s1)
            s1.add("2001:db8:1:2::3:4")
            s1.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:5:6::7:8")
            self.assertEqual(s1.issubset(s2), False)
            self.assertEqual(s2.issubset(s1), True)
            self.assertEqual(s1.issuperset(s2), True)
            self.assertEqual(s2.issuperset(s1), False)
            self.assertEqual(s1 <= s2, False)
            self.assertEqual(s2 <= s1, True)
            self.assertEqual(s1 >= s2, True)
            self.assertEqual(s2 >= s1, False)
            self.assertEqual(s2.issubset(["2001:db8:1:2::3:4",
                                          "2001:db8:5:6::7:8"]),
                             True)
            self.assertEqual(s2.issubset(["2001:db8:1:2::3:4"]), False)
            self.assertEqual(s1.issuperset(["2001:db8:1:2::3:4"]), True)
            self.assertEqual(s1.issuperset(["2001:db8:1:2::3:4",
                                            "2001:db8:0:0::0:0"]),
                             False)
            self.assertRaises(TypeError, operator.le, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, operator.ge, s1,
                              ["2001:db8:1:2::3:4"])

    def test_silk_IPSetUnion(self):
        s1 = IPSet()
        s2 = IPSet()
        s1.add("1.2.3.4")
        s1.add("5.6.7.8")
        s2.add("5.6.7.8")
        s2.add("9.10.11.12")
        s3 = s1.union(s2)
        s4 = s2.union(s1)
        s5 = s1.copy()
        s5.update(s2)
        self.assert_(s3 == s4 == s5)
        self.assert_(s1 <= s3)
        self.assert_(s2 <= s3)
        self.assert_(s1 <= s4)
        self.assert_(s2 <= s4)
        self.assert_(s1 <= s5)
        self.assert_(s2 <= s5)
        self.assertEqual(s3.cardinality(), 3)
        self.assertEqual(s4.cardinality(), 3)
        self.assertEqual(s5.cardinality(), 3)
        s3 = s1 | s2
        s4 = s2 | s1
        s5 = s1.copy()
        s5 |= s2
        self.assert_(s3 == s4 == s5)
        self.assert_(s1 <= s3)
        self.assert_(s2 <= s3)
        self.assert_(s1 <= s4)
        self.assert_(s2 <= s4)
        self.assert_(s1 <= s5)
        self.assert_(s2 <= s5)
        self.assertEqual(s3.cardinality(), 3)
        self.assertEqual(s4.cardinality(), 3)
        self.assertEqual(s5.cardinality(), 3)
        s3 = s1.union(["5.6.7.8", "9.10.11.12"])
        s4 = s2.union(["1.2.3.4", "5.6.7.8"])
        s5 = s1.copy()
        s5.update(["5.6.7.8", "9.10.11.12"])
        self.assert_(s3 == s4 == s5)
        self.assert_(s1 <= s3)
        self.assert_(s2 <= s3)
        self.assert_(s1 <= s4)
        self.assert_(s2 <= s4)
        self.assert_(s1 <= s5)
        self.assert_(s2 <= s5)
        self.assertEqual(s3.cardinality(), 3)
        self.assertEqual(s4.cardinality(), 3)
        self.assertEqual(s5.cardinality(), 3)
        s6 = s1.copy()
        s6.update(IPWildcard("10.x.x.10"))
        self.assertEqual("10.10.10.10" in s6, True)
        self.assertEqual("10.0.255.10" in s6, True)
        self.assertEqual("10.0.0.10" in s6, True)
        self.assertEqual("10.255.255.10" in s6, True)
        self.assertEqual("10.10.10.0" not in s6, True)
        self.assertEqual("0.10.10.10" not in s6, True)
        self.assertEqual(s6.cardinality(), 0x10002)
        self.assertRaises(TypeError, operator.or_, s1,
                          ["5.6.7.8", "9.10.11.12"])
        self.assertRaises(TypeError, operator.or_, s2, ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, operator.or_, s1,
                          ["5.6.7.8", "9.10.11.12"])
        self.assertRaises(TypeError, operator.or_, s2, ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, op_ior, s5,
                          ["5.6.7.8", "9.10.11.12"])
        if sys.version_info >= (2, 6):
            s7 = s1.union(s2, IPWildcard("10.x.x.10"),
                          ["192.168.1.2", "192.168.3.4"])
            s8 = s1.copy()
            s8.update(s2, IPWildcard("10.x.x.10"),
                          ["192.168.1.2", "192.168.3.4"])
            self.assert_(s7 == s8)
            self.assertEqual("1.2.3.4" in s8, True)
            self.assertEqual("5.6.7.8" in s8, True)
            self.assertEqual("192.168.1.2" in s8, True)
            self.assertEqual("10.10.10.10" in s8, True)
            self.assertEqual("10.0.255.10" in s8, True)
            self.assertEqual("10.0.0.10" in s8, True)
            self.assertEqual("10.255.255.10" in s8, True)
            self.assertEqual("10.10.10.0" not in s8, True)
            self.assertEqual("0.10.10.10" not in s8, True)
        if ipv6_enabled():
            s1 = IPSet()
            s2 = IPSet()
            s1.add("2001:db8:1:2::3:4")
            s1.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:9:10::11:12")
            s3 = s1.union(s2)
            s4 = s2.union(s1)
            s5 = s1.copy()
            s5.update(s2)
            self.assert_(s3 == s4 == s5)
            self.assert_(s1 <= s3)
            self.assert_(s2 <= s3)
            self.assert_(s1 <= s4)
            self.assert_(s2 <= s4)
            self.assert_(s1 <= s5)
            self.assert_(s2 <= s5)
            self.assertEqual(s3.cardinality(), 3)
            self.assertEqual(s4.cardinality(), 3)
            self.assertEqual(s5.cardinality(), 3)
            s3 = s1 | s2
            s4 = s2 | s1
            s5 = s1.copy()
            s5 |= s2
            self.assert_(s3 == s4 == s5)
            self.assert_(s1 <= s3)
            self.assert_(s2 <= s3)
            self.assert_(s1 <= s4)
            self.assert_(s2 <= s4)
            self.assert_(s1 <= s5)
            self.assert_(s2 <= s5)
            self.assertEqual(s3.cardinality(), 3)
            self.assertEqual(s4.cardinality(), 3)
            self.assertEqual(s5.cardinality(), 3)
            s3 = s1.union(["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            s4 = s2.union(["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            s5 = s1.copy()
            s5.update(["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assert_(s3 == s4 == s5)
            self.assert_(s1 <= s3)
            self.assert_(s2 <= s3)
            self.assert_(s1 <= s4)
            self.assert_(s2 <= s4)
            self.assert_(s1 <= s5)
            self.assert_(s2 <= s5)
            self.assertEqual(s3.cardinality(), 3)
            self.assertEqual(s4.cardinality(), 3)
            self.assertEqual(s5.cardinality(), 3)
            s6 = s1.copy()
            s6.update(IPWildcard("::ffff:10.x.x.10"))
            self.assertEqual("::ffff:10.10.10.10" in s6, True)
            self.assertEqual("::ffff:10.0.255.10" in s6, True)
            self.assertEqual("::ffff:10.0.0.10" in s6, True)
            self.assertEqual("::ffff:10.255.255.10" in s6, True)
            self.assertEqual("::ffff:10.10.10.0" not in s6, True)
            self.assertEqual("::ffff:0.10.10.10" not in s6, True)
            self.assertEqual(s6.cardinality(), 0x10002)
            self.assertRaises(TypeError, operator.or_, s1,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertRaises(TypeError, operator.or_, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, operator.or_, s1,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertRaises(TypeError, operator.or_, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, op_ior,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])

    def test_silk_IPSetIntersection(self):
        s1 = IPSet()
        s2 = IPSet()
        s1.add("1.2.3.4")
        s1.add("5.6.7.8")
        s2.add("5.6.7.8")
        s2.add("9.10.11.12")
        s3 = s1.intersection(s2)
        s4 = s2.intersection(s1)
        s5 = s1.copy()
        s5.intersection_update(s2)
        self.assert_(s3 == s4 == s5)
        self.assert_(s1 >= s3)
        self.assert_(s2 >= s3)
        self.assert_(s1 >= s4)
        self.assert_(s2 >= s4)
        self.assert_(s1 >= s5)
        self.assert_(s2 >= s5)
        self.assertEqual(s3.cardinality(), 1)
        self.assertEqual(s4.cardinality(), 1)
        self.assertEqual(s5.cardinality(), 1)
        s3 = s1 & s2
        s4 = s2 & s1
        s5 = s1.copy()
        s5 &= s2
        self.assert_(s3 == s4 == s5)
        self.assert_(s1 >= s3)
        self.assert_(s2 >= s3)
        self.assert_(s1 >= s4)
        self.assert_(s2 >= s4)
        self.assert_(s1 >= s5)
        self.assert_(s2 >= s5)
        self.assertEqual(s3.cardinality(), 1)
        self.assertEqual(s4.cardinality(), 1)
        self.assertEqual(s5.cardinality(), 1)
        s3 = s1.intersection(["5.6.7.8", "9.10.11.12"])
        s4 = s2.intersection(["1.2.3.4", "5.6.7.8"])
        s5 = s1.copy()
        s5.intersection_update(["5.6.7.8", "9.10.11.12"])
        self.assert_(s3 == s4 == s5)
        self.assert_(s1 >= s3)
        self.assert_(s2 >= s3)
        self.assert_(s1 >= s4)
        self.assert_(s2 >= s4)
        self.assert_(s1 >= s5)
        self.assert_(s2 >= s5)
        self.assertEqual(s3.cardinality(), 1)
        self.assertEqual(s4.cardinality(), 1)
        self.assertEqual(s5.cardinality(), 1)
        s5 = s1.copy()
        self.assertRaises(TypeError, operator.and_, s1,
                          ["5.6.7.8", "9.10.11.12"])
        self.assertRaises(TypeError, operator.and_, s2,
                          ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, operator.and_, s1,
                          ["5.6.7.8", "9.10.11.12"])
        self.assertRaises(TypeError, operator.and_, s2, ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, op_iand, s5,
                          ["5.6.7.8", "9.10.11.12"])
        if sys.version_info >= (2, 6):
            s6 = s1.intersection(s2, ["5.6.7.8", "9.10.11.12"])
            s7 = s1.copy()
            s7.intersection_update(s2, ["5.6.7.8", "9.10.11.12"])
            self.assertEqual(s6, s7)
            self.assertEqual("5.6.7.8" in s6, True)
            self.assertEqual(len(s6), 1)
        if ipv6_enabled():
            s1 = IPSet()
            s2 = IPSet()
            s1.add("2001:db8:1:2::3:4")
            s1.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:9:10::11:12")
            s3 = s1.intersection(s2)
            s4 = s2.intersection(s1)
            s5 = s1.copy()
            s5.intersection_update(s2)
            self.assert_(s3 == s4 == s5)
            self.assert_(s1 >= s3)
            self.assert_(s2 >= s3)
            self.assert_(s1 >= s4)
            self.assert_(s2 >= s4)
            self.assert_(s1 >= s5)
            self.assert_(s2 >= s5)
            self.assertEqual(s3.cardinality(), 1)
            self.assertEqual(s4.cardinality(), 1)
            self.assertEqual(s5.cardinality(), 1)
            s3 = s1 & s2
            s4 = s2 & s1
            s5 = s1.copy()
            s5 &= s2
            self.assert_(s3 == s4 == s5)
            self.assert_(s1 >= s3)
            self.assert_(s2 >= s3)
            self.assert_(s1 >= s4)
            self.assert_(s2 >= s4)
            self.assert_(s1 >= s5)
            self.assert_(s2 >= s5)
            self.assertEqual(s3.cardinality(), 1)
            self.assertEqual(s4.cardinality(), 1)
            self.assertEqual(s5.cardinality(), 1)
            s3 = s1.intersection(["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            s4 = s2.intersection(["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            s5 = s1.copy()
            s5.intersection_update(["2001:db8:5:6::7:8",
                                    "2001:db8:9:10::11:12"])
            self.assert_(s3 == s4 == s5)
            self.assert_(s1 >= s3)
            self.assert_(s2 >= s3)
            self.assert_(s1 >= s4)
            self.assert_(s2 >= s4)
            self.assert_(s1 >= s5)
            self.assert_(s2 >= s5)
            self.assertEqual(s3.cardinality(), 1)
            self.assertEqual(s4.cardinality(), 1)
            self.assertEqual(s5.cardinality(), 1)
            s5 = s1.copy()
            self.assertRaises(TypeError, operator.and_, s1,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertRaises(TypeError, operator.and_, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, operator.and_, s1,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertRaises(TypeError, operator.and_, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, op_iand, s5,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])

    def test_silk_IPSetDifference(self):
        s1 = IPSet()
        s2 = IPSet()
        s1.add("1.2.3.4")
        s1.add("5.6.7.8")
        s2.add("5.6.7.8")
        s2.add("9.10.11.12")
        s3 = s1.difference(s2)
        s4 = s2.difference(s1)
        s5 = s1.copy()
        s5.difference_update(s2)
        self.assertNotEqual(s3, s4)
        self.assertNotEqual(s5, s4)
        self.assert_(s1 >= s3)
        self.assert_(not (s3 & s2))
        self.assert_(s1 >= s5)
        self.assert_(not (s5 & s2))
        self.assert_(s2 >= s4)
        self.assert_(not (s4 & s1))
        self.assertEqual(s3.cardinality(), 1)
        self.assertEqual(s4.cardinality(), 1)
        self.assertEqual(s5.cardinality(), 1)
        s3 = s1 - s2
        s4 = s2 - s1
        s5 = s1.copy()
        s5 -= s2
        self.assertNotEqual(s3, s4)
        self.assertNotEqual(s5, s4)
        self.assert_(s1 >= s3)
        self.assert_(not (s3 & s2))
        self.assert_(s1 >= s5)
        self.assert_(not (s5 & s2))
        self.assert_(s2 >= s4)
        self.assert_(not (s4 & s1))
        self.assertEqual(s3.cardinality(), 1)
        self.assertEqual(s4.cardinality(), 1)
        self.assertEqual(s5.cardinality(), 1)
        s3 = s1.difference(["5.6.7.8", "9.10.11.12"])
        s4 = s2.difference(["1.2.3.4", "5.6.7.8"])
        s5 = s1.copy()
        s5.difference_update(["5.6.7.8", "9.10.11.12"])
        self.assertNotEqual(s3, s4)
        self.assertNotEqual(s5, s4)
        self.assert_(s1 >= s3)
        self.assert_(not (s3 & s2))
        self.assert_(s1 >= s5)
        self.assert_(not (s5 & s2))
        self.assert_(s2 >= s4)
        self.assert_(not (s4 & s1))
        self.assertEqual(s3.cardinality(), 1)
        self.assertEqual(s4.cardinality(), 1)
        self.assertEqual(s5.cardinality(), 1)
        self.assertRaises(TypeError, operator.sub, s1,
                          ["5.6.7.8", "9.10.11.12"])
        self.assertRaises(TypeError, operator.sub, s2,
                          ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, operator.sub, s1,
                          ["5.6.7.8", "9.10.11.12"])
        self.assertRaises(TypeError, operator.sub, s2, ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, op_isub, s5,
                          ["5.6.7.8", "9.10.11.12"])
        s6 = s1.copy()
        s6.add("7.7.7.7")
        s6.add("8.8.8.8")
        if sys.version_info >= (2, 6):
            s7 = s6.copy()
            s8 = s6.difference(s2, ["8.8.8.8", "9.9.9.9"])
            s7.difference_update(s2, ["8.8.8.8", "9.9.9.9"])
            self.assertEqual(s8, s7)
            self.assertEqual(len(s7), 2)
            self.assertEqual("1.2.3.4" in s7, True)
            self.assertEqual("7.7.7.7" in s7, True)
        if ipv6_enabled():
            s1 = IPSet()
            s2 = IPSet()
            s1.add("2001:db8:1:2::3:4")
            s1.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:9:10::11:12")
            s3 = s1.difference(s2)
            s4 = s2.difference(s1)
            s5 = s1.copy()
            s5.difference_update(s2)
            self.assertNotEqual(s3, s4)
            self.assertNotEqual(s5, s4)
            self.assert_(s1 >= s3)
            self.assert_(not (s3 & s2))
            self.assert_(s1 >= s5)
            self.assert_(not (s5 & s2))
            self.assert_(s2 >= s4)
            self.assert_(not (s4 & s1))
            self.assertEqual(s3.cardinality(), 1)
            self.assertEqual(s4.cardinality(), 1)
            self.assertEqual(s5.cardinality(), 1)
            s3 = s1 - s2
            s4 = s2 - s1
            s5 = s1.copy()
            s5 -= s2
            self.assertNotEqual(s3, s4)
            self.assertNotEqual(s5, s4)
            self.assert_(s1 >= s3)
            self.assert_(not (s3 & s2))
            self.assert_(s1 >= s5)
            self.assert_(not (s5 & s2))
            self.assert_(s2 >= s4)
            self.assert_(not (s4 & s1))
            self.assertEqual(s3.cardinality(), 1)
            self.assertEqual(s4.cardinality(), 1)
            self.assertEqual(s5.cardinality(), 1)
            s3 = s1.difference(["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            s4 = s2.difference(["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            s5 = s1.copy()
            s5.difference_update(["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertNotEqual(s3, s4)
            self.assertNotEqual(s5, s4)
            self.assert_(s1 >= s3)
            self.assert_(not (s3 & s2))
            self.assert_(s1 >= s5)
            self.assert_(not (s5 & s2))
            self.assert_(s2 >= s4)
            self.assert_(not (s4 & s1))
            self.assertEqual(s3.cardinality(), 1)
            self.assertEqual(s4.cardinality(), 1)
            self.assertEqual(s5.cardinality(), 1)
            self.assertRaises(TypeError, operator.sub, s1,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertRaises(TypeError, operator.sub, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, operator.sub, s1,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertRaises(TypeError, operator.sub, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, op_isub, s5,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])

    def test_silk_IPSetSymmetricDifference(self):
        s1 = IPSet()
        s2 = IPSet()
        s1.add("1.2.3.4")
        s1.add("5.6.7.8")
        s2.add("5.6.7.8")
        s2.add("9.10.11.12")
        s3 = s1.symmetric_difference(s2)
        s4 = s2.symmetric_difference(s1)
        s5 = s1.copy()
        s5.symmetric_difference_update(s2)
        self.assert_(s3 == s4 == s5)
        self.assert_(not s1 >= s3)
        self.assert_(not s2 >= s3)
        self.assert_(not s1 >= s4)
        self.assert_(not s2 >= s4)
        self.assert_(not s1 >= s5)
        self.assert_(not s2 >= s5)
        self.assert_(not s1 <= s3)
        self.assert_(not s2 <= s3)
        self.assert_(not s1 <= s4)
        self.assert_(not s2 <= s4)
        self.assert_(not s1 <= s5)
        self.assert_(not s2 <= s5)
        self.assertEqual(s3.cardinality(), 2)
        self.assertEqual(s4.cardinality(), 2)
        self.assertEqual(s5.cardinality(), 2)
        s3 = s1 ^ s2
        s4 = s2 ^ s1
        s5 = s1.copy()
        s5 ^= s2
        self.assert_(s3 == s4 == s5)
        self.assert_(not s1 >= s3)
        self.assert_(not s2 >= s3)
        self.assert_(not s1 >= s4)
        self.assert_(not s2 >= s4)
        self.assert_(not s1 >= s5)
        self.assert_(not s2 >= s5)
        self.assert_(not s1 <= s3)
        self.assert_(not s2 <= s3)
        self.assert_(not s1 <= s4)
        self.assert_(not s2 <= s4)
        self.assert_(not s1 <= s5)
        self.assert_(not s2 <= s5)
        self.assertEqual(s3.cardinality(), 2)
        self.assertEqual(s4.cardinality(), 2)
        self.assertEqual(s5.cardinality(), 2)
        s3 = s1.symmetric_difference(["5.6.7.8", "9.10.11.12"])
        s4 = s2.symmetric_difference(["1.2.3.4", "5.6.7.8"])
        s5 = s1.copy()
        s5.symmetric_difference_update(["5.6.7.8", "9.10.11.12"])
        self.assert_(s3 == s4 == s5)
        self.assert_(not s1 >= s3)
        self.assert_(not s2 >= s3)
        self.assert_(not s1 >= s4)
        self.assert_(not s2 >= s4)
        self.assert_(not s1 >= s5)
        self.assert_(not s2 >= s5)
        self.assert_(not s1 <= s3)
        self.assert_(not s2 <= s3)
        self.assert_(not s1 <= s4)
        self.assert_(not s2 <= s4)
        self.assert_(not s1 <= s5)
        self.assert_(not s2 <= s5)
        self.assertEqual(s3.cardinality(), 2)
        self.assertEqual(s4.cardinality(), 2)
        self.assertEqual(s5.cardinality(), 2)
        s5 = s1.copy()
        self.assertRaises(TypeError, operator.xor, s1,
                          ["5.6.7.8", "9.10.11.12"])
        self.assertRaises(TypeError, operator.xor, s2, ["1.2.3.4", "5.6.7.8"])
        self.assertRaises(TypeError, op_ixor, s5,
                          ["5.6.7.8", "9.10.11.12"])
        if ipv6_enabled():
            s1 = IPSet()
            s2 = IPSet()
            s1.add("2001:db8:1:2::3:4")
            s1.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:5:6::7:8")
            s2.add("2001:db8:9:10::11:12")
            s3 = s1.symmetric_difference(s2)
            s4 = s2.symmetric_difference(s1)
            s5 = s1.copy()
            s5.symmetric_difference_update(s2)
            self.assert_(s3 == s4 == s5)
            self.assert_(not s1 >= s3)
            self.assert_(not s2 >= s3)
            self.assert_(not s1 >= s4)
            self.assert_(not s2 >= s4)
            self.assert_(not s1 >= s5)
            self.assert_(not s2 >= s5)
            self.assert_(not s1 <= s3)
            self.assert_(not s2 <= s3)
            self.assert_(not s1 <= s4)
            self.assert_(not s2 <= s4)
            self.assert_(not s1 <= s5)
            self.assert_(not s2 <= s5)
            self.assertEqual(s3.cardinality(), 2)
            self.assertEqual(s4.cardinality(), 2)
            self.assertEqual(s5.cardinality(), 2)
            s3 = s1 ^ s2
            s4 = s2 ^ s1
            s5 = s1.copy()
            s5 ^= s2
            self.assert_(s3 == s4 == s5)
            self.assert_(not s1 >= s3)
            self.assert_(not s2 >= s3)
            self.assert_(not s1 >= s4)
            self.assert_(not s2 >= s4)
            self.assert_(not s1 >= s5)
            self.assert_(not s2 >= s5)
            self.assert_(not s1 <= s3)
            self.assert_(not s2 <= s3)
            self.assert_(not s1 <= s4)
            self.assert_(not s2 <= s4)
            self.assert_(not s1 <= s5)
            self.assert_(not s2 <= s5)
            self.assertEqual(s3.cardinality(), 2)
            self.assertEqual(s4.cardinality(), 2)
            self.assertEqual(s5.cardinality(), 2)
            s3 = s1.symmetric_difference(["2001:db8:5:6::7:8",
                                          "2001:db8:9:10::11:12"])
            s4 = s2.symmetric_difference(["2001:db8:1:2::3:4",
                                          "2001:db8:5:6::7:8"])
            s5 = s1.copy()
            s5.symmetric_difference_update(["2001:db8:5:6::7:8",
                                            "2001:db8:9:10::11:12"])
            self.assert_(s3 == s4 == s5)
            self.assert_(not s1 >= s3)
            self.assert_(not s2 >= s3)
            self.assert_(not s1 >= s4)
            self.assert_(not s2 >= s4)
            self.assert_(not s1 >= s5)
            self.assert_(not s2 >= s5)
            self.assert_(not s1 <= s3)
            self.assert_(not s2 <= s3)
            self.assert_(not s1 <= s4)
            self.assert_(not s2 <= s4)
            self.assert_(not s1 <= s5)
            self.assert_(not s2 <= s5)
            self.assertEqual(s3.cardinality(), 2)
            self.assertEqual(s4.cardinality(), 2)
            self.assertEqual(s5.cardinality(), 2)
            s5 = s1.copy()
            self.assertRaises(TypeError, operator.xor, s1,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])
            self.assertRaises(TypeError, operator.xor, s2,
                              ["2001:db8:1:2::3:4", "2001:db8:5:6::7:8"])
            self.assertRaises(TypeError, op_ixor, s5,
                              ["2001:db8:5:6::7:8", "2001:db8:9:10::11:12"])

    def test_silk_IPSetPop(self):
        s = IPSet(IPAddr(x) for x in ["1.1.1.1", "2.2.2.2"])
        self.assertEqual(len(s), 2)
        a = s.pop()
        self.assertEqual(len(s), 1)
        b = s.pop()
        self.assertEqual(len(s), 0)
        self.assert_(a == IPAddr("1.1.1.1") or a == IPAddr("2.2.2.2"))
        self.assert_(b == IPAddr("1.1.1.1") or b == IPAddr("2.2.2.2"))
        self.assertNotEqual(a, b)
        self.assertRaises(KeyError, s.pop)

    def test_silk_IPSetIterators(self):
        ipaddrs = [IPAddr(x) for x in
                   ["1.2.3.4", "1.2.3.5", "1.2.3.6", "1.2.3.7",
                    "1.2.3.8", "1.2.3.9", "0.0.0.0"]]
        s = IPSet(ipaddrs)
        count = 0
        for x in s:
            self.assert_(x in s)
            self.assert_(x in ipaddrs)
            count += 1
        self.assertEqual(count, len(ipaddrs))
        cidrlist = list(s.cidr_iter())
        self.assertEqual(len(cidrlist), 3)
        blocks = [IPAddr(x) for x in ['0.0.0.0', '1.2.3.4', '1.2.3.8']]
        prefixes = [32, 30, 31]
        self.assertEqual(set(cidrlist), set(zip(blocks, prefixes)))
        if ipv6_enabled():
            ipaddrs = [IPAddr(x) for x in
                       ["2001:db8:1:2::3:4", "2001:db8:1:2::3:5",
                        "2001:db8:1:2::3:6", "2001:db8:1:2::3:7",
                        "2001:db8:1:2::3:8", "2001:db8:1:2::3:9",
                        "2001:db8::"]]
            s = IPSet(ipaddrs)
            count = 0
            for x in s:
                self.assert_(x in s)
                self.assert_(x in ipaddrs)
                count += 1
            self.assertEqual(count, len(ipaddrs))
            cidrlist = list(s.cidr_iter())
            self.assertEqual(len(cidrlist), 3)
            blocks = [IPAddr(x) for x in
                      ['2001:db8:0:0::0:0', '2001:db8:1:2::3:4',
                       '2001:db8:1:2::3:8']]
            prefixes = [128, 126, 127]
            self.assertEqual(set(cidrlist), set(zip(blocks, prefixes)))
