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

import os, re, sys, itertools

from os       import path
from datetime import datetime

from netsa.data.times  import make_datetime
from netsa.util.tandem import dzip

class DateFileParseError(Exception):
    """
    Raised if a function is unable to parse a date within the provided
    filename.
    """
    pass

def warning(msg):
    print >> sys.stderr, msg

def date_from_file(file):
    """
    Attempt to extract dates from a filename. The filename can be a
    full pathname or relative path. Dates are presumed to exist
    somewhere in the pathname.  See :func:`split_on_date` for more
    detail on how dates are parsed from filenames.
    """
    (dir, chop) = split_on_date(file)
    ymd = {}
    for (i, field) in ( (1, 'year'), (3, 'month'),  (5, 'day'),
                        (7, 'hour'), (9, 'minute'), (11, 'second') ):
        if field in ('day', 'month'):
            ymd[field] = chop[i] or 1
        else:
            ymd[field] = chop[i] or 0
    try:
        return make_datetime(datetime(**ymd), utc_only=True)
    except ValueError, e:
        msg = str(e)
        msg += "\nproblem extracting date from %s" % file
        raise DateFileParseError, msg

def split_on_date(file):
    """
    Given a string (presumably the pathname to a file) with a date in
    it, return the directory of the file and the date/non-date
    components of the file name as an array. This routine is pretty
    liberal about what constites a valid date format since it expects,
    by contract, a filename with a date string embedded within it.

    For example, the input ``"foo/bar-20090120:12:17:21.txt"`` parses
    to::
    
      ('foo', ['bar-', 2009, None, 1, None, 20, ':", 12, ':', 17, ':', 21, '.txt'])

    The following are all valid dates::

      2008
      200811
      20081105
      2008/11
      2008/11/05
      2008-11-05
      2008.11.05
      2008-11-05:07
      2008-11-05:07:11
      2008-11-05:07:11:00

    Separators between year/month/day are 'non digits'. This implies
    that directories within the path string can contribute to the
    date along with information in the filename itself. The
    following is valid::

      '/path/to/2008/11/05.txt'
      
    The extraction is non-greedy: only the 'last' part that looks like a
    date is extracted. For example::

      '/path/to/2008/11/2008-11-05.txt'

    extracts only '2008-11-05' from the end of the string.

    Separators between hour/minute/sec must be ':'
    """
    pat = re.compile( \
        "(\d{4})(\D)?(\d\d)?(\D)?(\d\d)?((:)(\d\d))?((:)(\d\d))?((:)(\d\d))?")
    suffix = None
    while True:
        (dir, base) = path.split(file)
        if suffix is None:
            suffix = base
        else:
            suffix = path.join(base, suffix)
        chop = pat.split(suffix, 1)
        if chop:
            break
        if not dir:
            break
    if not chop or len(chop) != 16:
        raise DateFileParseError, "could not split on date: %s" % file
    # drop :00 (indices 6, 9, 12)
    chop = [chop[i] for i in (0, 1, 2, 3, 4, 5, 7, 8, 10, 11, 13, 14, 15)]
    for i in (1, 3, 5, 7, 9, 11):
        try:
            if chop[i] != None:
                chop[i] = int(chop[i])
        except TypeError:
            raise DateFileParseError, "could not split on date: %s" % file
    return (dir, chop)

def date_file_template(file, wildcard='x'):
    """
    Given a pathname *file*, returns the string with ``'x'`` in place
    of date components. The replacement character can be overridden
    with the *wildcard* argument.

    This is useful for determining what dated naming series are present
    in a shared directory.
    """
    if len(wildcard) > 1:
        raise ValueError, "wildcard must be a single character"
    (dir, chop) = split_on_date(file)
    if chop[1] != None:
        chop[1] = 4 * wildcard
    for i in (3, 5, 7, 9, 11):
        if chop[i] != None:
            chop[i] = 2 * wildcard
    return path.join(dir, ''.join(filter(lambda x: x, chop)))

