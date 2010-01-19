:mod:`netsa.files.datefiles` --- Date-based filenames
=====================================================

.. automodule:: netsa.files.datefiles

    Exceptions
    ----------

    .. autoexception:: DateFileParseError(message : str)

    Filename Manipulation
    ---------------------

    .. autofunction:: date_from_file(file : str) -> datetime

    .. autofunction:: split_on_date(file : str)

    .. autofunction:: date_file_template(file : str, [wildcard='x']) -> str

    .. autofunction:: sibling_date_file(file : str, date : datetime) -> str

    Directory Walking
    -----------------

    .. autofunction:: datefile_walker(dir : str, [suffix : str, silent=False, snapper : DateSnapper, descend=True, reverse=False]) -> iter

    .. autofunction:: latest_datefile(dir : str, [suffix : str, silent=False, snapper : DateSnapper, descend=True]) -> tuple or None

    .. autofunction:: date_snap_walker(dir : str, snapper : DateSnapper, [suffix : str, sparse=True]) -> iter

    .. autofunction:: tandem_datefile_walker(sources : str seq, [suffix : str, silent=True, snapper : DateSnapper, reverse=False]) -> iter


