# Copyright 2008-2011 by Carnegie Mellon University

# @OPENSOURCE_HEADER_START@
# Use of the Network Situational Awareness Python support library and
# related source code is subject to the terms of the following licenses:
# 
# GNU Public License (GPL) Rights pursuant to Version 2, June 1991
# Government Purpose License Rights (GPLR) pursuant to DFARS 252.227.7013
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

"""
A set of functions to produce ranges of aesthetically-pleasing numbers
that have the specified length and include the specified range.
Functions are provided for producing nice numeric and time-based
ranges.
"""

from __future__ import division
from datetime import date, datetime, timedelta
import calendar
import copy
import math
import times

from netsa.data.times import make_datetime, bin_datetime

#
# Regular number stuff (code mutated from original work by John
# Prevost)
#



nice_intervals = [1.0, 2.0, 2.5, 3.0, 5.0, 10.0]
int_intervals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
int_12_intervals = [1.0, 2.0, 3.0, 4.0, 6.0, 12.0]
int_60_intervals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 10.0,
                    12.0, 15.0, 20.0, 30.0]

def nice_ceil(x, intervals=nice_intervals, base=10.0):
    if x == 0:
        return 0
    if x < 0:
        return nice_floor(x * -1, intervals, base) * -1
    z = base ** math.floor(math.log(x, base))
    for i in xrange(len(intervals) - 1):
        result = intervals[i] * z
        if x <= result: return result
    return intervals[-1] * z

def nice_floor(x, intervals=nice_intervals, base=10.0):
    if x == 0:
        return 0
    if x < 0:
        return nice_ceil(x * -1, intervals, base) * -1
    z = base ** (math.ceil(math.log(x, base)) - 1.0)
    r = x / z
    for i in xrange(len(intervals)-1, 1, -1):
        result = intervals[i] * z
        if x >= result: return result
    return intervals[0] * z
    
def nice_round(x, intervals=nice_intervals, base=10.0):
    if x == 0:
        return 0
    z = base ** (math.ceil(math.log(x, base)) - 1.0)
    r = x / z
    for i in xrange(len(intervals) - 1):
        result = intervals[i] * z
        cutoff = (result + intervals[i+1] * z) / 2.0
        if x <= cutoff: return result
    return intervals[-1] * z

def nice_ticks(lo, hi, ticks=5, inside=False,
               intervals=nice_intervals, base=10.0):
    """
    Find 'nice' places to put *ticks* tick marks for numeric data
    spanning from *lo* to *hi*.  If *inside* is ``True``, then the
    nice range will be contained within the input range.  If *inside*
    is ``False``, then the nice range will contain the input range.
    To find nice numbers for time data, use :func:`nice_time_ticks`.

    The result is a tuple containing the minimum value of the nice
    range, the maximum value of the nice range, and an iterator over
    the tick marks.

    See also :func:`nice_ticks_seq`.
    """

    if lo > hi:
        value_error = ValueError(
            "Low value greater than high value: %r, %r" % (lo, hi))
        raise value_error

    delta_x = hi - lo
    if delta_x == 0:
        lo = nice_floor(lo, intervals, base)
        hi = nice_ceil(hi, intervals, base)
        delta_x = hi - lo
        if delta_x == 0:
            lo = lo - 0.5
            hi = hi + 0.5
            delta_x = hi - lo

    nice_delta_x = nice_ceil(delta_x, intervals, base)
    delta_t = nice_round(delta_x / (ticks - 1), intervals, base)
    if inside:
        lo_t = math.ceil(lo / delta_t) * delta_t
        hi_t = math.floor(hi / delta_t) * delta_t
    else:
        lo_t = math.floor(lo / delta_t) * delta_t
        hi_t = math.ceil(hi / delta_t) * delta_t

    def t_iter():
        t = lo_t
        while t <= hi_t:
            yield t
            t = t + delta_t
    return (lo_t, hi_t, t_iter())

def nice_ticks_seq(lo, hi, ticks=5, inside=False):
    """
    A convenience wrapper of :func:`nice_ticks` to return the nice
    range as a sequence.
    """
    return tuple(nice_ticks(lo, hi, ticks, inside)[2])

