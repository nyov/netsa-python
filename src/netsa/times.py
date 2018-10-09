# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

"""
Backwards-compatibility binding for :mod:`netsa.data.times`.  New code
should be sure to use :mod:`netsa.data.times` directly instead.
"""

from netsa.data.times import (
    make_datetime, bin_datetime, DateSnapper, dow_day_snapper )

from netsa.data.format import datetime_silk as silk_datetime
from netsa.data.format import datetime_silk_hour as silk_hour
from netsa.data.format import datetime_silk_day as silk_day
from netsa.data.format import datetime_iso as iso_datetime
from netsa.data.format import datetime_iso_day as iso_date

__all__ = """

    make_datetime
    silk_datetime
    silk_hour
    silk_day
    iso_datetime
    iso_date
    bin_datetime

    DateSnapper
    dow_day_snapper

""".split()
