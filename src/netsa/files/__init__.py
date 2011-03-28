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

from __future__ import division

import atexit
import math
import os
import os.path
import re
import sys
import time
import errno

from tempfile import NamedTemporaryFile, gettempdir

## path manipulation ###################################################

def relpath(p, base):
    """
    Given a target path along with a reference path, return the
    relative path from the target to the reference.

    This is a logical operation that does not consult the physical
    filesystem.

    :func:`os.path.relpath` in Python 2.6 adds something similar to this.
    """
    if base is None:
        return p
    p_parts = filter(lambda x: x != '', p.split('/'))
    b_parts = filter(lambda x: x != '', base.split('/'))
    if len(p_parts) < 2 or len(b_parts) < 2 or p_parts[1] != b_parts[1]:
        return p
    while p_parts and b_parts and p_parts[0] == b_parts[0]:
        p_parts.pop(0)
        b_parts.pop(0)
    if b_parts:
        prefix = ['..' for x in range(len(b_parts))]
        return os.path.join(os.path.join(*prefix), os.path.join(*p_parts))
    elif p_parts:
        return os.path.join(*p_parts)
    else:
        return p

def is_relpath(p, base):
    """
    Given a target path along with a base reference path, return whether
    or not the base path subsumes the target path.

    This is a logical operation that does not consult the physical
    filesystem.
    """
    return p != relpath(p, base)

## temporary directories ###############################################

class LocalTmpDirError(Exception):
    """
    Raised when an unrecoverable error occurs within
    :class:`LocalTmpDir`.
    """
    pass

class LocalTmpDir(object):
    """
    Provides ephemeral temporary directories, similar to
    :class:`tempfile.NamedTemporaryFile`. The resulting directory and
    all of its contents will be unlinked when the object goes out of
    scope.

    The parameter *prefix* is passed as the *prefix* parameter to
    :class:`tempfile.NamedTemporaryFile` when temporary files are
    created within the temporary directory.

    The parameter *create* controls whether the temporary directory is
    actually created. If you want to create the directory manually,
    you can use the method :meth:`assert_dir`.

    The parameter *verbose* controls whether status messages (such as
    creation/deletion of files and dirs) are printed to ``stderr``.

    The parameter *autodelete* controls whether the temporary
    directory, and all its contents, are deleted once the
    :class:`LocalTmpDir` object goes out of scope. (mostly useful for
    debugging)
    """

    def __init__(self, dir=None, prefix='tmp', create=True,
                 verbose=False, autodelete=True):
        self.verbose    = verbose
        self.autodelete = autodelete
        self.basedir    = None
        self._prefix    = prefix
        if dir:
            dir = os.path.abspath(dir)
            if os.path.isfile(dir):
                dir = os.path.dirname(dir)
            if not os.path.isdir(dir):
                raise LocalTmpDirError, "not a dir: %s" % dir
            self.basedir = dir
        self.name = NamedTemporaryFile(dir=dir, prefix=self.prefix()).name
        if not self.basedir:
            self.basedir = os.path.dirname(self.name)
        if create:
            self.assert_dir()

    def __str__(self):
        return self.name

    def __repr__(self):
        dc = fc = 0
        for (dir, subdirs, files) in os.walk(self.name, topdown=False):
            if dir == self.name:
                continue
            dc += 1
            fc += len(files)
        return "<tmp dir (%d subdirs, %d files) '%s'>" % (self.name, dc, fc)

    def prefix(self):
        """
        Returns the value of 'prefix' that is passed to
        :class:`tempfile.NamedTemporaryFile`.
        """
        prefix = self._prefix
        if not prefix.endswith('.'):
            prefix += '.'
        prefix += "%s." % os.getpid()
        return prefix

    def assert_dir(self):
        """
        Checks to see if this temp dir exists and creates it if not.
        Normally this happens during object creation.
        """
        tdir = os.path.dirname(self.name)
        if not os.path.exists(tdir) or not os.path.isdir(tdir):
            raise LocalTmpDirError, "parent not a dir: %s" % tdir
        if not os.path.isdir(self.name):
            if self.verbose:
                msg = "%d: create %s" % (os.getpid(), self.name)
                print >>sys.stderr, msg
            os.mkdir(self.name)
        return self.name

    def tmp_filename(self):
        """
        Returns a new temporary filename within this temp dir.
        """
        return self.tmp_file().name

    def tmp_file(self):
        """
        Returns a :class:`tempfile.NamedTemporaryFile` object within
        within this temp dir.
        """
        return NamedTemporaryFile(dir=self.name)

    def tmp_pipe(self):
        """
        Returns the filename of a new named pipe within within this
        temp dir.
        """
        np = self.tmp_filename()
        os.mkfifo(np)
        return np

    def __del__(self):
        if not os.path.isdir(self.name):
            return
        if self.name == self.basedir:
            if self.verbose:
                print >>sys.stderr, os.getpid(), \
                    ": no unlink, .name is .basedir ", self.name
            return
        (p, s) = os.path.split(self.name)
        if not s.startswith(self.prefix()):
            if self.verbose:
                print >>sys.stderr, os.getpid(), "do not own: ", self.name, s
            return
        pdir = os.path.dirname(self.name)
        for (dir, subdirs, files) in os.walk(self.name, topdown=False):
            rp = relpath(dir, pdir)
            for f in files:
                if self.verbose:
                    msg = "unlink %s" % os.path.join(rp, f)
                    if not self.autodelete:
                        msg = "no " + msg
                    msg = "%d: %s" % (os.getpid(), msg)
                    print >>sys.stderr, msg
                if self.autodelete:
                    os.unlink(os.path.join(dir, f))
            if self.verbose:
                msg = "rmdir  %s" % rp
                if not self.autodelete:
                    msg = "no " + msg
                msg = "%d: %s" % (os.getpid(), msg)
                print >>sys.stderr, msg
            if self.autodelete:
                os.rmdir(dir)