def nice_year_ticks(lo, hi, ticks=5, inside=False):
    lo_year = lo.year
    hi_year = hi.year
    if hi - make_datetime(datetime(hi_year, 1, 1)):
        hi_year += 1
    if hi_year - lo_year < (ticks - 1):
        raise ValueError()
    t_min, t_max, t_iter = nice_ticks(lo_year, hi_year, ticks, inside,
                                      intervals=int_intervals)
    year_min = make_datetime(datetime(int(t_min), 1, 1))
    year_max = make_datetime(datetime(int(t_max), 1, 1))
    def y_iter():
        for t in t_iter:
            yield make_datetime(datetime(int(t), 1, 1))
    return (year_min, year_max, y_iter())

def nice_month_ticks(lo, hi, ticks=5, inside=False):
    lo_year = lo.year
    lo_month = lo.month - 1
    hi_year = hi.year
    hi_month = hi.month - 1
    if hi - make_datetime(datetime(hi_year, hi.month, 1)):
        if hi_month == 11:
            hi_month = 0
            hi_year += 1
        else:
            hi_month += 1
    delta_year = hi_year - lo_year
    if delta_year * 12 + hi_month - lo_month < (ticks - 1):
        raise ValueError()
    t_min, t_max, t_iter = nice_ticks(lo_month, delta_year * 12 + hi_month,
                                      ticks, inside,
                                      intervals=int_12_intervals, base=12.0)
    t_min_year = int(lo_year + t_min / 12)
    t_min_month = int(t_min % 12) + 1
    t_max_year = int(lo_year + t_max / 12)
    t_max_month = int(t_max % 12) + 1
    month_min = make_datetime(datetime(t_min_year, t_min_month, 1))
    month_max = make_datetime(datetime(t_max_year, t_max_month, 1))
    def m_iter():
        for t in t_iter:
            year = int(lo_year + t / 12)
            month = int(t % 12) + 1
            yield make_datetime(datetime(year, month, 1))
    return (month_min, month_max, m_iter())

WEEK_EPOCH = make_datetime('1970-01-04')

def nice_week_ticks(lo, hi, ticks=5, inside=False):
    lo_week = bin_datetime(timedelta(days=7), lo, WEEK_EPOCH)
    hi_week = bin_datetime(timedelta(days=7), hi, WEEK_EPOCH)
    if hi - hi_week:
        hi_week += timedelta(days=7)
    delta_weeks = (hi_week - lo_week).days / 7
    if delta_weeks < (ticks - 1):
        raise ValueError()
    t_min, t_max, t_iter = nice_ticks(0, delta_weeks, ticks, inside,
                                      int_intervals)
    week_min = lo_week + timedelta(days=int(7*t_min))
    week_max = lo_week + timedelta(days=int(7*t_max))
    def w_iter():
        for t in t_iter:
            yield lo_week + timedelta(days=int(7*t))
    return (week_min, week_max, w_iter())

def nice_day_ticks(lo, hi, ticks=5, inside=False):
    lo_day = bin_datetime(timedelta(days=1), lo)
    hi_day = bin_datetime(timedelta(days=1), hi)
    if hi - hi_day:
        hi_day += timedelta(days=1)
    delta_days = (hi_day - lo_day).days
    if delta_days < (ticks - 1):
        raise ValueError()
    t_min, t_max, t_iter = nice_ticks(0, delta_days, ticks, inside,
                                      int_intervals)
    day_min = lo_day + timedelta(days=int(t_min))
    day_max = lo_day + timedelta(days=int(t_max))
    def d_iter():
        for t in t_iter:
            yield lo_day + timedelta(days=int(t))
    return (day_min, day_max, d_iter())

def nice_hour_ticks(lo, hi, ticks=5, inside=False):
    lo_hour = bin_datetime(timedelta(hours=1), lo)
    hi_hour = bin_datetime(timedelta(hours=1), hi)
    if hi - hi_hour:
        hi_hour += timedelta(hours=1)
    delta_hours = ((hi_hour - lo_hour).seconds / 3600 +
                   (hi_hour - lo_hour).days * 24)
    if delta_hours < (ticks - 1):
        raise ValueError()
    t_min, t_max, t_iter = nice_ticks(0, delta_hours, ticks, inside,
                                      intervals=int_12_intervals, base=24.0)
    hour_min = lo_hour + timedelta(hours=int(t_min))
    hour_max = lo_hour + timedelta(hours=int(t_max))
    def h_iter():
        for t in t_iter:
            yield lo_hour + timedelta(hours=int(t))
    return (hour_min, hour_max, h_iter())

