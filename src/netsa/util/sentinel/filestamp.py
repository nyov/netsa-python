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

from netsa.util.sentinel             import Sentinel, DEBUG
from netsa.util.sentinel.sig.md5     import md5_facility
from netsa.util.sentinel.ledger.file import FileLedger
from netsa.util.sentinel.audit.file  import FileAuditor, FileSigAuditor

###

class FileSentinel(Sentinel):
    """
    Sentinel subclass specifically tailored to monitor the status of
    files on the filesystem. The state of these files is also stored on
    the filesystem in a signature file.
    """

    def __init__(self, sig_file, base_path=None, **kwargs):
        """
        Returns a FileSentinel object given the provided signature file.
        Current state and updates are read from and written to this
        signature file.

        The optional parameter 'deep_check' is a boolean that indicates
        whether more resource-intensive checks should always be
        performed by auditors (default: False). This value is not used
        directly by this class, but is potentially passed down to
        individual auditor instances upon their creation.

        The optional parameter 'base_path' (default: None) is used when
        building keys for the signature file -- the keys in this case
        are the actual pathnames of the files. If base_path is provided,
        the keys will be relative to this path. Once again, this is not
        used directly by this class, but is passed down to individual
        auditor instances.
        """

        self.sig_file    = path.abspath(sig_file)
        self.base_path   = base_path
        self.sig_fac     = None
        Sentinel.__init__(self, **kwargs)

    def make_auditors(self, files, sigs=True):
        """
        Factory method for building auditors for each of the
        provided files.

        The 'files' parameter is a list of file paths for which auditor
        instances will be returned.
        """
        return tuple([self.make_auditor(f, sigs=sigs) for f in files])

    def make_auditor(self, file, sigs=True):
        """
        Factory method that buids an auditor for the provided file.

        The optional 'sigs' parameter (default: True) controls whether a
        hash signature will be utilized during the audit. When True, a
        signature-enabled auditor instance (FileSigAuditor) is produced.
        When False, an instance that only monitors inode status
        (FileAuditor) is produced for cases where a hash signature is
        never desired.
        """
        if sigs:
            return FileSigAuditor(file,
                base_path=self.base_path, deep_check=self.deep_check,
                sig_fac=self.sig_facility())
        else:
            return FileAuditor(file,
                base_path=self.base_path, deep_check=self.deep_check)

    def make_ledger(self):
        """
        Returns a ledger instance for storing and retreiving states.
        This is currently an instance of FileLedger -- states are saved
        in a file.
        """
        return FileLedger(self.sig_file)

    def sig_facility(self):
        """
        Returns a signature facility for generating hash signatures for
        files. Currently this is an md5 facility that returns md5 sums
        for files.
        """
        if not self.sig_fac:
            self.sig_fac = md5_facility()
        return self.sig_fac

###

__all__ = [ 'FileSentinel' ]
