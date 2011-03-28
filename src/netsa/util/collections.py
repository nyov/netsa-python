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

import bisect
import itertools

def imerge(*iterators, **kwargs):
    """
    Given several sorted iterables, returns an iterator that yields
    the sequentially merged items.

    If *reversed* is ``True``, merging is done under the assumption
    that values are presented in reverse order.
    """

    try:
        reversed = kwargs.pop('reversed')
    except KeyError:
        reversed = False
    if kwargs:
        type_error = TypeError("imerge() got an unexpected keyword argument %s"
                               % repr(kwargs.iterkeys().next()))
        raise type_error
    queue = []
    for it in iterators:
        it = iter(it)
        try:
            bisect.insort(queue, (it.next(), it))
        except StopIteration:
            pass
    while queue:
        if reversed:
            val, it = queue.pop(-1)
        else:
            val, it = queue.pop(0)
        yield val
        try:
            bisect.insort(queue, (it.next(), it))
        except StopIteration:
            pass

def dzip(*iterators, **kwargs):
    """
    Given several dicts or sorted iterables of key/value pairs,
    returns an iterator which yields pairs ``(key, values)`` pairing
    each key with its collected values.

    If *reversed* is ``True``, merging is done under the assumption
    that values are presented in reverse order.
    """

    try:
        reversed = kwargs.pop('reversed')
    except KeyError:
        reversed = False
    if kwargs:
        type_error = TypeError("dzip() got an unexpected keyword argument %s"
                               % repr(kwargs.iterkeys().next()))
        raise type_error
    iterators = list(iterators)
    for i, it in enumerate(iterators):
        try:
            # convert dictionaries to sorted k,v sequence
            iterators[i] = sorted(it.iteritems(), reverse=reversed)
        except AttributeError:
            pass
    for k,vs in itertools.groupby(imerge(reversed=reversed, *iterators),
                                  key=lambda (k,v): k):
        yield k, tuple(xs for l,xs in vs)


# requirements of elements:
# 1) a - b is a meaningful "distance"
# 2) fully ordered

