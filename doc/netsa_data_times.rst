:mod:`netsa.data.times` --- Time and Date Manipulation
======================================================

.. automodule:: netsa.data.times

    .. autofunction:: make_datetime(v : num or str or datetime or mxDateTime, [utc_only=True]) -> datetime
    
    .. autofunction:: bin_datetime(dt : timedelta, t : datetime, [z=UNIX_EPOCH : datetime]) -> datetime

    .. autofunction:: make_timedelta(v : timedelta or str) -> timedelta

    .. autofunction:: divmod_timedelta(n : timedelta, d : timedelta) -> int, timedelta

    Date Snappers
    -------------

    .. autoclass:: DateSnapper(size : timedelta, [epoch=UNIX_EPOCH : datetime])

        .. automethod:: date_aligned(date) -> bool

        .. automethod:: date_bin(date) -> datetime

        .. automethod:: date_bin_end(date) -> datetime

        .. automethod:: date_binner(dates : date seq) -> seq

        .. automethod:: date_clumper(date_ranges : seq) -> datetime seq

        .. automethod:: date_sequencer(date_list : date seq) -> seq

        .. automethod:: next_date_bin(date) -> datetime

        .. automethod:: prior_date_bin(date) -> datetime

        .. automethod:: today_bin() -> datetime

    .. autofunction:: dow_day_snapper(size : int, [dow=0]) -> DateSnapper
