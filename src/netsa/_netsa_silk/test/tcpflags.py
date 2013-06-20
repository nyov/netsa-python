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

from netsa._netsa_silk import (TCPFlags, TCP_FIN, TCP_SYN, TCP_RST, TCP_PSH,
                               TCP_URG, TCP_ECE, TCP_CWR, TCP_ACK)

class TCPFlagsTest(unittest.TestCase):

    def test_cons_1(self):
        self.assertRaises(TypeError, TCPFlags, 0.1)

    def test_cons_2(self):
        self.assertRaises(ValueError, TCPFlags, "bitter")

    def test_int_1(self):
        self.assertEqual(int(TCPFlags('F')), 0x01)

    def test_int_2(self):
        self.assertEqual(int(TCPFlags('S')), 0x02)

    def test_int_3(self):
        self.assertEqual(int(TCPFlags('R')), 0x04)

    def test_int_4(self):
        self.assertEqual(int(TCPFlags('p')), 0x08)

    def test_int_5(self):
        self.assertEqual(int(TCPFlags('  a  ')), 0x10)

    def test_int_6(self):
        self.assertEqual(int(TCPFlags('\tu\r\n')), 0x20)

    def test_int_7(self):
        self.assertEqual(int(TCPFlags('Ee')), 0x40)

    def test_int_8(self):
        self.assertEqual(int(TCPFlags('CcccCcC')), 0x80)

    def test_int_9(self):
        self.assertEqual(int(TCPFlags(0)), 0x00)

    def test_int_10(self):
        self.assertEqual(int(TCPFlags('frae')), 0x55)

    def test_int_11(self):
        self.assertEqual(int(TCPFlags('fsrpauec')), 0xFF)

    def test_inv_1(self):
        self.assertEqual(~TCPFlags('frae'), TCPFlags('spuc'))

    def test_inv_2(self):
        self.assertEqual(~TCPFlags('fsrp'), TCPFlags('auec'))

    def test_inv_3(self):
        self.assertEqual(~(~TCPFlags('frae')), TCPFlags('frae'))

    def test_and_1(self):
        self.assertEqual(TCPFlags('frae') & TCPFlags('fr'), TCPFlags('fr'))

    def test_and_2(self):
        self.assertEqual(TCPFlags('frae') & TCPFlags('fsrp'), TCPFlags('fr'))

    def test_and_3(self):
        self.assertEqual(TCPFlags('frae') & TCPFlags('spuc'), TCPFlags(''))

    def test_and_4(self):
        self.assertRaises(TypeError, operator.and_, TCPFlags('frae'), 0)

    def test_and_5(self):
        self.assertRaises(TypeError, operator.and_, TCPFlags('frae'), '')

    def test_or_1(self):
        self.assertEqual(TCPFlags('frae') | TCPFlags('fr'), TCPFlags('frae'))

    def test_or_2(self):
        self.assertEqual(TCPFlags('frae') | TCPFlags('fsrp'),
                         TCPFlags("fraesp"))

    def test_or_3(self):
        self.assertEqual(TCPFlags('frae') | TCPFlags('spuc'),
                         TCPFlags('fraespuc'))

    def test_or_5(self):
        self.assertRaises(TypeError, operator.or_, TCPFlags('frae'), 0)

    def test_or_6(self):
        self.assertRaises(TypeError, operator.or_, TCPFlags('frae'), '')

    def test_str_1(self):
        self.assertEqual(str(TCPFlags('fraespuc')), 'FSRPAUEC')

    def test_str_2(self):
        self.assertEqual(str(TCPFlags('fraesp')), 'FSRPAE')

    def test_padded_1(self):
        self.assertEqual(TCPFlags('fraespuc').padded(), 'FSRPAUEC')

    def test_padded_2(self):
        self.assertEqual(TCPFlags('fraesp').padded(), 'FSRPA E ')

    def test_bool_1(self):
        self.assertEqual(bool(TCPFlags('frae')), True)

    def test_bool_2(self):
        self.assertEqual(bool(TCPFlags('')), False)

    def test_matches_1(self):
        self.assertTrue(TCPFlags('fsrp').matches('fp'))

    def test_matches_2(self):
        self.assertFalse(TCPFlags('fsrp').matches('rpu'))

    def test_matches_3(self):
        self.assertTrue(TCPFlags('fsrp').matches('f/fa'))

    def test_matches_4(self):
        self.assertFalse(TCPFlags('fsrp').matches('f/fs'))

    def test_matches_5(self):
        self.assertRaises(TypeError, TCPFlags('fsrp').matches, 17)

    def test_matches_6(self):
        self.assertRaises(TypeError, TCPFlags('fsrp').matches, TCPFlags('fs'))

    def test_matches_7(self):
        self.assertRaises(ValueError, TCPFlags('fsrp').matches, 'fsqq')

    def test_silk_TCPFlagsConstruction(self):
        for i in range(0, 256):
            TCPFlags(i)
        TCPFlags('F')
        TCPFlags('S')
        TCPFlags('R')
        TCPFlags('P')
        TCPFlags('U')
        TCPFlags('E')
        TCPFlags('C')
        TCPFlags('  A  ')
        TCPFlags('FSRPUECA')
        TCPFlags('f')
        TCPFlags('s')
        TCPFlags('r')
        TCPFlags('p')
        TCPFlags('u')
        TCPFlags('e')
        TCPFlags('c')
        TCPFlags('  a  ')
        TCPFlags('fsrpueca')
        TCPFlags('aa')
        TCPFlags('')
        TCPFlags(TCPFlags(0))
        TCPFlags(TCPFlags(''))

    def test_silk_TCPFlagsBadValues(self):
        self.assertRaises(ValueError, TCPFlags, -1)
        self.assertRaises(ValueError, TCPFlags, 256)
        self.assertRaises(ValueError, TCPFlags, 'x')
        self.assertRaises(ValueError, TCPFlags, 'fsrpuecax')

    def test_silk_TCPFlagsString(self):
        self.assertEqual(str(TCPFlags('FSRPAUEC')), 'FSRPAUEC')
        self.assertEqual(str(TCPFlags('F')), 'F')
        self.assertEqual(str(TCPFlags('C')), 'C')
        self.assertEqual(str(TCPFlags('FSRAUEC')), 'FSRAUEC')
        self.assertEqual(TCPFlags('FSRPAUEC').padded(), 'FSRPAUEC')
        self.assertEqual(TCPFlags('F').padded(), 'F       ')
        self.assertEqual(TCPFlags('C').padded(), '       C')
        self.assertEqual(TCPFlags('FSRAUEC').padded(), 'FSR AUEC')

    def test_silk_TCPFlagsMembers(self):
        flags = TCPFlags('fsrpueca')
        self.assertEqual(flags.fin, True)
        self.assertEqual(flags.syn, True)
        self.assertEqual(flags.rst, True)
        self.assertEqual(flags.psh, True)
        self.assertEqual(flags.ack, True)
        self.assertEqual(flags.urg, True)
        self.assertEqual(flags.ece, True)
        self.assertEqual(flags.cwr, True)
        flags = TCPFlags('')
        self.assertEqual(flags.fin, False)
        self.assertEqual(flags.syn, False)
        self.assertEqual(flags.rst, False)
        self.assertEqual(flags.psh, False)
        self.assertEqual(flags.ack, False)
        self.assertEqual(flags.urg, False)
        self.assertEqual(flags.ece, False)
        self.assertEqual(flags.cwr, False)

    def test_silk_TCPFlagsConstants(self):
        self.assertEqual(TCPFlags('f'), TCP_FIN)
        self.assertEqual(TCPFlags('s'), TCP_SYN)
        self.assertEqual(TCPFlags('r'), TCP_RST)
        self.assertEqual(TCPFlags('p'), TCP_PSH)
        self.assertEqual(TCPFlags('a'), TCP_ACK)
        self.assertEqual(TCPFlags('u'), TCP_URG)
        self.assertEqual(TCPFlags('e'), TCP_ECE)
        self.assertEqual(TCPFlags('c'), TCP_CWR)

    def test_silk_TCPFlagsIntConv(self):
        self.assertEqual(int(TCP_FIN), 1)
        self.assertEqual(int(TCP_SYN), 2)
        self.assertEqual(int(TCP_RST), 4)
        self.assertEqual(int(TCP_PSH), 8)
        self.assertEqual(int(TCP_ACK), 16)
        self.assertEqual(int(TCP_URG), 32)
        self.assertEqual(int(TCP_ECE), 64)
        self.assertEqual(int(TCP_CWR), 128)

    def test_silk_TCPFlagsInequality(self):
        self.assert_(TCPFlags('f') == TCPFlags ('F'))
        self.assert_(TCPFlags('f') != TCPFlags ('FA'))

    def test_silk_TCPFlagsBinary(self):
        self.assertEqual(~TCPFlags('fsrp'), TCPFlags('ueca'))
        self.assertEqual(TCPFlags('fsrp') & TCPFlags('fpua'), TCPFlags('fp'))
        self.assertEqual(TCPFlags('frp') | TCPFlags('fa'), TCPFlags('frpa'))
        self.assertEqual(TCPFlags('frp') ^ TCPFlags('fa'), TCPFlags('rpa'))
        self.assert_(TCPFlags('a'))
        self.assert_(not TCPFlags(''))

    def test_silk_TCPFlagsMatches(self):
        self.assertEqual(TCPFlags('fsrp').matches('fs/fsau'), True)
        self.assertEqual(TCPFlags('fsrp').matches('fs/fspu'), False)
        self.assertEqual(TCPFlags('fs').matches('fs'), True)
        self.assertEqual(TCPFlags('fsa').matches('fs'), True)
        self.assertRaises(ValueError, TCPFlags('').matches, 'a/s/')
        self.assertRaises(ValueError, TCPFlags('').matches, 'x')