## directory based locking #############################################

DEFAULT_LOCK_DIR = '/var/tmp'
LOCK_ATTEMPTS = 3
LOCK_WAIT_TIME = 2

class DirLockBlock(Exception):
    """
    Raised when an attempt to lock a directory is blocked for too long
    a time by another process holding the lock.
    """
    pass

def remove_pidfile(file):
    try:
        os.unlink(file)
    except OSError:
        pass

def remove_lockdir(dir):
    try:
        os.rmdir(dir)
    except OSError:
        pass

class DirLocker(object):
    """
    Provides cheap cross-process locking via
    ``mkdir``/``rmdir``. *name* is the token identifying the
    application group. *dir* optionally specifies the directory in
    which to establish the lock (defaults to ``'/var/tmp'`` or some
    sensible temp dir name). If *seize* is ``True`` and the requested
    lock appears to have been orphaned, a new lock is established and
    the old lock debris is removed.

    This is not an infallible locking solution. This is advisory
    locking. It is possible to have an orphaned lock or a ghosted lock.

    For simple scenarios such as avoiding long-running cron jobs from
    trampling over one another, it's probably sufficient.

    See also :func:`netsa.tools.service.check_pidfile`.
    """

    def __init__(self, name, dir=None, seize=False, debug=False):
        if dir is None:
            if path.isdir(DEFAULT_LOCK_DIR):
                dir = DEFAULT_LOCK_DIR
            else:
                dir = gettempdir()
        self.name     = name
        self.dir      = path.join(dir, name)
        self.pidfile  = path.join(dir, '%s.pid' % name)
        self.debug    = debug
        blocked = True
        for x in (xrange(LOCK_ATTEMPTS)):
            try:
                self._lock_dir()
                blocked = False
                break
            except DirLockBlock:
                if not path.exists(self.pidfile):
                    time.sleep(LOCK_WAIT_TIME)
        try:
            if self.debug:
                print >>sys.stderr, "inspecting %s" % self.pidfile
            fh = open(self.pidfile, 'r')
            opid = fh.read().strip()
            if self.debug:
                print >>sys.stderr, "inspect results %s" % opid
        except IOError:
            if self.debug:
                print >>sys.stderr, "inspect fail %s" % self.pidfile
            opid = None
        if opid is not None:
            opid = int(opid)
        is_running = True
        if opid is None:
            blocked = is_running = False
        else:
            if self.debug:
                print >>sys.stderr, "potential block, pid: (%s)" % opid
            try:
                os.kill(opid, 0)
            except OSError, e:
                if e.errno == errno.ESRCH:
                    is_running = False
        if is_running:
            blocked = True
        if blocked:
            if not is_running and seize:
                if self.debug:
                    print >>sys.stderr, \
                        "seizing presumed orphan lock pid: (%s)" % opid
            else:
                remove_lockdir(self.dir)
                if is_running:
                    msg = "process blocked by pid: (%s) %s" % (opid, self.dir)
                else:
                    msg = "process blocked by orphan pid: (%s) %s" \
                        % (opid, self.dir)
                raise DirLockBlock, msg
        if self.debug:
            print >>sys.stderr, "create pid file: %s" % self.pidfile
        fh = open(self.pidfile, 'w')
        atexit.register(remove_pidfile, self.pidfile)
        print >>fh, "%s" % os.getpid()
        fh.close()
        if self.debug:
            print >>sys.stderr, "removing lock dir: %s" % self.dir
        remove_lockdir(self.dir)
    
    def _lock_dir(self):
        try:
            if self.debug:
                print >>sys.stderr, "attempt lock: %s" % self.dir
            # mkdir is atomic for POSIX compliant OS's and NFS
            # (what about AFS? -- investigate)
            os.mkdir(self.dir)
            if self.debug:
                print >>sys.stderr, "success lock: %s" % self.dir
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise e
            else:
                raise DirLockBlock, "already exists: %s" % self.dir
            
    def __str__(self):
        return "<lock pidfile (%s) %s>" % (self.pidfile, os.getpid())

__all__ = """

    relpath
    is_relpath

    LocalTmpDirError
    LocalTmpDir

    DirLockBlock
    DirLocker

""".split()
