Deprecated Features
===================

Deprecated functions from :mod:`netsa.files`
********************************************

.. currentmodule:: netsa.files

.. autoexception:: DirLockBlock(message)

.. autoclass:: DirLocker(name : str, [dir : str, seize=False, debug=False])
    :members:

.. autoexception:: LocalTmpDirError(message)

.. autoclass:: LocalTmpDir([dir : str, prefix='tmp', create=True, verbose=False, autodelete=True])

    .. automethod:: assert_dir()

    .. automethod:: prefix()

    .. automethod:: tmp_file() -> NamedTemporaryFile

    .. automethod:: tmp_filename() -> str

    .. automethod:: tmp_pipe() -> str

Deprecated module :mod:`netsa.files.datefiles`
**********************************************

.. automodule:: netsa.files.datefiles

    *Deprecated* as of netsa-python v1.4.  No general replacement is
    yet available.

    .. autoexception:: DateFileParseError(message : str)

    .. autofunction:: date_from_file(file : str) -> datetime

    .. autofunction:: split_on_date(file : str)

    .. autofunction:: date_file_template(file : str, [wildcard='x']) -> str

    .. autofunction:: sibling_date_file(file : str, date : datetime) -> str

    .. autofunction:: datefile_walker(dir : str, [suffix : str, silent=False, snapper : DateSnapper, descend=True, reverse=False]) -> iter

    .. autofunction:: latest_datefile(dir : str, [suffix : str, silent=False, snapper : DateSnapper, descend=True]) -> tuple or None

    .. autofunction:: date_snap_walker(dir : str, snapper : DateSnapper, [suffix : str, sparse=True]) -> iter

    .. autofunction:: tandem_datefile_walker(sources : str seq, [suffix : str, silent=True, snapper : DateSnapper, reverse=False]) -> iter

Deprecated functions from :mod:`netsa.script`
*********************************************

.. currentmodule:: netsa.script

.. autofunction:: get_temp_dir_file_name([file_name : str]) -> str

.. autofunction:: get_temp_dir_file([file_name : str, append=False]) -> file

.. autofunction:: get_temp_dir_pipe_name([pipe_name : str]) -> str

Deprecated module :mod:`netsa.tools.service`
********************************************

.. automodule:: netsa.tools.service

    .. autofunction:: check_pidfile(path : str, [unlink=True]) -> bool

