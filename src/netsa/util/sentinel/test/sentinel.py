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

import os, stat, sys

from os import path

from netsa.util.sentinel.filestamp import FileSentinel

try:
    import hashlib
    new_md5 = hashlib.md5
except ImportError:
    import md5
    new_md5 = md5.new

test_dir = path.dirname(__file__)
myfile = __file__
if myfile.endswith('pyc'):
    myfile = myfile[:-1]
files = (myfile, path.join(test_dir, '__init__.py'))

def file_ctime_size(file):
    ctime = int(path.getctime(file))
    size  = path.getsize(file)
    return ctime, size


def file_md5(file):
    digest = new_md5()
    fh = open(file, 'r')
    for line in fh:
        digest.update(line)
    return digest.hexdigest()

def stamp_correct(file):
    return file_ctime_size(file) + (file_md5(file),)

def stamp_sig_mismatch(file):
    stamp = list(file_ctime_size(file))
    stamp.append('0' * 32)
    return tuple(stamp)

def stamp_ctime_mismatch(file):
    stamp = list(stamp_correct(file))
    stamp[0] = 0
    return tuple(stamp)

def stamp_size_mismatch(file):
    stamp = list(stamp_correct(file))
    stamp[1] = 0
    return tuple(stamp)

def stamps_correct(files):
    return dict([(x, stamp_correct(x)) for x in files])

def stamps_sig_mismatch(files):
    return dict([(x, stamp_sig_mismatch(x)) for x in files])

def stamps_size_mismatch(files):
    return dict([(x, stamp_size_mismatch(x)) for x in files])

def stamps_ctime_mismatch(files):
    return dict([(x, stamp_ctime_mismatch(x)) for x in files])

def stamps_sig_ctime_mismatch(files):
    stamps = dict([(x, stamp_ctime_mismatch(x)) for x in files])
    for f in stamps:
        s = list(stamps[f])
        s[-1] = '0' * 32
        stamps[f] = tuple(s)
    return stamps

class SentinelTest(unittest.TestCase):

    def _prepare_audit(self, stamps, cache_level=None, deep_check=False):
        bigaudit = FileSentinel(
            '/dev/null', cache_level=cache_level, deep_check=deep_check)
        auditors = tuple(bigaudit.make_auditors(files, sigs=True))
        stamps   = dict(stamps)
        self.assert_(len(stamps) == len(auditors), 'stamps vs auditors')
        return bigaudit, auditors, stamps

    def _cache_present(self, bigaudit, auditors, stamps, cache_level=None):
        if not cache_level:
            self.assert_(not bigaudit.cache(), "cache not present")
            return
        otheraudit, other_auditors, other_stamps = \
            self._prepare_audit(stamps, cache_level=cache_level)
        # bigaudit was audited once already
        bigcache = bigaudit.cache()
        self.assert_(bigcache, "cache present")
        ac = len(auditors)
        count = 3
        for x in range(count):
            bigaudit.changed(auditors, stamps)
            otheraudit.changed(other_auditors, other_stamps)
        # twice more time for other, putting it one ahead of big
        otheraudit.changed(other_auditors, other_stamps)
        otheraudit.changed(other_auditors, other_stamps)
        othercache = otheraudit.cache()
        self.assert_(othercache, 'other cache present')
        if cache_level <= 1:
            self.assert_(len(bigcache.audits) == ac)
            self.assert_(bigcache.audit_hits == ac*count)
            self.assert_(bigcache.audit_misses == ac)
            # other
            self.assert_(len(othercache.audits) == ac)
            self.assert_(othercache.audit_hits == ac*count + 2)
            self.assert_(othercache.audit_misses == ac)
        else:
            for c in (bigcache, othercache):
                self.assert_(len(c.audits) == ac)
                self.assert_(c.audit_hits == 2*ac*count + 2*ac)
                self.assert_(c.audit_misses == ac)

    def _test_audit_correct(self, stamps, cache_level=None):
        bigaudit, auditors, stamps = \
            self._prepare_audit(stamps, cache_level=cache_level)
        for a, match, actual, msg in bigaudit.auditor(auditors, stamps):
            self.assert_(match, 'audit match')
            self.assert_(msg is None, 'no msg on match')
        self._cache_present(bigaudit, auditors, stamps, cache_level=cache_level)

    def _test_audit_sigfail(self, stamps, cache_level=None, deep_check=False):
        bigaudit, auditors, stamps = self._prepare_audit(
            stamps, cache_level=cache_level, deep_check=deep_check)
        for a, match, actual, msg in bigaudit.auditor(auditors, stamps):
            if deep_check:
                self.assert_(not match, 'audit not match (sig, deep)')
            else:
                self.assert_(match, 'audit match (bad sig no deep)')
        self._cache_present(bigaudit, auditors, stamps, cache_level=cache_level)

    def _test_audit_ct2sigfail(self, stamps, cache_level=None):
        bigaudit, auditors, stamps = self._prepare_audit(
            stamps, cache_level=cache_level, deep_check=False)
        for a, match, actual, msg in bigaudit.auditor(auditors, stamps):
            self.assert_(not match, 'audit ctime2sig fail')
        self._cache_present(bigaudit, auditors, stamps, cache_level=cache_level)

    def _test_audit_sizefail(self, stamps, cache_level=None):
        bigaudit, auditors, stamps = self._prepare_audit(
            stamps, cache_level=cache_level, deep_check=False)
        for a, match, actual, msg in bigaudit.auditor(auditors, stamps):
            self.assert_(not match, 'audit not match (size)')
        self._cache_present(bigaudit, auditors, stamps, cache_level=cache_level)

    def _test_audit_ctimerefresh(self, stamps, cache_level=None):
        bigaudit, auditors, stamps = self._prepare_audit(
            stamps, cache_level=cache_level, deep_check=False)
        for a, match, actual, msg in bigaudit.auditor(auditors, stamps):
            self.assert_(match is None, 'audit is None (ctime miss, sig hit)')
        self._cache_present(bigaudit, auditors, stamps, cache_level=cache_level)

    ###

    def test_basic(self):
        """basic audit test (FileSigAuditor)"""
        self._test_audit_correct(stamps_correct(files))

    def test_sigfail(self):
        """sig fail audit test (FileSigAuditor)"""
        stamps = stamps_sig_mismatch(files)
        self._test_audit_sigfail(stamps_sig_mismatch(files), deep_check=False)
        self._test_audit_sigfail(stamps_sig_mismatch(files), deep_check=True)
        stamps = stamps_sig_ctime_mismatch(files)
        self._test_audit_ct2sigfail(stamps)

    def test_sizefail(self):
        """size fail audit test (FileSigAuditor)"""
        stamps = stamps_size_mismatch(files)
        self._test_audit_sizefail(stamps)

    def test_ctimerefresh(self):
        """ctime refresh audit test (FileSigAuditor)"""
        stamps = stamps_ctime_mismatch(files)
        self._test_audit_ctimerefresh(stamps)

    ###

    def test_cache1_basic(self):
        """basic audit test cache level 1 (FileSigAuditor)"""
        self._test_audit_correct(stamps_correct(files), cache_level=1)

    def test_cache2_basic(self):
        """basic audit test cache level 2 (FileSigAuditor)"""
        self._test_audit_correct(stamps_correct(files), cache_level=2)

if __name__ == "__main__":
    unittest.main()   

__all__ = ['SentinelTest']
