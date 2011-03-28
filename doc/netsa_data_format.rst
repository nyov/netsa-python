:mod:`netsa.data.format` --- Formatting Data for Output
=======================================================

.. automodule:: netsa.data.format

    Numbers
    -------

    .. autofunction:: num_fixed(value : num, [units : str, dec_fig=2, thousands_sep : str]) -> str

    .. autofunction:: num_exponent(value : num, [units : str, sig_fig=3]) -> str

    .. autofunction:: num_prefix(value : num, [units : str, sig_fig=3, use_binary=False, thousands_sep : str]) -> str

    Dates and Times
    ---------------

    Dates and times may be formatted to a variety of precisions.  The
    formatting functions support the following precisions, except
    where otherwise noted: :const:`DATETIME_YEAR`,
    :const:`DATETIME_MONTH`, :const:`DATETIME_DAY`,
    :const:`DATETIME_HOUR`, :const:`DATETIME_MINUTE`,
    :const:`DATETIME_SECOND`, :const:`DATETIME_MSEC`, and
    :const:`DATETIME_USEC`.

    .. autofunction:: datetime_silk(value : datetime, [precision=DATETIME_SECOND]) -> str

    .. autofunction:: datetime_silk_hour(value : datetime) -> str

    .. autofunction:: datetime_silk_day(v : datetime) -> str

    .. autofunction:: datetime_iso(value : datetime, [precision=DATETIME_SECOND]) -> str

    .. autofunction:: datetime_iso_day(value : datetime) -> str

    .. autofunction:: datetime_iso_basic(value : datetime, [precision=DATETIME_SECOND]) -> str

    .. autofunction:: timedelta_iso(value : timedelta) -> str
