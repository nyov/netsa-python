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

from os import path

from netsa.files import relpath

from netsa.util.sentinel \
    import DEBUG, SentinelAuditor, \
           AuditStampError, AuditSourceError, \
           AuditSourceNotFound, AuditNotFound, AuditMismatch, AuditRefresh

from netsa.util.sentinel.sig.md5 import md5_facility

###

class FileAuditCtimeMismatch(AuditMismatch):
    pass

class FileAuditSizeMismatch(AuditMismatch):
    pass

###

class FileAuditor(SentinelAuditor):
    """
    A sentinel auditor that tracks and compares the state of a file
    based on file size and the reported creation time of the inode. If
    either of these properties have changed, the file is considered to
    have changed.
    """

    def __init__(self, file, base_path=None, deep_check=False):
        """
        Returns a FileAuditor instance for the given file.

        The optional parameter 'base_path' is used as a basis of
        comparision in the key() method.

        The optional parameter 'deep_check' is to maintain
        consistency with the SentinelAuditor API, but is not actually
        used in this class.
        """
        self.file       = path.abspath(file)
        self.base_path  = base_path
        self.deep_check = deep_check
        self.key_file   = None

    def key(self):
        """
        Returns the key to use in the ledger. If this object has a
        'base_path' attribute, the key is the path relative to this base
        path. Otherwise it is the absolute pathname to the file.
        """
        if self.key_file is None:
            if self.base_path:
                self.key_file = relpath(self.file, self.base_path)
            else:
                self.key_file = self.file
        return self.key_file

    def stamp(self):
        """
        Returns the current state of the file in the form of a tuple
        pair: ctime and size.
        """
        ctime = int(path.getctime(self.file))
        size  = path.getsize(self.file)
        return ctime, size

    def audit(self, stamp):
        """
        Compares the provided stamp (ctime, size) with the current state
        of the file. If they match, the current stamp is returned. If
        they do not match, an exception will be raised with the current
        stamp and a diagnostic message as arguments.
        """
        if not path.exists(self.file):
            raise AuditSourceNotFound, (self, "missing", None)
        if not path.isfile(self.file):
            raise AuditSourceError, (self, "not a file", None)
        try:
            self.validate(stamp)
        except AuditStampError, e:
            msg = "sig type mismatch"
            if DEBUG:
                msg += " %s" % e
            raise AuditMismatch, (self, msg, None)
        stored_ctime, stored_size = stamp
        actual = ctime, size = self.stamp()
        if size != stored_size:
            msg = ('size', size, stored_size)
            raise FileAuditSizeMismatch, (self, msg, actual)
        if ctime != stored_ctime:
            msg = "ctime change"
            raise FileAuditCtimeMismatch, (self, msg, actual)
        return actual

    def validate(self, stamp):
        """
        Ensure that a stamp consists of a tuple or list of two integer
        values representing ctime and size.
        """
        try:
            ctime, size = stamp
        except (ValueError, TypeError):
            raise AuditStampError, stamp
        if not str(ctime).isdigit() and str(size).isdigit():
            raise AuditStampError, stamp
        return stamp

    def __cachekey__(self):
        return self.file

class FileSigAuditor(FileAuditor):
    """
    A subclass of FileAuditor that adds hash signature checking of the
    file contents to the creation time and size tracking aspects of
    FileAuditor. If the size or signature of the file has changed, the
    file is considered to have changed.
    """

    def __init__(self, file, base_path=None, deep_check=False, sig_fac=None):
        """
        Returns a FileSigAuditor instance for the given file.

        The optional parameter 'base_path' (default: None) is used as a
        basis of comparision in the key() method.

        The optional parameter 'deep_check' (default: None) determines
        whether signature checks are forced -- normally a signature
        check only happens if the size or creation time of the file
        have changed.

        The optional 'sig_fac' parameter (default: None) is for
        providing a pre-existing signature facility object; if not
        provided, a new one is created for this instance.
        """
        FileAuditor.__init__(self, file, base_path, deep_check)
        self.sig_fac = sig_fac

    def stamp(self):
        """
        Returns the current state of the file in the form of a tuple
        pair: ctime, size, and hash signature
        """
        if DEBUG:
            print >> sys.stderr, "MD5(%s)" % self.key()
        sig = self.sig_for_file()
        ctime, size = FileAuditor.stamp(self)
        return ctime, size, sig

    def audit(self, stamp):
        """
        Compares the provided stamp (ctime, size, sig) with the current
        state of the file.

        If ctime and size have not changed, no signature check is
        performed (the stored signature is returned with results without
        having been verified).

        If size or signature are different, an exception will be raised
        with the current stamp and a diagnostic message as arguments.

        If the ctime (but not size) has changed, a signature check is
        performed -- if the signature matches, then a refresh exception
        is raised which can be useful for eliminating false positives on
        changes. Otherwise a regular mismatch exception is raised.
        """
        try:
            self.validate(stamp)
        except AuditStampError, e:
            msg = "sig type mismatch"
            if DEBUG:
                msg += " %s" % e
            raise AuditMismatch, (self, msg, None)
        stored_ctime, stored_size, stored_sig = stamp
        cts_stamp = (stored_ctime, stored_size)
        if self.deep_check:
            if not path.exists(self.file):
                raise AuditSourceNotFound, (self, "missing", None)
            if not path.isfile(self.file):
                raise AuditSourceError, (self, "not a file", None)
            actual = ctime, size, sig = self.stamp()
            if sig != stored_sig:
                msg = "md5 mismatch"
                raise AuditMismatch, (self, msg, actual)
        else:
            try:
                # use an instance here so audit() doesn't use our own
                # stamp(), validate()
                subauditor = FileAuditor(self.file)
                cts_actual = subauditor.audit(cts_stamp)
                actual = cts_actual + (stored_sig,)
            except FileAuditCtimeMismatch, e:
                actual = self.stamp()
                sig = self.sig_for_file()
                actual += (sig,)
                if sig != stored_sig:
                    msg = "ctime induced md5 mismatch"
                    raise AuditMismatch, (self, msg, actual)
                else:
                    msg = "meta refresh needed"
                    raise AuditRefresh, (self, msg, actual)
        return actual

    def validate(self, stamp):
        """
        Ensure that a stamp consists of a tuple or list of three values:
        an integer ctime, integer size, and string signature.
        """
        try:
            ctime, size, sig = stamp
        except (ValueError, TypeError):
            raise AuditStampError, stamp
        try:
            FileAuditor.validate(self, (ctime, size))
        except AuditStampError:
            raise AuditStampError, stamp
        if not isinstance(sig, str):
            raise AuditStampError, stamp
        return stamp

    def sig_for_file(self):
        """
        Returns the current hash signature of the file. The actual
        calculation is performed by the signature facility instance.
        """
        return self.sig_facility().sig(self.file)

    def sig_facility(self):
        """
        Returns the current signature facility instance if present,
        otherwise creates one and caches it.
        """
        if not self.sig_fac:
            self.sig_fac = md5_facility()
        return self.sig_fac

__all__ = [

    'FileAuditor',
    'FileSigAuditor',

    'FileAuditCtimeMismatch',
    'FileAuditSizeMismatch',

]
