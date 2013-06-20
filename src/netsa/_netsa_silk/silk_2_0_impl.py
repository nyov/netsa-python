# Copyright 2008-2012 by Carnegie Mellon University

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

import silk

from silk import ipv6_enabled as has_IPv6Addr
from silk import IPAddr, IPv4Addr
if has_IPv6Addr():
    from silk import IPv6Addr
from silk import IPSet as ip_set
from silk import IPWildcard, TCPFlags

_IPSet_old_union = ip_set.union
_IPSet_old_intersection = ip_set.intersection
_IPSet_old_difference = ip_set.difference
_IPSet_old_update = ip_set.update
_IPSet_old_intersection_update = ip_set.intersection_update
_IPSet_old_difference_update = ip_set.difference_update
@classmethod
def _IPSet_supports_IPv6(cls):
    """
    Returns True is this ip_set supports IPv6 addresses.
    """
    return False
def _IPSet_pop(self):
    """
    Remove and return an arbitrary set element.
    Raises KeyError if the set is empty.
    """
    for x in self:
        self.discard(x)
        return x
    raise KeyError('pop from an empty IPSet')
def _IPSet_union(self, *iterables):
    """
    Return the union of two or more ip_sets as a new ip_set.
    (i.e. all elements that are in any set.)
    """
    self = self.copy()
    for other in iterables:
        self = _IPSet_old_union(self, other)
    return self
def _IPSet_intersection(self, *iterables):
    """
    Return the intersection of two or more ip_sets as a new ip_set.
    (i.e. elements that are common to all of the sets.)
    """
    self = self.copy()
    for other in iterables:
        self = _IPSet_old_intersection(self, other)
    return self
def _IPSet_difference(self, *iterables):
    """
    Return the difference of two or more ip_sets as a new ip_set.
    (i.e. elements that are in this set but not the others.)
    """
    self = self.copy()
    for other in iterables:
        self = _IPSet_old_difference(self, other)
    return self
def _IPSet_update(self, *iterables):
    """
    Updates the ip_set with the union of itself and others.
    """
    for other in iterables:
        _IPSet_old_update(self, other)
    return self
def _IPSet_intersection_update(self, *iterables):
    """
    Updates the ip_set with the intersection of itself and others.
    """
    for other in iterables:
        _IPSet_old_intersection_update(self, other)
    return self
def _IPSet_difference_update(self, *iterables):
    """
    Updates the ip_set with the difference of itself and others.
    """
    for other in iterables:
        _IPSet_old_difference_update(self, other)
    return self
ip_set.supports_IPv6 = _IPSet_supports_IPv6
ip_set.pop = _IPSet_pop
ip_set.union = _IPSet_union
ip_set.intersection = _IPSet_intersection
ip_set.difference = _IPSet_difference
ip_set.update = _IPSet_update
ip_set.intersection_update = _IPSet_intersection_update
ip_set.difference_update = _IPSet_difference_update
# TCPFlags attributes - names not fixable
# TCPFlags constants - easy to rename
from silk import FIN as TCP_FIN
from silk import SYN as TCP_SYN
from silk import RST as TCP_RST
from silk import PSH as TCP_PSH
from silk import ACK as TCP_ACK
from silk import URG as TCP_URG
from silk import ECE as TCP_ECE
from silk import CWR as TCP_CWR
# IPWildcard - make constructor accept IPWildcard value
_IPWildcard_old = IPWildcard
def _IPWildcard(v):
    if isinstance(v, _IPWildcard_old):
        return v
    else:
        return _IPWildcard_old(v)
IPWildcard = _IPWildcard
# IPv6Addr - provide a no-op class if needed
if not has_IPv6Addr():
    def IPv6Addr(x):
        raise NotImplementedError("netsa_silk.IPv6Addr")
