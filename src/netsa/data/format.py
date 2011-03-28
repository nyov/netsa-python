# Copyright 2008-2010 by Carnegie Mellon University

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

"""
The :mod:`netsa.data.format` module contains functions useful for
formatting data to be displayed in human-readable output.
"""

from __future__ import division

########################################################################

# Numeric formatting

import decimal
import math

_base_ctx = decimal.ExtendedContext.copy()
_base_ctx.prec = 20
_base_ctx.capitals = 0

def _make_rounding_context(sig_fig):
    ctx = _base_ctx.copy()
    ctx.prec = sig_fig
    return ctx

_rounding_contexts = [ _make_rounding_context(x) for x in xrange(10) ]

def _make_rounding_quantum(sig_fig):
    return _base_ctx.create_decimal("1." + "0" * sig_fig)

_rounding_quanta = [ _make_rounding_quantum(x) for x in xrange(10) ]

def _get_rounding_context(sig_fig):
    if 0 <= sig_fig < len(_rounding_contexts):
        return _rounding_contexts[sig_fig]
    else:
        return _make_rounding_context(sig_fig)

def _get_rounding_quantum(sig_fig):
    if 0 <= sig_fig < len(_rounding_quanta):
        return _rounding_quanta[sig_fig]
    else:
        return _make_rounding_quantum(sig_fig)

def _delimit_thousands(s, thousands_sep):
    if thousands_sep:
        i = 0
        while i < len(s) and s[i].isdigit():
            i += 1
        s = list(s)
        while i > 3:
            i -= 3
            s[i:0] = [thousands_sep]
        s = "".join(s)
    return s

_pzero = _base_ctx.create_decimal("+0")
_nzero = _base_ctx.create_decimal("-0")

def _dec_is_zero(n):
    return (n == _pzero) or (n == _nzero)

def num_fixed(value, units="", dec_fig=2, thousands_sep=""):
    """
    Format *value* using a fixed number of figures after the decimal
    point.  (e.g. "1234" is formatted as "1234.00") If *units* is
    provided, this unit of measurement is included in the output.
    *dec_fig* specifies the number of figures after the decimal point.

    If *thousands_sep* is given, it is used to separate each group of
    three digits to the left of the decimal point.

    Examples::

        >>> num_fixed(1234, 'm')
        '1234.00m'
        >>> num_fixed(1234, 'm', dec_fig=4)
        '1234.0000m'
        >>> num_fixed(1234.5678, 'm', dec_fig=0)
        '1235m'
        >>> num_fixed(123456789, dec_fig=3, thousands_sep=",")
        '123,456,789.000'
    """
    value = _base_ctx.create_decimal(str(value))
    value = value.quantize(_get_rounding_quantum(dec_fig))
    result = str(value) + units
    return _delimit_thousands(result, thousands_sep)

def _num_to_sci_string(value, sig_fig):
    (sign, digits, exp) = value.as_tuple()
    exp = len(digits) - 1 + exp
    digits = (list(digits) + [0] * sig_fig)[:sig_fig]
    if len(digits) == 0:
        digits = [0]
    if len(digits) > 1:
        digits[1:0] = '.'
    digits = ''.join(str(d) for d in digits)
    if sign:
        digits[0:0] = '-'
    return ("%se%+02d" % (digits, exp))

def num_exponent(value, units="", sig_fig=3):
    """
    Format *value* using exponential notation.  (i.e. "1234" becomes
    "1.23e+3" for three significant digits, or "1.234e+4" for four
    significant digits.)  If *units* is provided, this unit of
    measurement is included in the output.  *sig_fig* is the number of
    significant figures to display in the formatted result.

    Examples::

        >>> num_exponent(1234, 'm')
        '1.23e+3m'
        >>> num_exponent(1234, 'm', sig_fig=4)
        '1.234e+3m'
        >>> num_exponent(1234.5678, 'm', sig_fig=6)
        '1.23457e+3m'
        >>> num_exponent(123456789, sig_fig=2)
        '1.2e+8'
        >>> num_exponent(123456, sig_fig=6)
        '1.23456e+5'
    """
    ctx = _get_rounding_context(sig_fig)
    value = ctx.create_decimal(str(value))
    return _num_to_sci_string(value, sig_fig) + units

