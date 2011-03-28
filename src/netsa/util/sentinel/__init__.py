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

import sys

DEBUG = False

from netsa.util.sentinel.audit  import *
from netsa.util.sentinel.ledger import *

###

class Sentinel(object):
    """
    Base class for monitoring changes in the source inputs of a
    processing pipeline.
    """

    def __init__(self, deep_check=False, cache_level=None):
        """
        Returns a Sentinel object that monitors changes in resources of
        interest.

        The optional parameter 'deep_check' (default: False) is
        available for subclasses that utilize both intensive and less
        intensive status checks.

        The optional parameter 'cache_level' enables memeoized audit
        results and ledger loads. A value of 1 enables per-instance
        caches and a value of 2 or greater enables per-class caches (in
        the latter case, every sentinel instance of a particular class
        share the same cache). Uniqueness is determined by the
        __cachekey__() method in audit and ledger instances.

        This class by itself is not particularly useful. It must be
        subclassed in order to do anything interesting.
        """
        self.deep_check  = deep_check
        self.cache_level = cache_level
        self.ledger      = self.make_ledger()
        if self.cache_level:
            self.clear_cache()

    def load(self):
        """
        Returns the stored state of input sources as a dictionary. The
        load() method of the ledger is ultimately responsible for
        retreiving the stored state.
        """
        try:
            return self.ledger.load()
        except LedgerLoadRecoverable, e:
            print >> sys.stderr, e
            return {}
        except LedgerNotFoundError, e:
            if DEBUG:
                print >> sys.stderr, e
            return {}

    def store(self, auditors, stamps=None):
        """
        Stores the current state of inputs. If any of the current states
        are already known, they can be provided in the optional 'stamps'
        dictionary. Any states that are not present or incomplete will
        be calculated before storage takes place.
        """
        if not stamps:
            stamps = {}
        for auditor in auditors:
            key = auditor.key()
            try:
                # we've been handed a stamp, just make sure it's well-
                # formed (without recalculating the stamp)
                stamps[key] = auditor.validate(stamps[key])
            except (KeyError, AuditStampError), e:
                # calculate the stamp from scratch
                if DEBUG:
                    msg = "stamp key %s (%s)" % (key, e)
                    print >> sys.stderr, msg
                stamps[key] = auditor.stamp()
        self.ledger.store(stamps)

    def changed(self, auditors, stamps=None,
                subset=False, abort_on_changed=True):
        """
        Determine whether anything has changed between the stored state
        of inputs and their current state. Returns a tuple of four values:

          1. changed (boolean)
          2. refresh required (boolean)
          3. current states (tuple of stamps per auditor)
          4. messages (tuple of tuple pairs where each pair is an
             auditor that detected a change along with an accompanying
             explanation)

        If the optional 'abort_on_changed' parameter is True, processing
        ceases after the first auditor that detects a change. Should
        this occur, the states that are returned might not represent the
        full set of states across all auditors.

        The actual comparison for each source is performed by the
        audit() method of each provided source auditor.
        """
        initial_fail = False
        if not stamps:
            stamps = self.load()
            if not stamps:
                if not auditors:
                    # no stamps, no auditors -- no change
                    return False, False, (), ()
                else:
                    initial_fail = "no stamps present"
        if abort_on_changed and not subset and len(auditors) != len(stamps):
                lengths = (len(auditors), len(stamps))
                initial_fail = "file/audit count mismatch (%d/%d)" % lengths
                ak = set([x.key() for x in auditors])
                sk = set(stamps.keys())
                if DEBUG:
                    print >> sys.stderr, initial_fail
                    print >> sys.stderr, 'auditors ', len(auditors)
                    print >> sys.stderr, 'stamps   ', len(stamps)
                    print >> sys.stderr, 'ak       ', len(ak)
                    print >> sys.stderr, 'sk       ', len(sk)
        if initial_fail:
            return True, True, None, ((None, initial_fail),)
        audit  = self.auditor(auditors, stamps, subset=subset)
        chnged = refresh = False
        msgs = []
        actuals = {}
        missing = {}
        for auditor, match, actual, msg in audit:
            if actual:
                actuals[auditor.key()] = actual
            if msg:
                msgs.append((auditor, msg))
            if match is None:
                # a match value of None is interpreted as a pseudo
                # match; i.e., the 'deep' check matched but the
                # 'shallow' check did not. Example: a file with a ctime
                # mismatch but an md5 signature match.
                refresh = True
            elif not match:
                chnged = refresh = True
                if abort_on_changed:
                    break
        return chnged, refresh, actuals, tuple(msgs)

    def auditable(self):
        """
        Returns a status indicating whether the sentinel is auditable or
        not; in particular this means whether the ledger has ever been
        initialized or saved. A non-initialized ledger is not in the
        same state as a merely empty ledger -- the former is an
        unknown state, whereas the latter is an assertion that no
        audit targets exist.
        """
        try:
            self.ledger.load()
        except LedgerNotFoundError, e:
            return False
        return True

    def auditor(self, auditors, stamps=None, subset=False):
        """
        Returns a visitor iterator for the provided source auditors.
        Each source auditor will compare the current state with the
        stored state and return a tuple of four values:

            1. the source auditor in question
            2. whether the states matched for this source
            3. the current state of the source as generated during the
               audit
            4. an explanatory message in cases of mismatch

        The inspection step will invoke the audit() method for each
        source auditor, which is generally overridden in source-
        specific subclasses.
        """
        if not stamps:
            stamps = self.load()
        audits_seen = set()
        for a in auditors:
            audits_seen.add(a.key())
            match, msg, actual = True, None, None
            try:
                actual = self.inspect(a, stamps)
            except AuditMismatch, e:
                src, msg, actual = e
                match = False
            except (AuditStampNotFound, AuditSourceNotFound), e:
                src, msg, actual = e
                match = False
            except AuditRefresh, e:
                src, msg, actual = e
                match = None
            yield a, match, actual, msg
        if not subset:
            for s in stamps:
                if s not in audits_seen:
                    yield None, False, None, "stamp not found (%s)" % s

    def inspect(self, auditor, stamps=None):
        """
        Front end method invoked for each source auditor during an audit
        check. After some inital bookeeping, it invokes the audit()
        method for the given auditor.
        """
        if not stamps:
            stamps = self.load()
        stamp = None
        try:
            stamp = stamps[auditor.key()]
        except KeyError:
            pass
        if not stamp:
            # catch it if stamps[key] is None/False also
            msg = "no record"
            raise AuditStampNotFound, (auditor, msg, None)
        return self.audit(auditor, stamp)

    def audit(self, auditor, stamp):
        """
        Invokes the audit method for the provided auditor, passing the
        given stamp as a parameter. The primary reason this is here is
        to provide an opportunity for subclasses to override.
        """
        return auditor.audit(stamp)

    ### cache magic

    def _cached_audit(self, auditor, stamp):
        cache_key = (auditor.__class__, hash(auditor), hash(stamp))
        cache = self.cache()
        try:
            res = cache.audits[cache_key]
            cache.audit_hits += 1
            if isinstance(res, Exception):
                raise res
            else:
                return res
        except KeyError:
            cache.audit_misses += 1
            try:
                actual = self._fresh_audit(auditor, stamp)
                cache.audits[cache_key] = actual
                return actual
            except (AuditMismatch, AuditRefresh), e:
                cache.audits[cache_key] = e
                raise

    def _cached_load(self):
        cache_key = (self.ledger.__class__, hash(self.ledger))
        cache = self.cache()
        if cache_key in cache.loads:
            cache.load_hits += 1
            return cache.loads[cache_key]
        else:
            cache.load_misses += 1
            stamps = self._fresh_load()
            cache.loads[cache_key] = stamps
            return stamps

    def _cached_store(self, auditors, stamps=None):
        self._fresh_store(auditors, stamps)
        self.clear_cache()

    def cache(self):
        try:
            return self._cache.cache()
        except AttributeError:
            return None

    def clear_cache(self):
        if not self.cache_level:
            return
        if self.cache_level > 1:
            self._cache = SentinelSharedCache()
        else:
            self._cache = SentinelPrivateCache()
        # the method swapping is so that derived classes will
        # transparently benefit from cache behavior
        if self.audit != self._cached_audit:
            self.audit, self._fresh_audit = self._cached_audit, self.audit
        if self.load != self._cached_load:
            self.load,  self._fresh_load  = self._cached_load,  self.load
        if self.store != self._cached_store:
            self.store,  self._fresh_store  = self._cached_store,  self.store

class SentinelCache(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self.audits       = {}
        self.loads        = {}
        self.audit_hits   = 0
        self.audit_misses = 0
        self.load_hits    = 0
        self.load_misses  = 0

class SentinelPrivateCache(object):

    def __init__(self):
        self._cache = SentinelCache()
        self.clear()

    def cache(self):
        return self._cache

    def clear(self):
        self.cache().clear()

class SentinelSharedCache(SentinelPrivateCache):

    _cache = SentinelCache()
    _cache.clear()

    def __init__(self):
        pass

###

__all__ = ['Sentinel']
