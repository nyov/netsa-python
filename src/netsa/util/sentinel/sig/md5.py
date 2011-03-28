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

import re
from os import path
from subprocess import Popen, PIPE

from netsa.util.sentinel.sig import SigFacility, SigFacilityError

def md5_facility():
    """
    Factory routine for returning an instance of the best MD5 hash
    signature generator available on the system. Currently this means
    the openssl command, md5sum command, or native md5 python module, in
    order of preference.
    """
    for c in (SigMD5OpenSSL, SigMD5Sum, SigMD5Native):
        try:
            return c()
        except SigFacilityError:
            continue
    raise SigFacilityError, "no md5 facilities found"


class SigMD5OpenSSL(SigFacility):
    """
    MD5 hash signature facility based on the 'openssl' command
    line tool.
    """

    name    = 'openssl'
    command = path.join('/usr/bin', name)

    def sig(self, file):
        stdout, stderr = self.sig_cmd_output(file)
        sig = stdout.strip()
        if not sig:
            msg = "problem generating %s md5 for %s" % (self.name, file)
            if stdout:
                msg += " : %s" % stdout
            raise SigFacilityError, msg
        return sig

    def version(self):
        if self.ver is None:
            try:
                cmd = [self.command, 'version']
                p = Popen(cmd, stdin=None, stdout=PIPE, shell=False)
                self.ver = p.communicate()[0]
                self.ver.strip()
            except OSError:
                pass
        return self.ver

    def sig_cmd_output(self, file):
        cmd = [self.command, 'md5']
        fh = open(file, 'r')
        p = Popen(cmd, stdin=fh, stdout=PIPE, shell=False)
        return p.communicate()


class SigMD5Sum(SigFacility):
    """
    MD5 hash signature facility based on the 'md5sum' command
    line tool.
    """

    name    = 'md5sum'
    command = path.join('/usr/bin', name)

    def sig(self, file):
        stdout, stderr = self.sig_cmd_output(file)
        sig = None
        for line in re.split('\n+', stdout):
            fields = re.split('\s+', line.strip())
            sig = fields[0]
            if len(sig) == 32:
                break
        if not sig:
            msg = "problem generating %s for %s" % (self.name, file)
            if stdout:
                msg += " : %s" % stdout
            raise StampFacilityError, msg
        return sig

    def version(self):
        if self.ver is None:
            try:
                cmd = [self.command, '--version']
                p = Popen(cmd, stdin=None, stdout=PIPE, shell=False)
                self.ver = p.communicate()[0]
                self.ver.strip()
            except OSError:
                pass
        return self.ver

    def sig_cmd_output(self, file):
        fh = open(file, 'r')
        p = Popen(self.command, stdin=fh, stdout=PIPE, shell=False)
        return p.communicate()

class SigMD5Native(SigFacility):
    """
    MD5 hash signature facility based on the python md5 module.
    """

    name = 'python.md5'

    def sig(self, file):
        fh = open(file, 'rb')
        hasher = self._new()
        for chunk in fh:
            hasher.update(chunk)
        fh.close()
        return hasher.hexdigest()

    def version(self):
        if self.ver is None:
            try:
                import hashlib
                self._new = self._hashlib_new
                self.ver = True
            except ImportError:
                try:
                    import md5
                    self._new = self._md5_new
                    self.ver = True
                except ImportError:
                    pass
        return self.ver

    def _md5_new(self):
        return md5.new()

    def _hashlib_new(self):
        return hashlib.md5()

###

__all__ = [

    'md5_facility',

    'SigMD5OpenSSL',
    'SigMD5Sum',
    'SigMD5Native',

]
