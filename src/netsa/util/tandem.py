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