def num_prefix(value, units="", sig_fig=3, use_binary=False, thousands_sep=""):
    """
    Format *value* using SI prefix notation.  (e.g. 1k is 1000) If
    *units* is provided, this unit of measurement is included in the
    output.  *sig_fig* is the number of significant figures to display
    in the formatted result.

    If *use_binary* is ``True``, then SI binary prefixes are used
    (e.g. 1Ki is 1024).  Note that there are no binary prefixes for
    negative exponents, so standard prefixes are always used for such
    cases.

    For very large or very small values, exponential notation
    (e.g. "1e-30") is used.

    If *thousands_sep* is given, it is used to separate each group of
    three digits to the left of the decimal point.

    Examples::

        >>> num_prefix(1024, 'b')
        '1.02kb'
        >>> num_prefix(1024, 'b', use_binary=True)
        '1.00Kib'
        >>> num_prefix(12345, 'b', sig_fig=2)
        '12kb'
        >>> num_prefix(12345, 'b', sig_fig=7)
        '12345.00b'
        >>> num_prefix(12345678901234567890, 'b')
        '12.3Eb'
        >>> num_prefix(12345678901234567890, 'b', sig_fig=7)
        '12345.68Pb'
        >>> num_prefix(1234567890123456789012345, 's')
        '1.23e+24s'
        >>> num_prefix(0.001, 's')
        '1.00ms'
        >>> num_prefix(0.001, 's', use_binary=True)
        '1.00ms'
    """
    ctx = _get_rounding_context(sig_fig)
    quant = _get_rounding_quantum(sig_fig)
    value = _base_ctx.create_decimal(str(value))
    (sign, digits, exp) = value.as_tuple()
    if _dec_is_zero(value):
        result = "0" + units
    elif 0 <= value.adjusted() < sig_fig:
        value = value.quantize(quant)
        result = str(ctx.create_decimal(value)) + units
    elif use_binary and value.adjusted() >= 0:
        prefixes = ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei"]
        (exp, exp_value) = (0, value)
        while exp_value.adjusted()+1 > sig_fig:
            (exp, exp_value) = (exp + 1, exp_value / 1024)
        if exp >= len(prefixes):
            result = (_num_to_sci_string(ctx.create_decimal(value), sig_fig)
                      + units)
        else:
            exp_value = exp_value.quantize(quant)
            result = str(ctx.create_decimal(exp_value)) + prefixes[exp] + units
    elif value.adjusted() >= 0:
        prefixes = ["", "k", "M", "G", "T", "P", "E"]
        (exp, exp_value) = (0, value)
        while exp_value.adjusted()+1 > sig_fig:
            (exp, exp_value) = (exp + 1, exp_value / 1000)
        if exp >= len(prefixes):
            result = (_num_to_sci_string(ctx.create_decimal(value), sig_fig)
                      + units)
        else:
            exp_value = exp_value.quantize(quant)
            result = str(ctx.create_decimal(exp_value)) + prefixes[exp] + units
    else:
        prefixes = ["", "m", "u", "n", "p", "f", "a"]
        (exp, exp_value) = (0, value)
        while exp_value.adjusted() < 0:
            (exp, exp_value) = (exp + 1, exp_value * 1000)
        if exp >= len(prefixes):
            result = (_numto_sci_string(ctx.create_decimal(value), sig_fig)
                      + units)
        else:
            exp_value = exp_value.quantize(quant)
            result = str(ctx.create_decimal(exp_value)) + prefixes[exp] + units
    return _delimit_thousands(result, thousands_sep)

########################################################################

# Date and time formatting

import netsa.data.times

DATETIME_YEAR = 0
DATETIME_MONTH = 1
DATETIME_DAY = 2
DATETIME_HOUR = 3
DATETIME_MINUTE = 4
DATETIME_SECOND = 5
DATETIME_MSEC = 6
DATETIME_USEC = 7

