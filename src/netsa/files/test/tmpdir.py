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

import os, stat

from os import path

from netsa.files import LocalTmpDir

def _is_fifo(f):
    return stat.S_ISFIFO(stat.S_IFMT(os.stat(f)[stat.ST_MODE]))

class LocalTmpDirTest(unittest.TestCase):

    def assert_locality(self, basedir=None):
        td = LocalTmpDir(dir=basedir)
        self.assert_(path.isdir(td.name))
        (d, n) = path.split(td.name)
        self.assert_(d == basedir)
        fn = td.tmp_filename()
        (d, n) = path.split(fn)
        self.assert_(d == td.name)
        self.assert_(not path.exists(fn))
        fh = td.tmp_file()
        (d, n) = path.split(fh.name)
        self.assert_(d == td.name)
        fn = fh.name
        self.assert_(path.isfile(fn))
        fh = None
        self.assert_(not path.exists(fn))
        fp = td.tmp_pipe()
        (d, n) = path.split(fp)
        self.assert_(d == td.name)
        self.assert_(_is_fifo(fp))
        return td

    def test_basic(self):
        """basic creation, deletion"""
        for d in ('/tmp', '/var/tmp'):
            td = self.assert_locality(d)
            name = td.name
            (bd, n) = path.split(name)
            self.assert_(path.exists(name))
            self.assert_(bd == d)
            td = None
            self.assert_(not path.exists(name))

if __name__ == "__main__":
    unittest.main()   

__all__ = ['LocalTmpDirTest']