def nice_minute_ticks(lo, hi, ticks=5, inside=False):
    lo_min = bin_datetime(timedelta(minutes=1), lo)
    hi_min = bin_datetime(timedelta(minutes=1), hi)
    if hi - hi_min:
        hi_min += timedelta(minutes=1)
    delta_mins = (hi_min - lo_min).seconds / 60 + (hi_min - lo_min).days * 1440
    if delta_mins < (ticks - 1):
        raise ValueError()
    t_min, t_max, t_iter = nice_ticks(0, delta_mins, ticks, inside,
                                      intervals=int_60_intervals, base=60.0)
    min_min = lo_min + timedelta(minutes=int(t_min))
    min_max = lo_min + timedelta(minutes=int(t_max))
    def m_iter():
        for t in t_iter:
            yield lo_min + timedelta(minutes=int(t))
    return (min_min, min_max, m_iter())

def nice_second_ticks(lo, hi, ticks=5, inside=False):
    lo_sec = bin_datetime(timedelta(seconds=1), lo)
    hi_sec = bin_datetime(timedelta(seconds=1), hi)
    if hi - hi_sec:
        hi_sec += timedelta(seconds=1)
    delta_secs = (hi_sec - lo_sec).seconds + (hi_sec - lo_sec).days * 86400
    if delta_secs < (ticks - 1):
        raise ValueError()
    t_min, t_max, t_iter = nice_ticks(0, delta_secs, ticks, inside,
                                      int_60_intervals, base=60.0)
    min_sec = lo_sec + timedelta(seconds=int(t_min))
    max_sec = lo_sec + timedelta(seconds=int(t_max))
    def s_iter():
        for t in t_iter:
            yield lo_sec + timedelta(seconds=int(t))
    return (min_sec, max_sec, s_iter())

def nice_arb_ticks(lo, hi, ticks=5, inside=False):
    base = bin_datetime(timedelta(minutes=1), lo)
    lo_sec = (lo - base).seconds + (lo - base).days * 86400
    hi_sec = (hi - base).seconds + (hi - base).days * 86400
    t_min, t_max, t_iter = nice_ticks(lo_sec, hi_sec, ticks, inside)
    min_sec = base + timedelta(seconds=t_min)
    max_sec = base + timedelta(seconds=t_max)
    def s_iter():
        for t in t_iter:
            yield base + timedelta(seconds=t)
    return (min_sec, max_sec, s_iter())

def nice_time_ticks(lo, hi, ticks=5, inside=False):
    """
    Find 'nice' places to put *ticks* tick marks for time data
    spanning from *lo* to *hi*.  If *inside* is ``True``, then the
    nice range will be contained within the input range.  If *inside*
    is ``False``, then the nice range will contain the input range.
    To find nice numbers for numerical data, use :func:`nice_ticks`.

    The result is a tuple containing the minimum value of the nice
    range, the maximum value of the nice range, and an iterator over
    the ticks marks.  If *as_datetime* is ``True``, the result values
    will be :class:`datetime.datetime` objects.  Otherwise, the result
    values will be numbers of seconds since UNIX epoch. Regardless,
    the return value is expressed in UTC.

    See also :func:`nice_time_ticks_seq`.
    """
    try:
        return nice_year_ticks(lo, hi, ticks, inside)
    except ValueError:
        pass
    try:
        return nice_month_ticks(lo, hi, ticks, inside)
    except ValueError:
        pass
    try:
        return nice_day_ticks(lo, hi, ticks, inside)
    except ValueError:
        pass
    try:
        return nice_hour_ticks(lo, hi, ticks, inside)
    except ValueError:
        pass
    try:
        return nice_minute_ticks(lo, hi, ticks, inside)
    except ValueError:
        pass
    try:
        return nice_second_ticks(lo, hi, ticks, inside)
    except ValueError:
        pass
    try:
        return nice_arb_ticks(lo, hi, ticks, inside)
    except ValueError:
        pass
    raise ValueError("Unable to compute nice time ticks")

def nice_time_ticks_seq(lo, hi, ticks=5, inside=False):
    """
    A convenience wrapper of :func:`nice_time_ticks` to return the
    nice range as a sequence.
    """
    (a, b, i) = nice_time_ticks(lo, hi, ticks, inside)
    return tuple(i)

__all__ = """
    nice_ticks
    nice_ticks_seq
    nice_time_ticks
    nice_time_ticks_seq
""".split()
