# Copyright 2008-2011 by Carnegie Mellon University

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

from datetime import date, datetime, timedelta, tzinfo
from calendar import timegm
import re

mxDateTime_support = False
# Attempt to load mx datetime support
try:
    from mx.DateTime import DateTimeType as mxDateTimeType
    mxDateTime_support = True
except:
    pass

import netsa.data.format

# Note: When we format dates in ISO format, we do not include the Z or
# +00:00 to designate that it's UTC.  We assume that any date without
# an explicit timezone is UTC.  Internally, we work with datetime
# objects that include the UTC timezone field to be sure that they are
# correctly handled by other things.

TD_ZERO = timedelta(0)

class tzinfo_UTC(tzinfo):
    def utcoffset(self, dt):
        return TD_ZERO
    def tzname(self, dt):
        return "Z"
    def dst(self, dt):
        return TD_ZERO
    def __repr__(self):
        return "tzinfo_UTC()"

class tzinfo_fixed(tzinfo):
    def __init__(self, offset):
        self.__minutes = offset
        self.__offset = timedelta(minutes=offset)
        self.__name = "%+03d:%02d" % (offset // 60, offset % 60)
    def utcoffset(self, dt):
        return self.__offset
    def tzname(self, dt):
        return self.__name
    def dst(self, dt):
        return TD_ZERO
    def __repr__(self):
        return "tzinfo_fixed(%d)" % self.__minutes

utc = tzinfo_UTC()

DT_EPOCH = datetime.utcfromtimestamp(0).replace(tzinfo=utc)

re_iso_datetime = re.compile(r"""
       ^ (?P<year>\d\d\d\d)
       - (?P<mon>\d\d)
       - (?P<day>\d\d)
(?: [ T] (?P<hour>\d\d)
(?:    : (?P<min>\d\d)
(?:    : (?P<sec>\d\d)
(?:   \. (?P<fsec>\d+) )? )? )? )?
(?:      (?P<tz> Z | [+-] \d\d (?: : \d\d )? ) )? $
""", re.VERBOSE)

re_silk_datetime = re.compile(r"""
        ^ (?P<year>\d\d?\d?\d?)
        / (?P<mon>\d\d?)
        / (?P<day>\d\d?)
(?: [ :T] (?P<hour>\d\d?)
(?:     : (?P<min>\d\d?)
(?:     : (?P<sec>\d\d?)
(?:    \. (?P<fsec>\d+) )? )? )? )? $
""", re.VERBOSE)

re_old_silk_datetime = re.compile(r"""
        ^ (?P<mon>\d\d)
        / (?P<day>\d\d)
        / (?P<year>\d\d\d\d)
(?: [ :T] (?P<hour>\d\d)
(?:     : (?P<min>\d\d)
(?:     : (?P<sec>\d\d)
(?:    \. (?P<fsec>\d+) )? )? )? )? $
""", re.VERBOSE)

def make_datetime(value, utc_only=True):
    """

    Produces a :class:`datetime.datetime` object from a number
    (seconds from UNIX epoch), a string (in ISO format, SiLK format,
    or old SiLK format), or a :class:`datetime.datetime` object.  If
    *utc_only* is ``True``, coerces the result to be in the UTC time
    zone.

    If the mxDateTime_ library is installed, this function also
    accepts :class:`mxDateTime` objects.

    .. _mxDateTime: http://www.egenix.com/products/python/mxBase/mxDateTime/
    """
    v = value
    if mxDateTime_support and isinstance(v, mxDateTimeType):
        v = str(v)
    if isinstance(v, (int, long, float)):
        # seconds from epoch: return datetime
        v = datetime.utcfromtimestamp(v)
        return v.replace(tzinfo=utc)
    if isinstance(v, basestring):
        # string representation: parse to datetime, then proceed
        vs = v.strip()
        m = (re_iso_datetime.match(vs) or
             re_silk_datetime.match(vs) or
             re_old_silk_datetime.match(vs))
        if not m:
            raise ValueError("Could not parse %s as a datetime" % repr(v))
        dt_year = int(m.group('year'))
        dt_mon = int(m.group('mon'))
        dt_day = int(m.group('day'))
        dt_hour = int(m.group('hour') or 0)
        dt_min = int(m.group('min') or 0)
        dt_sec = int(m.group('sec') or 0)
        dt_usec = int(((m.group('fsec') or '0') + '00000')[:6])
        try:
            dt_tz_str = m.group('tz')
        except:
            dt_tz_str = 'Z'
        if dt_tz_str == '' or dt_tz_str is None:
            dt_tz = None
        elif dt_tz_str == 'Z':
            dt_tz = utc
        else:
            if len(dt_tz_str) == 3:
                dt_tz_offset = int(dt_tz_str[1:3]) * 60
            else:
                dt_tz_offset = int(dt_tz_str[1:3]) * 60 + int(dt_tz_str[4:6])
            if dt_tz_str[0] == '-':
                dt_tz_offset = -dt_tz_offset
            dt_tz = tzinfo_fixed(dt_tz_offset)
        v = datetime(dt_year, dt_mon, dt_day, dt_hour, dt_min, dt_sec,
                     dt_usec, dt_tz)
    if isinstance(v, datetime):
        # datetime object
        if not utc_only:
            # allowing non-UTC times, so return it
            return v
        else:
            # normalize to UTC
            if v.tzinfo == None:
                # if it's a datetime with no timezone, assume UTC
                return v.replace(tzinfo=utc)
            else:
                # otherwise, convert it to UTC
                return v.astimezone(utc)
    value_error = ValueError("can't interpret %s as a datetime" % repr(value))
    raise value_error

def normalize_datetime(v):
    """
    Coerces a datetime object to UTC if it is not already.
    """
    if not isinstance(v, datetime):
        raise TypeError("time value must be instance of datetime.datetime")
    # v is a datetime, normalize it to UTC
    if v.tzinfo == utc:
        return v
    elif v.tzinfo == None:
        return v.replace(tzinfo=utc)
    else:
        return v.astimezone(utc)

def epoch_usec(dt):
    """
    Converts the given datetime into the number of microseconds
    since the epoch.
    """
    return timegm(dt.timetuple())*1000000 + dt.microsecond

def bin_datetime(dt, t, z=DT_EPOCH):
    """
    Returns a new :class:`datetime.datetime` object which is the floor
    of the :class:`datetime.datetime` *t* in a *dt*-sized bin.  For
    example::

        bin_datetime(timedelta(minutes=5), t)

    will return the beginning of a five-minute bin containing the time
    *t*.  If you have very specific requirements, you can replace the
    origin point for binning (*z*) with a time of your choice.  By
    default, the UNIX epoch is used, which is appropriate for most
    uses.
    """
    # handle a few "deltas" specially
    if isinstance(dt, basestring):
        if dt.strip().lower() in ('mon', 'month', 'months', 'monthly'):
            t = make_datetime(
                netsa.data.format.datetime_iso(
                    t, precision=netsa.data.format.DATETIME_MONTH) +
                "-01")
            return t
        elif dt.strip().lower() in ('year', 'years', 'yearly', 'annual'):
            t = make_datetime(
                netsa.data.format.datetime_iso(
                    t, precision=netsa.data.format.DATETIME_YEAR) +
                "-01-01")
            return t
        else:
            return ValueError("bin_datetime couldn't understand %s" % repr(dt))
    # normalize "just in case" for now
    t = normalize_datetime(t)
    # ignore microseconds
    tz = t - z
    tzs = tz.days * 86400 + tz.seconds
    dts = dt.days * 86400 + dt.seconds
    rs = (tzs // dts) * dts
    return z + timedelta(seconds=rs)

re_iso_duration = re.compile(r"""
    ^ (?P<sign>[+-])?
    P
    ((?P<years>[0-9]+)Y)?
    ((?P<months>[0-9]+)M)?
    ((?P<weeks>[0-9]+)W)?
    ((?P<days>[0-9]+)D)?
    (T
    ((?P<hours>[0-9]+)H)?
    ((?P<minutes>[0-9]+)M)?
    ((?P<seconds>[0-9]+(\.[0-9]+)?)S)?
    )?$
""", re.VERBOSE)

def make_timedelta(value):
    """
    Produces a :class:`datetime.timedelta` object from a string (in
    ISO 8601 duration format) or a :class:`datetime.timedelta`
    object.

    Since :class:`datetime.timedelta` objects do not internally support
    units larger than 'days', ISO 8601 strings containing month or year
    designations are discouraged. If these units are encountered in the
    string, however, they converted to days using a precise formula.
    This is an exact conversion that does not take into account any
    calendrical context. If you apply the result to a datetime, and the
    interval happens to include leapseconds, or if you expect to land on
    the same day of the month while adding 'months' or 'years', adjust
    your expectations accordingly.

    Example of ISO 8601: 'P1DT1H1M1S'

    This translates as a period of '1 day' with time offset of '1 hour,
    1 minute, and 1 second'. Fields are optional, the 'P' is required,
    as is the 'T' if using any units smaller than a day. A zero-valued
    timedelta can be represented as 'P0D'.

    .. ISO 8601: http://www.w3.org/TR/xmlschema-2/#duration
    """
    if isinstance(value, timedelta):
        return value
    match = re_iso_duration.match(value)
    if not match:
        error = ValueError("unable to parse %s as duration" % repr(value))
        raise error
    negative = False
    years = months = 0
    kwargs = {}
    for k, v in match.groupdict().iteritems():
        if v is None:
            continue
        if k == 'years':
            years = int(v)
            continue
        elif k == 'months':
            months = int(v)
            continue
        elif k == 'sign' and v == '-':
            negative = True
            continue
        try:
            kwargs[k] = int(v)
        except ValueError:
            kwargs[k] = float(v)
    if months or years:
        kwargs.setdefault('days', 0)
        kwargs['days'] += int((years + (months / 12.0)) * 365.2425)
    d = timedelta(**kwargs)
    if negative:
        d = -d
    return d

def divmod_timedelta(n, d):
    """
    Given two :class:`datetime.timedelta` objects, return the
    number of times the second one (denominator) fits into the
    first one (numerator), along with any remainder expressed
    as another timedelta.
    """
    nus = (n.days*24*3600 + n.seconds)*1000000 + n.microseconds
    dus = (d.days*24*3600 + d.seconds)*1000000 + d.microseconds
    q, r = divmod(nus, dus)
    return q, timedelta(microseconds=r)

### timebin additions

def dow_epoch(dow=0, skew=None, z=DT_EPOCH):
    """
    Given an integer day-of-the-week, return a datetime representing the
    first occurrence of that day after the optional epoch, suitable for
    anchoring date bins as provided by bin_datetime(). Monday is the 0th
    DOW. DOW values are modulo 7, so the 7th DOW also represents Monday.
    Sunday is the 6th DOW. The optional epoch parameter *z* defaults to
    the UNIX epoch. An optional timedelta *skew* can be provided in
    order to shift the epoch from midnight.
    """
    offset = (dow + (7 - (DT_EPOCH.weekday()))) % 7
    epoch  = DT_EPOCH + timedelta(days=offset)
    if skew:
        epoch += skew
    return epoch

def dow_day_snapper(size, dow=0, z=DT_EPOCH):
    """
    Given an integer size in days and an integer day-of-the-week,
    returns a :class:``DateSnapper`` object anchored on the first
    occurring instance of that DOW after the given epoch, which defaults
    to the UNIX epoch. Monday is the 0th DOW. DOW values are modulo 7,
    so the 7th DOW would also represent Monday.
    """
    return DateSnapper(timedelta(days=size), epoch=dow_epoch(dow))

class DateSnapper(object):
    """
    Class for date bin manipulations
    """
    def __init__(self, size, epoch=DT_EPOCH):
        """
        Returns a :class:`DateSnapper` object that bins dates in bins
        of the given size, specified as a :class:`datetime.timedelta`
        object.  An optional *epoch* can be provided as an absolute
        anchor for subsequent bins.
        """
        self.size  = abs(size)
        self.epoch = epoch
    
    def date_bin(self, date):
        """
        Returns a :class:`datetime.datetime` object representing the
        beginning of the date bin containing the provided date
        ('snapping' the date into place)

        See :func:`make_datetime` for more detail on acceptable
        formats for date descriptors.
        """
        return bin_datetime(self.size, make_datetime(date), z=self.epoch)

    def date_aligned(self, date):
        """
        Tests whether or not the provided date is the beginning
        :class:`datetime.datetime` for the containing time bin.
        
        See :func:`make_datetime` for more detail on acceptable
        formats for date descriptors.
        """
        return self.date_bin(date) == make_datetime(date)

    def next_date_bin(self, date):
        """
        Returns a :class:`datetime.datetime` object representing the
        beginning of the date bin following the date bin in which the
        given date resides.

        See :func:`make_datetime` for more detail on acceptable
        formats for date descriptors.
        """
        return self.date_bin(date) + self.size

    def prior_date_bin(self, date):
        """
        Returns a :class:`datetime.datetime` object representing the
        beginning of the date bin prior to the date bin in which the
        given date resides.

        See :func:`make_datetime` for more detail on acceptable
        formats for date descriptors.
        """
        return self.date_bin(date) - self.size

    def today_bin(self):
        """
        Returns a :class:`datetime.datetime` object representing the
        beginning of the date bin containing the current date.
        """
        return self.date_bin(datetime.today())

    def date_bin_end(self, date):
        """
        Returns a :class:`datetime.datetime` object representing the
        last date of the date bin which contains the provided date.

        See :func:`make_datetime` for more detail on acceptable
        formats for date descriptors.
        """
        return self.next_date_bin(date) - timedelta(seconds=1)

    def date_clumper(self, date_ranges):
        """
        Given a list of date ranges, return a list of date bins that
        intersect the union of the given date ranges. Each date range in
        the provided list can be a single datetime descriptor or a tuple
        representing a beginning and end datetime for the range.

        See :func:`make_datetime` for more detail on acceptable
        formats for date descriptors.
        """
        overlay = {}
        for drange in date_ranges:
            if isinstance(drange, basestring):
                drange = make_datetime(drange)
                begin  = self.date_bin(drange)
                end    = self.next_date_bin(begin)
            elif isinstance(drange, datetime):
                begin = self.date_bin(drange)
                end   = begin
            else:
                (begin, end) = sorted([self.date_bin(x) for x in drange])
            sib = None
            try:
                overlay[begin] += 1
                if overlay[begin] == 0:
                    del overlay[begin]
            except KeyError:
                overlay[begin] = 1
            end_plus = self.next_date_bin(end)
            try:
                overlay[end_plus] -= 1
                if overlay[end_plus] == 0:
                    del overlay[end_plus]
            except KeyError:
                overlay[end_plus] = -1
        begin = None
        in_range = 0
        for date in sorted(overlay):
            count = overlay[date]
            if begin == None:
                begin = date
            in_range += count
            if not in_range:
                yield (begin, self.prior_date_bin(date))
                begin = None

    def date_binner(self, dates):
        """
        Given a list of datetimes, returns an iterator which produces
        tuples containing two datetime objects for each provided
        datetime. The first value of the tuple is the beginning of the
        date bin containing the datetime in question and the second
        value is the original datetime.

        See :func:`make_datetime` for more detail on acceptable
        formats for datetime descriptors.
        """
        for date in dates:
            yield(self.date_bin(date), date)

    def date_sequencer(self, date_list):
        """
        Given a list of datetimes, returns an iterator which produces
        tuples containing two datetime objects. The first value of the
        tuple is the begining of the date bin and the second value is
        the original datetime. Both bins and datetimes will be
        repeated where necessary to fill in gaps not present in the
        original list of datetimes.

        If, for example, the span between each successive datetime in
        the provided list is smaller than the defined bin size, the same
        bin will be returned for each datetime residing in that bin. (An
        example of this would be a bin size of 7 days and a list of
        daily dates -- the same bin would be returned for each week of
        dates within that bin).

        If, on the other hand, the span between successive datetimes in
        the provided list is larger than the defined bin size, each
        provided date will be repeatly returned with each bin that
        exists between the provided datetimes. (An example of this would
        be a bin size of 7 days and a list of monthly dates -- each
        monthly date would be succesively returned with the 4 (or so)
        bins touched by that month)

        See :func:`make_datetime` for more detail on acceptable
        formats for date descriptors.
        """
        datebins = self.date_binner(sorted(date_list))
        prior_bin = prior_date = None
        for (bin, date) in datebins:
            if (prior_date):
                fill_bin = self.next_date_bin(prior_date)
                while fill_bin < bin:
                    yield(fill_bin, prior_date)
                    fill_bin = self.next_date_bin(fill_bin)
            prior_date = date
            yield(bin, date)

###
    
__all__ = """

    make_datetime
    bin_datetime

    make_timedelta
    divmod_timedelta

    DateSnapper
    dow_day_snapper
    dow_epoch

""".split()
