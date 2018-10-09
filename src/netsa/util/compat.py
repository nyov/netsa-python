# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import sys

if sys.version_info < (2, 5):
    import __builtin__
    def any(items):
        for x in items:
            if x:
                return True
        return False
    def all(items):
        for x in items:
            if not x:
                return False
        return True
    __builtin__.any = any
    __builtin__.all = all

if sys.version_info < (2, 6):
    # itertools.product
    import itertools
    def product(*iters):
        if not iters:
            yield ()
        else:
            for a in iters[0]:
                for bs in product(*iters[1:]):
                    yield (a,) + bs
    itertools.product = product

    # os.path.relpath
    import os.path
    from netsa.files import relpath
    os.path.relpath = relpath

    # heapq.merge
    import heapq, bisect
    def merge(*iterators):
        queue = []
        for it in iterators:
            it = iter(it)
            try:
                bisect.insort(queue, (it.next(), it))
            except StopIteration:
                pass
        while queue:
            val, it = queue.pop(0)
            yield val
            try:
                bisect.insort(queue, (it.next(), it))
            except StopIteration:
                pass
    heapq.merge = merge

# potential example for when a module does not exist:
#
# >>> import blahblah
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# ImportError: No module named blahblah
# >>> import sys, imp
# >>> try:
# ...     import blahblah
# ... except ImportError:
# ...     sys.modules['blahblah'] = imp.new_module('blahblah')
# ...     import blahblah
# ...
# >>> import blahblah

__all__ = []