class range_set(object):
    # _ranges is kept in sorted order, non-overlapping ranges, coalesced
    __slots__ = ('_ranges')
    def __init__(self, iterable=None):
        self._ranges = []
        if iterable != None:
            self._ranges = list(self._range_iter(iterable)) 

    # The following methods (through _out_conv) are particularly
    # useful to override to create type-specific subclasses.

    def _cmp(self, a, b):
        """
        Compares two elements of this set, returning -1 if a < b, 0 if
        a == b, and 1 if a > b.
        """
        return cmp(a, b)
    def _succ(self, x):
        """
        Returns the successor of an item in this set.  That is, the
        next higher adjacent value.
        """
        return x + 1
    def _pred(self, x):
        """
        Returns the predecessor of an item in this set.  That is, the
        next lower adjacent value.
        """
        return x - 1
    def _diff(self, a, b):
        """
        Returns the difference of two values in this set.  That is, the
        number of values in the closed interval [a,b].
        """
        return a - b
    def _in_conv(self, x):
        """
        Returns the internal representation of a value in this set,
        given the external representation.  This is useful if it is
        easy to convert between the external representation and
        integers, for example.
        """
        return x
    def _out_conv(self, x):
        """
        Returns the external representation of a value in this set,
        given the internal representation.  This is useful if it is
        easy to convert between the external representation and
        integers, for example.
        """
        return x

    # The above methods (through _cmp) are particularly useful to
    # override to create type-specific subclasses.

    def _range_merge(self, xs, ys):
        """
        Merges two sorted iterators of ranges.  Each result is a tuple
        ``((a, b), c)`` where ``(a, b)`` is a range of values, and
        ``c`` is -1 if the range is present only in *ys*, 1 if the
        range is present only in *xs*, and 0 if the range is present
        in both.
        """
        try:
            (xa, xb) = xs.next()
        except StopIteration:
            while True: yield (ys.next(), -1)
            return
        try:
            (ya, yb) = ys.next()
        except StopIteration:
            yield ((xa, xb), 1)
            while True: yield (xs.next(), 1)
        while True:
            if self._cmp(xa, ya) < 0: # xa < ya
                if self._cmp(xb, ya) < 0: # xb < ya
                    yield ((xa, xb), 1)
                    try:
                        (xa, xb) = xs.next()
                    except StopIteration:
                        yield ((ya, yb), -1)
                        while True: yield (ys.next(), -1)
                else: # xb >= ya
                    yield ((xa, self._pred(ya)), 1)
                    (xa, xb) = (ya, xb)
            elif self._cmp(xa, ya) > 0: # xa > ya
                if self._cmp(yb, xa) < 0: # yb < xa
                    yield ((ya, yb), -1)
                    try:
                        (ya, yb) = ys.next()
                    except StopIteration:
                        yield ((xa, xb), 1)
                        while True: yield (xs.next(), 1)
                else: # yb >= xa
                    yield ((ya, self._pred(xa)), -1)
                    (ya, yb) = (xa, yb)
            else: # xa == ya
                if self._cmp(xb, yb) == 0: # xb == yb
                    yield ((xa, xb), 0)
                    try:
                        (xa, xb) = xs.next()
                    except StopIteration:
                        while True: yield (ys.next(), -1)
                    try:
                        (ya, yb) = ys.next()
                    except StopIteration:
                        yield ((xa, xb), 1)
                        while True: yield (xs.next(), 1)
                elif self._cmp(xb, yb) < 0: # xb < yb
                    yield ((xa, xb), 0)
                    (ya, yb) = (self._succ(xb), yb)
                    try:
                        (xa, xb) = xs.next()
                    except StopIteration:
                        yield ((ya, yb), -1)
                        while True: yield (ys.next(), -1)
                else: # yb < xb
                    yield ((xa, yb), 0)
                    (xa, xb) = (self._succ(yb), xb)
                    try:
                        (ya, yb) = ys.next()
                    except StopIteration:
                        yield ((xa, xb), 1)
                        while True: yield (xs.next(), 1)
    def _range_iter(self, other):
        """
        Converts a collection or a range_set into an iterator for use
        in internal functions.  If the type of *other* is the same as
        the type of *self*, no conversion is done at all.  If *other*
        has a method ``iterranges()``, the ranges from that method are
        used after conversion via :meth:`_in_conv`.  If the first item
        resulting from *other* is a pair, the values of each pair are
        converted via :meth:`_in_conv`.  Finally, if none of the above
        is true, the values from *other* are sorted, converted via
        :meth:`_in_conv`, and yielded as pairs.
        """
        if type(self) == type(other):
            # Other is identical, use _ranges directly.
            for ab in other._ranges:
                yield ab
            return
        # Not identical.  Try using iterranges()
        try:
            ys = other.iterranges()
            while True:
                (ya, yb) = ys.next()
                yield (self._in_conv(ya), self._in_conv(yb))
            return
        except AttributeError:
            pass
        ys = iter(sorted(other))
        y = ys.next()
        try:
            (ya, yb) = y
            pairs = True
        except:
            pairs = False
        if pairs:
            while True:
                yield (self._in_conv(ya), self._in_conv(yb))
                (ya, yb) = ys.next()
        else:
            y = self._in_conv(y)
            while True:
                yield (y, y)
                y = self._in_conv(ys.next())
    def _range_coalesce(self, xs):
        """
        Coalesces a sorted iterator of ranges.  This combines
        overlapping ranges and stiches adjacent ranges together.
        """
        (xa, xb) = xs.next()
        while True:
            try:
                (nxa, nxb) = xs.next()
            except StopIteration:
                yield (xa, xb)
                break
            if self._cmp(nxa, self._succ(xb)) <= 0: # nxa <= xb + 1:
                if self._cmp(xb, nxb) < 0: # xb < nxb
                    (xa, xb) = (xa, nxb)
                else: # xb >= nxb
                    (xa, xb) = (xa, xb)
            else:
                yield (xa, xb)
                (xa, xb) = (nxa, nxb)
    def _range_without(self, xs, x):
        """
        Given a sorted iterator of range pairs and a value to remove,
        yields every range that should be present without that value.
        """
        while True:
            (xa, xb) = xs.next()
            (ca, cb) = (self._cmp(x, xa), self._cmp(x, xb))
            if ca < 0 or cb > 0: # x < xa or x > xb
                yield (xa, xb)
            if ca == 0 and cb == 0: # x == xa and x == xb
                continue
            elif ca == 0: # x == xa
                yield (self._succ(xa), xb)
            elif cb == 0: # x == xb
                yield (xa, self._succ(xb))
            else: # xa < x and x < xb
                yield (xa, self._pred(x))
                yield (self._succ(x), xb)
    def _check_range(self, other, op_name):
        """
        Checks that the other value is one we should work with via
        operators.  (i.e. a range set)
        """
        try:
            ys = other.iterranges
            return True
        except AttributeError:
            return False
    def __iter__(self):
        """
        Returns an iterator that yields every value from this
        :class:`range_set` individually.
        """
        r = self._ranges
        for (a, b) in r:
            while self._cmp(a, b) <= 0:
                yield self._out_conv(a)
                a = self._succ(a)
    def ranges(self):
        """
        Returns a sorted list of pairs representing the ranges covered
        by this :class:`range_set`.  Each pair ``(a, b)`` represents a
        closed interval of values, indicating that all values ``x``
        such that ``a <= x <= b`` are in the set.
        """
        return list(self.iterranges())
    def iterranges(self):
        """
        Returns an iterator of pairs representing ths ranges covered
        by this :class:`range_set`, in sorted order.  Each pair ``(a,
        b)`` represents a closed interval of values, indicating that
        all values ``x`` such that ``a <= x <= b`` are in the set.
        """
        for (a, b) in self._ranges:
            yield (self._out_conv(a), self._out_conv(b))
    def __len__(self):
        l = 0
        for (a,b) in self._ranges:
            l += self._diff(b, a)
        return l
    def __contains__(self, x):
        x = self._in_conv(x)
        r = self._ranges
        (a, b) = (0, len(r))
        while True:
            if a == b:
                if a < len(r):
                    (ra, rb) = r[a]
                    return (self._cmp(ra, x) <= 0 and self._cmp(x, rb) <= 0)
                else:
                    return False
            i = int((a + b) / 2)
            (ra, rb) = r[i]
            if self._cmp(x, ra) < 0: # x < ra
                if a == i:
                    return False
                (a, b) = (a, i-1)
            elif self._cmp(rb, x) < 0: # rb < x
                if b == i:
                    return False
                (a, b) = (i+1, b)
            else: # ra <= x <= rb
                return True
    def isdisjoint(self, other):
        for (_, c) in self._range_merge(self._range_iter(self),
                                        self._range_iter(other)):
            if c == 0:
                return False
        return True
    def issubset(self, other):
        for (_, c) in self._range_merge(self._range_iter(self),
                                        self._range_iter(other)):
            if c == 1:
                return False
        return True
    def __le__(self, other):
        if not self._check_range(other, "<="): return NotImplemented
        return self.issubset(other)
    def __lt__(self, other):
        if not self._check_range(other, "<"): return NotImplemented
        saw_extra = False
        for (_, c) in self._range_merge(self._range_iter(self),
                                        self._range_iter(other)):
            if c == 1:
                return False
            elif c == -1:
                saw_extra = True
        return saw_extra
    def issuperset(self, other):
        for (_, c) in self._range_merge(self._range_iter(self),
                                        self._range_iter(other)):
            if c == -1:
                return False
        return True
    def __ge__(self, other):
        if not self._check_range(other, ">="): return NotImplemented
        return self.issuperset(other)
    def __gt__(self, other):
        if not self._check_range(other, ">"): return NotImplemented
        saw_extra = False
        for (_, c) in self._range_merge(self._range_iter(self),
                                        self._range_iter(other)):
            if c == -1:
                return False
            elif c == 1:
                saw_extra = True
        return saw_extra
    def union(self, other):
        return self.__class__(
            self._range_coalesce(
                x for (x, _) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))))
    def __or__(self, other):
        if not self._check_range(other, "|"): return NotImplemented
        return self.union(other)
    def intersection(self, other):
        return self.__class__(
            self._range_coalesce(
                x for (x, c) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))
                if c == 0))
    def __and__(self, other):
        if not self._check_range(other, "&"): return NotImplemented
        return self.intersection(other)
    def difference(self, other):
        return self.__class__(
            self._range_coalesce(
                x for (x, c) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))
                if c == 1))
    def __sub__(self, other):
        if not self._check_range(other, "-"): return NotImplemented
        return self.difference(other)
    def symmetric_difference(self, other):
        return self.__class__(
            self._range_coalesce(
                x for (x, c) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))
                if c != 0))
    def __xor__(self, other):
        if not self._check_range(other, "^"): return NotImplemented
        return self.symmetric_difference(other)
    def copy(self):
        return self.__class__(self)
    def __eq__(self, other):
        for (_, c) in self._range_merge(self._range_iter(self),
                                        self._range_iter(other)):
            if c != 0:
                return False
        return True
    def update(self, other):
        self._ranges = list(self._range_coalesce(
                x for (x, _) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))))
    def __ior__(self, other):
        if not self._check_range(other, "|="): return NotImplemented
        self.update(other)
    def intersection_update(self, other):
        self._ranges = list(self._range_coalesce(
                x for (x, c) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))
                if c == 0))
    def __iand__(self, other):
        if not self._check_range(other, "&="): return NotImplemented
        self.intersection_update(other)
    def difference_update(self, other):
        self._ranges = list(self._range_coalesce(
                x for (x, c) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))
                if c == 1))
    def __isub__(self, other):
        if not self._check_range(other, "-="): return NotImplemented
        self.difference_update(other)
    def symmetric_difference_update(self, other):
        self._ranges = list(self._range_coalesce(
                x for (x, c) in
                self._range_merge(self._range_iter(self),
                                  self._range_iter(other))
                if c != 0))
    def __ixor__(self, other):
        if not self._check_range(other, "^="): return NotImplemented
        self.symmetric_difference_update(other)
    def add(self, elem):
        self.update([(elem, elem)])
    def remove(self, elem):
        if elem not in self:
            raise KeyError(elem)
        self.discard(elem)
    def discard(self, elem):
        self._ranges = list(self._range_without(self._range_iter(self), elem))
    def pop(self):
        if len(self._ranges) < 1:
            raise KeyError('pop from an empty range_set')
        (xa, xb) = self._ranges[-1]
        if self._cmp(xa, xb) == 0: # xa == xb
            self._ranges.pop()
            return self._out_conv(xa)
        else:
            self._ranges[-1] = (xa, self._pred(xb))
            return self._out_conv(xb)
    def clear(self):
        self._ranges = []
    def __repr__(self):
        return "range_set(%s)" % repr(self.ranges())

__all__ = """

    range_set

""".split()
