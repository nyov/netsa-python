# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

from __future__ import division

import atexit
import errno
import math
import os
import os.path
import re
import shutil
import sys
import threading
import tempfile
import time

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
    p_parts = p.split('/')
    b_parts = base.split('/')
    if p_parts[-1] == '': p_parts.pop()
    if b_parts[-1] == '': b_parts.pop()
    if p_parts == b_parts:
        return "."
    if len(p_parts) < 1 or len(b_parts) < 1 or p_parts[0] != b_parts[0]:
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
    if base is None:
        return True
    p_parts = p.split('/')
    b_parts = base.split('/')
    if p_parts[-1] == '': p_parts.pop()
    if b_parts[-1] == '': b_parts.pop()
    if p_parts == b_parts:
        return True
    if len(p_parts) < 1:
        if len(b_parts) < 1:
            return True
        else:
            return False
    else:
        if len(b_parts) < 1:
            return True
    while p_parts and b_parts and p_parts[0] == b_parts[0]:
        p_parts.pop(0)
        b_parts.pop(0)
    if b_parts:
        return False
    return True

########################################################################

import atexit
import errno
import time
import os
import warnings

_pidfile_atexit_registered = False
_locked_pidfiles = set()

def _remove_pidfile_locks():
    for path in list(_locked_pidfiles):
        release_pidfile_lock(path)

def _add_pidfile_lock(path):
    global _pidfile_atexit_registered
    if not _pidfile_atexit_registered:
        _pidfile_atexit_registered = True
        atexit.register(_remove_pidfile_locks)
    _locked_pidfiles.add(path)

def _remove_pidfile_lock(path):
    _locked_pidfiles.discard(path)

def acquire_pidfile_lock(path):
    """
    Attempts to acquire a locking PID file at the requested pathname
    *path*.  If the file does not exist, creates it with the current
    process ID.  If the file does exist but refers to a
    no-longer-existing process, attempts to replace it.  If the file
    does exist and refers to a running process, does nothing.

    Registers the lock to be released (as with
    :func:`release_pidfile_lock`) when the currently running process
    exits, if it has not already been released.

    Returns ``True`` if this process holds the lock, or ``False`` if
    another running process holds the lock.
    """
    lock_stolen = False
    while True:
        status = examine_pidfile_lock(path)
        if status is None:
            # No file exists
            # Create new lock file
            fd = None
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                os.write(fd, str(os.getpid()))
                os.close(fd)
                # There's a race condition if two processes try to
                # steal the lock at the same time.  To ensure that the
                # winner of the race is known, sleep for one second,
                # but only if the lock has been stolen.
                if lock_stolen:
                    time.sleep(1)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
        else:
            # File exists
            (existing_pid, is_running) = status
            if is_running:
                # Some process holds the lock
                if existing_pid == os.getpid():
                    # This process holds the lock
                    result = True
                    break
                else:
                    # Another process holds the lock
                    result = False
                    break
            else:
                # A non-running process holds the lock
                os.unlink(path)
                lock_stolen = True
    if result is True:
        _add_pidfile_lock(path)
    return result

def examine_pidfile_lock(path):
    """
    Examines the state of a locking PID file at *path* and returns it.
    If the file does not exist or is not in the proper format, returns
    ``None``.  If the file does exist and contains a PID, returns
    :samp:`({pid}, {state})` where *pid* is the process ID holding the
    lock, and *state* is ``True`` if a running process has that
    process ID, or ``False`` otherwise.
    """
    try:
        # Read the current PID from the file.
        f = open(path, 'r')
        pid = int(f.read())
        f.close()
    except (IOError, ValueError, TypeError):
        # File does not exist, or is not readable
        return None
    # Check if the process is running.
    try:
        os.kill(pid, 0)
        return (pid, True)
    except OSError:
        return (pid, False)

def release_pidfile_lock(path):
    """
    Attempts to release a locking PID file at the requested pathname
    *path*.  If the file does not exist or contains a lock for a
    different PID, does nothing.  Otherwise, unlinks the file.
    """
    try:
        status = examine_pidfile_lock(path)
        if status is not None:
            (existing_pid, is_running) = status
            if existing_pid == os.getpid():
                os.unlink(path)
        _locked_pidfiles.remove(path)
    except:
        pass

########################################################################

_temp_dir = None

_temp_lock = threading.RLock()
_temp_filenames = set()
_temp_filename_counter = 0

def get_temp_dir_base():
    """
    Internal function, called to initialize the temp dir, and set up
    automatic cleanup.  Called by functions in this module and by
    netsa.script.execute.
    """
    global _temp_dir
    if _temp_dir is None:
        _temp_lock.acquire()
        try:
            if _temp_dir is None:
                _temp_dir = tempfile.mkdtemp()
                def _temp_cleanup():
                    shutil.rmtree(_temp_dir, True)
                    pass
                atexit.register(_temp_cleanup)
        finally:
            _temp_lock.release()
    return _temp_dir

def get_temp_file_name(file_name=None):
    """
    Return the path to a file named *file_name* in a temporary
    directory that will be cleaned up when the process exits.  If
    *file_name* is ``None`` then a new file name is created that has
    not been used before.

    A temporary file at the named location will be cleaned up as long
    as the Python interpreter exits normally.
    """
    global _temp_filename_counter
    _temp_lock.acquire()
    try:
        if file_name == None:
            # If the filename wasn't provided by the user
            while file_name == None or file_name in _temp_filenames:
                # Allocate new filenames until one not in the list of used
                # filenames is found.
                _temp_filename_counter += 1
                file_name = "tmp%d.tmp" % _temp_filename_counter
        # Remember the filename used.
        _temp_filenames.add(file_name)
        return os.path.join(get_temp_dir_base(), file_name)
    finally:
        _temp_lock.release()

def get_temp_file(file_name=None, mode='r'):
    """
    Returns an open :class:`file` object for the file named
    *file_name* in the temporary working directory, with the given
    *mode* (as described in :func:`open`.  If *file_name* is ``None``
    then a new file name is used that has not been used before.

    The resulting temporary file will be cleaned up as long as the
    Python interpreter exits normally.
    """
    _temp_lock.acquire()
    try:
        fn = get_temp_file_name(file_name)
        out_file = open(fn, mode)
        return out_file
    finally:
        _temp_lock.release()

def get_temp_pipe_name(file_name=None):
    """
    Returns the path to a named pipe *file_name* that has been created
    in a temporary directory that will be cleaned up when the process
    exits. If *file_name* is ``None`` then a new file name is created
    that has not been used before.
    """
    _temp_lock.acquire()
    try:
        pn = get_temp_file_name(file_name)
        os.mkfifo(pn)
        return pn
    finally:
        _temp_lock.release()

__all__ = """

    relpath
    is_relpath

    acquire_pidfile_lock
    examine_pidfile_lock
    release_pidfile_lock

    get_temp_file_name
    get_temp_file
    get_temp_pipe_name

""".split()
