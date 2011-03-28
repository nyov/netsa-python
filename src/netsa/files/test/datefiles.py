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

from os       import path
from datetime import datetime

from netsa.files.datefiles import *

verbose = False

prefix    = 'whee'
extension = 'txt'

bogus = 'whee.2008-02-33:01:01:01.txt'

def permute():
    for prefix in ('', 'whee', '/hey/howdy/bubba'):
        for ext in ('', 'txt'):
            for d in (('2008',), ('2008', '07'), ('2008', '07', '11')):
                for sep in ('-', '.'):
                    dstr = sep.join(d)
                    if prefix:
                        dstr = "%s.%s" % (prefix, dstr)
                    if ext:
                        dstr = "%s.%s" % (dstr, ext)
                    yield dstr
        for sep in ('-', '.'):
            d = sep.join(['2008', '07', '11'])
            for t in (('10',), ('10', '11'), ('10', '11', '12')):
                tstr = ':'.join(t)
                dstr = ':'.join([d, tstr])
                yield dstr


class DateFileTest(unittest.TestCase):

    def test_split(self):
        for file in permute():
            if verbose:
                print >> sys.stderr, file
            (d, f) = path.split(file)
            (dir, chop) = split_on_date(file)
            if d:
                self.assertEquals(d, dir)
            d = date_from_file(file)
            self.assert_(isinstance(d, datetime))
        if verbose:
            print >> sys.stderr, bogus
        self.assertRaises(DateFileParseError, date_from_file, bogus)


if __name__ == "__main__":
    unittest.main()

__all__ = ['DateFileTest']
