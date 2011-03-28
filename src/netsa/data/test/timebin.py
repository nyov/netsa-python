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

from datetime  import datetime, timedelta
from itertools import chain

from netsa.data import times

DEBUG = False

def date_str(date):
    return "%04d-%02d-%02d" % (date.year, date.month, date.day)

def printzip(ziplist):
    for (x,y) in ziplist:
        print "%s => %s" % (date_str(x), date_str(y))

date_begin   = datetime(2007, 12,  5, tzinfo=times.utc)
date_end     = datetime(2008,  2, 27, tzinfo=times.utc)
bin_begin    = datetime(2007, 12,  3, tzinfo=times.utc)
bin_end      = datetime(2008,  2, 25, tzinfo=times.utc)
bin_end_next = datetime(2008,  2, 25, tzinfo=times.utc)
bin_end_next = datetime(2008,  3,  3, tzinfo=times.utc)

if DEBUG:
    print "    begin: %s" % date_str(date_begin)
    print "      end: %s" % date_str(date_end)
    print "bin begin: %s" % date_str(bin_begin)

known = []
cursor = bin_begin
while (cursor <= bin_end):
    known.append(cursor)
    cursor += timedelta(weeks=1)

if DEBUG:
    print "KNOWN:"
    for x in known: print x

under_data = []
cursor = date_begin
while (cursor <= date_end):
    under_data.append(cursor)
    cursor += timedelta(weeks=2)
under_data_fluffed = [x for x in chain(*[iter((x,x)) for x in under_data])]
under_known = known[:]
under_map = zip(under_known, under_data_fluffed)

if DEBUG:
    print 'UNDER:'
    printzip(under_map)

over_data = []
cursor = date_begin
while (cursor <= date_end):
    over_data.append(cursor)
    cursor += timedelta(days=1)
over_known = [x for x in chain(*[iter((x,x,x,x,x,x,x)) for x in known])]
cursor = over_data[0]
while cursor != over_known[0]:
    over_known.pop(0)
    cursor -= timedelta(days=1)
over_map = zip(over_known, over_data)

if DEBUG:
    print "OVER:"
    printzip(over_map)

snap = times.dow_day_snapper(size=7)

class TimeBinTest(unittest.TestCase):

    def test_date_bin(self):
        self.assertEqual(snap.date_bin(date_begin), bin_begin)
        self.assertEqual(snap.date_bin(date_end),   bin_end)
        self.assertEqual(snap.date_bin(bin_begin),  bin_begin)

    def test_next_date_bin(self):
        self.assertEqual(snap.next_date_bin(date_begin), known[1])
        self.assertEqual(snap.next_date_bin(bin_begin),  known[1])
        self.assertEqual(snap.next_date_bin(date_end),   bin_end_next)

    def test_identity(self):
        seq = [x for x in snap.date_sequencer(known)]
        self.assertEqual(seq, zip(known, known))

    def test_undersample(self):
        seq = [x for x in snap.date_sequencer(under_data)]
        self.assertEqual(seq, under_map)

    def test_oversample(self):
        seq = [x for x in snap.date_sequencer(over_data)]
        self.assertEqual(seq, over_map)

if __name__ == "__main__":
    unittest.main()

__all__ = ['TimeBinTest']