def sibling_date_files(file, dates):
    """
    Given a pathname *file* containing a date, along with a list of
    target dates *dates*, returns an iterator of analagous filenames
    corresponding to each date in *dates*. No attempt is made to check
    whether the resulting files actually exist on the filesystem.

    Example of use:

    Imagine a directory containing a series of dated files such as the
    following::

        foo-YYYY-MM-DD.dat
        bar-YYYY-MM-DD.dat
        baz-YYYY-MM-DD.dat
        YYYY-MM-DD.tweedle.dat

    This routine allows you to easily pull apart the foo, bar, baz, and
    tweedle naming sequences as separate iterators.
    """
    (dir, chop) = split_on_date(file)
    for date in dates:
        if chop[1] != None:
            chop[1] = "%04d" % date.year
        items = {
            3  : date.month,
            5  : date.day,
            7  : date.hour,
            9  : date.minute,
            11 : date.second
        }
        for (i, item) in items.iteritems():
            if chop[i] != None:
                chop[i] = "%02d" % item
        yield path.join(dir, ''.join(filter(lambda x: x, chop)))

def sibling_date_file(file, date):
    """
    Given a filename *file*, along with a date, returns the analagous
    filename corresponding to that date.
    """
    res = list(sibling_date_files(file, [date]))
    if res:
        return res[0]

def datefile_walker(dir, suffix=None,
                    silent=False, snapper=None, descend=True, reverse=False):
    """
    Returns an iterator based on the dated files that exist in
    directory *dir*.  Each value returned by the iterator is a tuple
    of ``(date, [file1, file2, ...])``, where each file matches the
    given date.  See :func:`split_on_date` for more detail on how
    dates are parsed from filenames.

    If *descend* is ``True``, the entire directory tree will be
    traversed.  Otherwise, only the top-level directory is examined.

    If *reverse* is ``True``, the iterator returns entries for each
    date in descending order.  Otherwise, entries are returns in
    ascending order.

    If a :class:`netsa.data.times.DateSnapper` *snapper* is provided,
    it will be used to enforce the alignment of dates, throwing a
    :exc:`ValueError` if a misaligned date is encountered.
    """
    if not path.isdir(dir):
        raise ValueError, "not a directory: %s" % dir
    if suffix:
        if suffix[0] != '.':
            suffix = '.' + suffix
    dates_seen = set()
    datefiles = []
    for (dir, dirnames, files) in os.walk(dir):
        for file in files:
            if suffix and not re.search('%s$' % re.escape(suffix), file):
                continue
            try:
                d = date_from_file(file)
            except DateFileParseError:
                continue
            if d in dates_seen and not silent:
                warning("duplicate date (%s) from %s" % \
                    (d, path.join(dir,file)))
                continue
            if snapper and not snapper.date_aligned(d):
                date_bin = snapper.date_bin(d)
                warning("misaligned: %s" % file)
                raise ValueError, "misaligned date: %s != %s" % (d, date_bin)
            dates_seen.add(d)
            datefiles.append((d, path.join(dir, file)))
        if not descend:
            break
    datefiles = sorted(datefiles)
    if reverse:
        datefiles.reverse()
    return tuple(datefiles)

def latest_datefile(dir, suffix=None,
                    silent=False, snapper=None, descend=True):
    """
    Traverses the given directory and returns a single tuple ``(date,
    [file1, file2, ...])`` where date is the latest date present and
    each file in the list contains that date.  See
    :func:`split_on_date` for more detail on how dates are parsed from
    filenames.

    If *descend* is ``True``, the entire directory tree is traversed
    recursively.  Otherwise, only the top-level directory is examined.

    If a :class:`netsa.data.times.DateSnapper` *snapper* is provided, it
    will be used to enforce the alignment of dates, throwing a
    :exc:`ValueError` if a misaligned date is encountered.
    """

    dates = datefile_walker(dir, suffix=suffix, silent=silent,
                            snapper=snapper, descend=descend, reverse=True)
    for d in dates:
        return d

