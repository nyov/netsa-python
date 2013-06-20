# Copyright 2011 by Carnegie Mellon University

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
