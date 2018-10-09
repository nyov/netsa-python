# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

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