def datedir_walker(dirname, silent=False):
    """
    Returns an iterator based on the directories contained within the
    given directory.  Each value returned by the iterator is a tuple
    ``(date, dir)`` where the directory's name matches the given date.
    See :func:`split_on_date` for more detail on how dates are parsed
    from filenames.

    If *silent* is ``False``, warnings are emitted when duplicate
    dates are encountered.  Otherwise, the warnings are suppressed.
    """
    if not path.isdir(dirname):
        raise ValueError, "not a directory: %s" % dirname
    dates_seen = set()
    dates = []
    for (dir, dirnames, files) in os.walk(dirname):
        if dir == dirname:
            continue
        try:
            d = date_from_file(dir)
        except DateFileParseError:
            continue
        if d in dates_seen and not silent:
            warning("duplicate date (%s) from %s" % \
                (d, path.join(dir,file)))
            continue
        dates_seen.add(d)
        dates.append((d, dir))
    for item in sorted(dates):
        yield item

def date_snap_walker(dir, snapper, suffix=None, sparse=True):
    """
    Returns an iterator based on traversing the given directory.  Each
    value returned by the iterator is a tuple ``(date_bin, ((date,
    file), (date2, file2), ...))`` where each filename contains a date
    which falls within the given date bin (as defined by *snapper*).

    The beginning and ending dates for this sequence are determined by
    what files are present on the system. If *spare* is ``True``, then
    only date bins which are actually occupied by files in the
    directory are emitted.  Otherwise, a tuple is generated for each
    date between the smallest and largest dates present in the
    directory.  See :class:`netsa.data.times.DateSnapper` for more
    information on date bins.

    If *suffix* is provided, all files not ending with the provided
    extension are ignored.
    """
    dwalker = datefile_walker(dir, suffix=suffix, silent=True)
    bwalker = ((snapper.date_bin(d), d, f) for d, f in dwalker)
    last_bin = None
    for date_bin, g in itertools.groupby(bwalker, lambda x: x[0]):
        if not sparse and last_bin:
            while last_bin < date_bin:
                yield last_bin, tuple()
                last_bin = snapper.next_date_bin(last_bin)
        yield date_bin, ((x[1], x[2]) for x in g)
        last_bin = snapper.next_date_bin(date_bin)

def tandem_datefile_walker(sources, suffix=None,
                           silent=True, snapper=None, reverse=False):
    """
    Returns an iterator based on traversing multiple directories given
    by *sources*.  Each value returned by the iterator is a tuple
    ``(date, (dir, file), (dir2, file2), ...)``, where the given
    directory contains the given file, which contains this date in its
    name.  See :func:`split_on_date` for more detail on how dates are
    parsed from filenames.

    For example, given: ``('/dir/one', /dir/two')``, a returned tuple
    might look like::

       (date, ('/dir/one', file_from_dir_one_containing_date_in_its_name),
              ('/dir/two', file_from_dir_two_containing_date_in_its_name),
              ('/dir/two', another_file_from_dir_two_with_date_in_its_name))

    If *suffix* is provided, all files not ending with the provided
    extension are ignored.

    If *reverse* is ``True``, tuples are generated with dates in
    descending order.  Otherwise, dates are generated in ascending
    order.

    If a :class:`netsa.data.times.DateSnapper` *snapper* is provided,
    it will be used to enforce the alignment of dates, throwing a
    :exc:`ValueError` if a misaligned date is encountered.
    """
    def _dwalk(d):
        w = datefile_walker(d, suffix=suffix,
                            silent=silent, snapper=snapper, reverse=reverse)
        for date, files in w:
            yield date, (d, files)
    walkers = [[x for x in _dwalk(dir)] for dir in sources]
    return dzip(*walkers)

__all__ = """
    date_from_file
    split_on_date
    date_file_template
    sibling_date_file
    datefile_walker
    latest_datefile
    date_snap_walker
    tandem_datefile_walker

    DateFileParseError
""".split()
