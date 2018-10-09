# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import bisect, itertools

def imerge(*iterators, **kwargs):
    """
    Given a list of presumably pre-sorted iterables, return an iterator
    that yields the sequentially merged items.

    The optional parameter 'reversed' (default: False) specifies
    whether the highest value is picked during each iteration as
    opposed to the lowest value.
    """

    try:
        reversed = kwargs.pop('reversed')
    except KeyError:
        reversed = False
    if kwargs:
        msg = "imerge() got an unexpected keyword argument "
        raise TypeError, msg + "'%s'" % kwargs.keys()[0]
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
    Given a list of pre-sorted iterables that return key/value pairs, or
    dictionaries, return an iterator that yields each key along with its
    grouped values.

    Iterators that yield multiple key/value pairs for the same key are
    fine; those values get grouped along with the values from the other
    iterators.

    The optional parameter 'reversed' (default: False) specifies whether
    the provided iterators generate values in ascending or descending
    order.

    If any of the provided 'iterators' are dictionaries, then an
    iterator that returns key/value pairs in an order based on the value
    of 'reversed' will be used instead.
    """

    try:
        reversed = kwargs.pop('reversed')
    except KeyError:
        reversed = False
    if kwargs:
        msg = "dzip() got an unexpected keyword argument"
        raise TypeError, msg + "'%s'" % kwargs.keys()[0]
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
