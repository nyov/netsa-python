:mod:`netsa.files` --- File and Path Manipulation
=================================================

.. automodule:: netsa.files

    The routines in :mod:`netsa.files` are intended to help with
    manipulation of files in the filesystem as well as pathnames.

    Paths
    -----

    .. autofunction:: relpath(p : str, base : str) -> str

    .. autofunction:: is_relpath(p : str, base : str) -> bool


    Directory-based Locking
    -----------------------

    .. autoexception:: DirLockBlock(message)

    .. autoclass:: DirLocker(name : str, [dir : str, seize=False, debug=False])
        :members:

    Garbage Collected Temporary Directories
    ---------------------------------------

    .. autoexception:: LocalTmpDirError(message)

    .. autoclass:: LocalTmpDir([dir : str, prefix='tmp', create=True, verbose=False, autodelete=True])

        .. automethod:: assert_dir()

        .. automethod:: prefix()

        .. automethod:: tmp_file() -> NamedTemporaryFile

        .. automethod:: tmp_filename() -> str

        .. automethod:: tmp_pipe() -> str