def datetime_silk(value, precision=DATETIME_SECOND):
    """
    Format *value* as a SiLK format date and time
    (``YYYY/MM/DDTHH:MM:SS.SSS``).  Implicitly coerces the time into
    UTC.

    *precision* is the amount of precision that should be included in
    the output.

    For a more general way to round times, see
    :func:`netsa.data.times.bin_datetime`.  See also
    :func:`datetime_silk_hour` and :func:`datetime_silk_day` for the
    most common ways to format incomplete dates in SiLK format.

    Examples::

        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007")
        >>> datetime_silk(t)
        '2010/02/03T04:05:06'
        >>> datetime_silk(t, precision=DATETIME_YEAR)
        '2010'
        >>> datetime_silk(t, precision=DATETIME_MONTH)
        '2010/02'
        >>> datetime_silk(t, precision=DATETIME_DAY)
        '2010/02/03'
        >>> datetime_silk(t, precision=DATETIME_HOUR)
        '2010/02/03T04'
        >>> datetime_silk(t, precision=DATETIME_MINUTE)
        '2010/02/03T04:05'
        >>> datetime_silk(t, precision=DATETIME_SECOND)
        '2010/02/03T04:05:06'
        >>> datetime_silk(t, precision=DATETIME_MSEC)
        '2010/02/03T04:05:06.007'
        >>> datetime_silk(t, precision=DATETIME_USEC)
        '2010/02/03T04:05:06.007000'
    """
    v = netsa.data.times.normalize_datetime(value)
    if precision == DATETIME_SECOND:
        return ("%04d/%02d/%02dT%02d:%02d:%02d" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second))
    elif precision == DATETIME_MSEC:
        return ("%04d/%02d/%02dT%02d:%02d:%02d.%03d" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 v.microsecond // 1000))
    elif precision == DATETIME_HOUR:
        return ("%04d/%02d/%02dT%02d" % (v.year, v.month, v.day, v.hour))
    elif precision == DATETIME_DAY:
        return ("%04d/%02d/%02d" % (v.year, v.month, v.day))
    elif precision == DATETIME_MINUTE:
        return ("%04d/%02d/%02dT%02d:%02d" %
                (v.year, v.month, v.day, v.hour, v.minute))
    elif precision == DATETIME_MONTH:
        return ("%04d/%02d" % (v.year, v.month))
    elif precision == DATETIME_YEAR:
        return ("%04d" % (v.year))
    elif precision == DATETIME_USEC:
        return ("%04d/%02d/%02dT%02d:%02d:%02d.%03d000" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 v.microsecond // 1000))
    else:
        value_error = ValueError("Unrecognized neta.data.format datetime "
                                 "precision option %s" % repr(precision))
        raise value_error

def datetime_silk_hour(value):
    """
    Format *value* as a SiLK format datetime to the precision of an
    hour (``YYYY/MM/DDTHH``).  Implicitly coerces time into UTC.  This
    is shorthand for ``datetime_silk(value, precision=DATETIME_HOUR)``.

    Example::

        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007")
        >>> datetime_silk_hour(t)
        '2010/02/03T04'
    """
    return datetime_silk(value, precision=DATETIME_HOUR)

def datetime_silk_day(value):
    """
    Format *value* as a SiLK format datetime to the precision of a day
    (``YYYY/MM/DD``).  Implicitly coerces time into UTC.  This is
    shorthand for ``datetime_silk(value, precision=DATETIME_DAY)``.

    Example::

        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007")
        >>> datetime_silk_day(t)
        '2010/02/03'
    """
    return datetime_silk(value, precision=DATETIME_DAY)

def _iso_tzname(v):
    """
    Returns a string representation of the ISO timezone offeset, or
    the empty string if there is none or it is UTC.
    """
    offset = v.utcoffset()
    if offset is None:
        return ""
    offset = offset.seconds // 60
    if offset == 0:
        return ""
    else:
        return "%+03d:%02d" % divmod(offset, 60)

def datetime_iso(value, precision=DATETIME_SECOND):
    """
    Format *value* as an ISO 8601 extended format date and time
    (``YYYY/MM/DDTHH:MM:SS.SSSSSS[TZ]``).  Includes timezone offset
    unless the value has no timezone or the value's timezone is UTC.

    *precision* is the amount of precision that should be included in
    the output.

    For a more general way to round times, see
    :func:`netsa.data.times.bin_datetime`.  See also
    :func:`datetime_silk_hour` and :func:`datetime_silk_day` for the
    most common ways to format incomplete dates in SiLK format.    

    Examples::

        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007008")
        >>> datetime_iso(t)
        '2010-02-03T04:05:06'
        >>> datetime_iso(t, precision=DATETIME_YEAR)
        '2010'
        >>> datetime_iso(t, precision=DATETIME_MONTH)
        '2010-02'
        >>> datetime_iso(t, precision=DATETIME_DAY)
        '2010-02-03'
        >>> datetime_iso(t, precision=DATETIME_HOUR)
        '2010-02-03T04'
        >>> datetime_iso(t, precision=DATETIME_MINUTE)
        '2010-02-03T04:05'
        >>> datetime_iso(t, precision=DATETIME_SECOND)
        '2010-02-03T04:05:06'
        >>> datetime_iso(t, precision=DATETIME_MSEC)
        '2010-02-03T04:05:06.007'
        >>> datetime_iso(t, precision=DATETIME_USEC)
        '2010-02-03T04:05:06.007008'
        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007008+09:10", utc_only=False)
        >>> datetime_iso(t)
        '2010-02-03T04:05:06+09:10'
    """
    v = value
    if precision == DATETIME_USEC:
        return ("%04d-%02d-%02dT%02d:%02d:%02d.%06d%s" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 v.microsecond, _iso_tzname(v)))
    elif precision == DATETIME_MSEC:
        return ("%04d-%02d-%02dT%02d:%02d:%02d.%03d%s" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 v.microsecond // 1000, _iso_tzname(v)))
    elif precision == DATETIME_SECOND:
        return ("%04d-%02d-%02dT%02d:%02d:%02d%s" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 _iso_tzname(v)))
    elif precision == DATETIME_MINUTE:
        return ("%04d-%02d-%02dT%02d:%02d%s" %
                (v.year, v.month, v.day, v.hour, v.minute, _iso_tzname(v)))
    elif precision == DATETIME_HOUR:
        return ("%04d-%02d-%02dT%02d%s" %
                (v.year, v.month, v.day, v.hour, _iso_tzname(v)))
    elif precision == DATETIME_DAY:
        return ("%04d-%02d-%02d%s" %
                (v.year, v.month, v.day, _iso_tzname(v)))
    elif precision == DATETIME_MONTH:
        return ("%04d-%02d%s" %
                (v.year, v.month, _iso_tzname(v)))
    elif precision == DATETIME_YEAR:
        return ("%04d%s" %
                (v.year, _iso_tzname(v)))
    else:
        value_error = ValueError("Unrecognized neta.data.format datetime "
                                 "precision option %s" % repr(precision))
        raise value_error        

def _iso_tzname_basic(v):
    """
    Returns a string representation of the ISO basic format timezone
    offeset, or the empty string if there is none or it is UTC.
    """
    offset = v.utcoffset()
    if offset is None:
        return ""
    offset = offset.seconds // 60
    if offset == 0:
        return ""
    else:
        return "%+03d%02d" % divmod(offset, 60)

def datetime_iso_basic(value, precision=DATETIME_SECOND):
    """
    Format *value* as an ISO 8601 basic (compact) format date and time
    (``YYYYMMDDTHHMMSS.SSSSSS[TZ]``).  Includes timezone offset unless
    the value has no timezone or the value's timezone is UTC.

    *precision* is the amount of precision that should be included in
    the output.  Note that in accordance with the ISO 8601
    specification, this format does not support the
    :const:`DATETIME_MONTH` precision, because ``YYYYMM`` and
    ``YYMMDD`` would be potentially ambiguous.

    For a more general way to round times, see
    :func:`netsa.data.times.bin_datetime`.  See also
    :func:`datetime_silk_hour` and :func:`datetime_silk_day` for the
    most common ways to format incomplete dates in SiLK format.    

    Examples::

        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007008")
        >>> datetime_iso_basic(t)
        '20100203T040506'
        >>> datetime_iso_basic(t, precision=DATETIME_YEAR)
        '2010'
        >>> datetime_iso_basic(t, precision=DATETIME_DAY)
        '20100203'
        >>> datetime_iso_basic(t, precision=DATETIME_HOUR)
        '20100203T04'
        >>> datetime_iso_basic(t, precision=DATETIME_MINUTE)
        '20100203T0405'
        >>> datetime_iso_basic(t, precision=DATETIME_SECOND)
        '20100203T040506'
        >>> datetime_iso_basic(t, precision=DATETIME_MSEC)
        '20100203T040506.007'
        >>> datetime_iso_basic(t, precision=DATETIME_USEC)
        '20100203T040506.007008'
        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007008+09:10", utc_only=False)
        >>> datetime_iso_basic(t)
        '20100203T040506+0910'
    """
    v = value
    if precision == DATETIME_USEC:
        return ("%04d%02d%02dT%02d%02d%02d.%06d%s" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 v.microsecond, _iso_tzname_basic(v)))
    elif precision == DATETIME_MSEC:
        return ("%04d%02d%02dT%02d%02d%02d.%03d%s" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 v.microsecond // 1000, _iso_tzname_basic(v)))
    elif precision == DATETIME_SECOND:
        return ("%04d%02d%02dT%02d%02d%02d%s" %
                (v.year, v.month, v.day, v.hour, v.minute, v.second,
                 _iso_tzname_basic(v)))
    elif precision == DATETIME_MINUTE:
        return ("%04d%02d%02dT%02d%02d%s" %
                (v.year, v.month, v.day, v.hour, v.minute,
                 _iso_tzname_basic(v)))
    elif precision == DATETIME_HOUR:
        return ("%04d%02d%02dT%02d%s" %
                (v.year, v.month, v.day, v.hour, _iso_tzname_basic(v)))
    elif precision == DATETIME_DAY:
        return ("%04d%02d%02d%s" %
                (v.year, v.month, v.day, _iso_tzname_basic(v)))
    elif precision == DATETIME_MONTH:
        value_error = ValueError("datetime_iso_basic format does not support "
                                 "precision option DATETIME_MONTH")
        raise value_error
    elif precision == DATETIME_YEAR:
        return ("%04d%s" %
                (v.year, _iso_tzname_basic(v)))
    else:
        value_error = ValueError("Unrecognized neta.data.format datetime "
                                 "precision option %s" % repr(precision))
        raise value_error

def datetime_iso_day(value):
    """
    Format *value* as an ISO 8601 extended format date to the
    precision of a day (``YYYY-MM-DD[TZ]``).  Includes timezone offset
    unless the value has no timezone or the value's timezone is UTC.
    This is shorthand for ``datetime_iso(value,
    precision=DATETIME_DAY)``.

    Example::

        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007")
        >>> datetime_iso_day(t)
        '2010-02-03'
        >>> t = netsa.data.times.make_datetime("2010-02-03T04:05:06.007+03:00", utc_only=False)
        >>> datetime_iso_day(t)
        '2010-02-03+03:00'
    """
    return datetime_iso(value, precision=DATETIME_DAY)

def timedelta_iso(value):
    """
    Format a :class:`datetime.timedelta` object as a str in ISO 8601
    duration format, minus 'year' and 'month' designators
    (``P[n]DT[n]H[n]M[n]S``). Fractional seconds will represented using
    decimal notation in the seconds field.

    Note that conversions between units are precise and do not take into
    account any calendrical context. In particular, a day is exactly
    24*3600 seconds, just like :class:`datetime.timedelta` uses.

    If you apply the resulting timedelta to a datetime and the interval
    happens to include something like leap seconds adjust your
    expectations accordingly.

    Since :class:`datetime.timedelta` has no internal representation of
    months or years, these units are never included in the result.

    Examples::

        >>> t1 = netsa.data.times.make_datetime("2010-02-03T04:05:06.007008")
        >>> t2 = netsa.data.times.make_datetime("2010-02-04T05:06:07.008009")
        >>> t3 = netsa.data.times.make_datetime("2010-02-03T04:06:06.008009")
        >>> d1 = t2 - t1
        >>> d2 = t3 - t1
        >>> timedelta_iso(d1)
        >>> 'P1DT1H1M1.001001S'
        >>> timedelta_iso(d2)
        >>> 'PT1M0.001001S'
    """
    d = "P"
    if value.days < 0:
        value = -value
        d = "-P"
    if value.days:
        d += "%dD" % value.days
    if value.seconds or value.microseconds:
        d += "T"
        hours, seconds   = divmod(value.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if hours:
            d += "%dH" % hours
        if minutes:
            d += "%dM" % minutes
        if value.microseconds:
            d += "%fS" % float("%d.%06d" % (seconds, value.microseconds))
        elif seconds:
            d += "%dS" % seconds
    elif not value.days:
        d += "0D"
    return d

__all__ = """

    num_fixed
    num_exponent
    num_prefix

    DATETIME_YEAR
    DATETIME_MONTH
    DATETIME_DAY
    DATETIME_HOUR
    DATETIME_MINUTE
    DATETIME_SECOND
    DATETIME_MSEC
    DATETIME_USEC

    datetime_silk
    datetime_silk_hour
    datetime_silk_day

    datetime_iso
    datetime_iso_day

    datetime_iso_basic

    timedelta_iso

""".split()
