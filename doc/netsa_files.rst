:mod:`netsa.files` --- File and Path Manipulation
=================================================

.. automodule:: netsa.files

    The routines in :mod:`netsa.files` are intended to help with
    manipulation of files in the filesystem as well as pathnames.

    Paths
    -----

    .. autofunction:: relpath(p : str, base : str) -> str

    .. autofunction:: is_relpath(p : str, base : str) -> bool

    Process ID Locks
    ----------------

    This form of lock is generally used by services that wish to
    ensure that only one copy of the service is running at a time.

    .. autofunction:: acquire_pidfile_lock(path : str) -> bool

    .. autofunction:: examine_pidfile_lock(path : str) -> (int, bool) or None

    .. autofunction:: release_pidfile_lock(path : str)

    .. _netsa-files-tempfile-functions:

    Temporary Files
    ---------------

    .. autofunction:: get_temp_file_name([file_name : str]) -> str

    .. autofunction:: get_temp_file([file_name : str, mode='r']) -> file

    .. autofunction:: get_temp_pipe_name([pipe_name : str]) -> str

