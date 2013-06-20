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

import sys

def has_IPv6Addr():
    """
    Returns 'True' if IPv6Addr support is available, `False'
    otherwise.  If IPv6Addr support is not available, IPaddr will
    raise ValueError when given an IPv6 address, and any call to
    IPv6Addr will raise NotImplementedError.
    """
    return True

IPv4_MAX = 0xFFFFFFFF;
IPv6_MAX = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;

def _chunk_ipv4(a):
    """
    Takes an address-like string in the form of a dot-separated IPv4
    address and returns strings for each of the v4 octets.
    """
    if not isinstance(a, basestring):
        raise TypeError()
    if '.' not in a:
        raise ValueError()
    ipv4_part = a.split('.')
    if len(ipv4_part) != 4:
        raise ValueError()
    return ipv4_part

def _chunk_ipv6(a):
    """
    Takes an address-like string in the form of a colon-separated IPv6
    address (including '::' zero-filling and with optional v4 part),
    and returns strings for each of the v6 fields, and also strings
    for each of the v4 octets (if a v4 address was present.)  If "::"
    zero-compression is used, the missing fields are returned as "0".
    If an IPv4 address is present, the full eight v6 fields are
    included, with the last two fields as "0".

    Examples:

    "a:b:c::d:e:f" => (["a","b","c","0","0","d","e","f"], None)
    "a:b::1.2.3.4" => (["a","b","0","0","0","0","0","0"], ["1","2","3","4"])
    "0-ffff::random_thing:x.x.x.x" =>
    (["0-ffff","0","0","0","0","random_thing", "0", "0"], ["x","x","x","x"])
    """
    if not isinstance(a, basestring):
        raise TypeError()
    if ':' not in a:
        raise ValueError()
    ipv6_part = []
    ipv4_part = a.split(':')[-1]

    if '.' in ipv4_part:
        # IPv4 addr included
        ipv4_part = _chunk_ipv4(ipv4_part)
        a = ':'.join(a.split(':')[:-1] + ['0', '0'])
    else:
        ipv4_part = None

    if '::' in a:
        if '::' in a.split('::', 1)[1]:
            raise ValueError()
        zero_compression = True
        a0, a1 = (part.split(':') for part in a.split('::'))
        if a0 == ['']: a0 = []
        if a1 == ['']: a1 = []
    else:
        zero_compression = False
        a0, a1 = (a.split(':'), [])

    ipv6_part.extend(a0)
    if zero_compression:
        ipv6_part.extend(['0'] * (8 - len(a0) - len(a1)))
    ipv6_part.extend(a1)

    if len(ipv6_part) != 8:
        raise ValueError()

    return (ipv6_part, ipv4_part)

def _parse_ipv4(addr):
    try:
        a = addr
        if not isinstance(a, (basestring, int, long)):
            raise TypeError()
        try:
            a = int(a)
        except ValueError:
            a = a.strip()
            ipv4_part = _chunk_ipv4(a)
            a = 0
            for octet in ipv4_part:
                if ' ' in octet:
                    raise ValueError()
                octet = int(octet, 10)
                if octet < 0 or octet > 255:
                    raise ValueError()
                a <<= 8
                a |= octet
        if a < 0 or a > IPv4_MAX:
            raise ValueError()
        return a
    except ValueError:
        value_error = ValueError("Invalid IPv4 address: %r" % addr)
        raise value_error
    except TypeError:
        type_error = TypeError(
            "IPv4 value must be a string, integer, or IPAddr: %r" % addr)
        raise type_error

def _parse_ipv6(addr):
    try:
        a = addr
        if not isinstance(a, (basestring, int, long)):
            raise TypeError()
        try:
            a = int(a)
        except ValueError:
            a = a.strip()
            (ipv6_part, ipv4_part) = _chunk_ipv6(a)
            a = 0
            for field in ipv6_part:
                if ' ' in field:
                    raise ValueError()
                field = int(field, 16)
                if field < 0 or field > 0xFFFF:
                    raise ValueError()
                a <<= 16
                a |= field
            if ipv4_part:
                a4 = 0
                for octet in ipv4_part:
                    if ' ' in octet:
                        raise ValueError()
                    octet = int(octet, 10)
                    if octet < 0 or octet > 255:
                        raise ValueError()
                    a4 <<= 8
                    a4 |= octet
                a |= a4
        if a < 0 or a > IPv6_MAX:
            raise ValueError()
        return a
    except ValueError:
        value_error = ValueError("Invalid IPv6 address: %r" % addr)
        raise value_error
    except TypeError:
        type_error = TypeError(
            "IPv6 value must be a string, integer, or IPAddr: %r" % addr)
        raise type_error

class IPAddr(object):
    __slots__ = ['_addr']
    def __new__(cls, addr):
        if cls == IPAddr:
            if isinstance(addr, IPAddr):
                return addr
            try:
                addr = _parse_ipv4(addr)
                return object.__new__(IPv4Addr)
            except ValueError:
                if str(addr).find(':') == -1:
                    raise
                else:
                    addr = _parse_ipv6(addr)
                    return object.__new__(IPv6Addr)
        else:
            return object.__new__(cls)
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))
    def __hash__(self):
        return hash(self._addr)
    def __nonzero__(self):
        return bool(self._addr)
    def __int__(self):
        return self._addr

def _str_dotted_quad(v):
    v = v & 0xFFFFFFFF
    return ("%d.%d.%d.%d" % tuple((v >> (8*(3-i))) & 0xFF for i in xrange(4)))

class IPv4Addr(IPAddr):
    __slots__ = []
    def __init__(self, addr):
        if isinstance(addr, IPAddr):
            a = addr.to_ipv4()
            if a is None:
                value_error = ValueError(
                    "Cannot convert IPv6 address to IPv4: %r" % addr)
                raise value_error
            self._addr = a._addr
        else:
            self._addr = _parse_ipv4(addr)
    def __cmp__(self, other):
        if not isinstance(other, IPAddr):
            return cmp(self.__class__, other.__class__)
        if other.is_ipv6():
            self = self.to_ipv6()
        return cmp(self._addr, other._addr)
    def is_ipv6(self):
        return False
    def to_ipv4(self):
        return self
    def to_ipv6(self):
        return IPv6Addr(0xFFFF00000000 | (self._addr & 0xFFFFFFFF))
    def __str__(self):
        return _str_dotted_quad(self._addr)
    def padded(self):
        return ('%03d.%03d.%03d.%03d' % self.octets())
    def octets(self):
        a = self._addr
        return tuple((a >> (8*(3-i))) & 0xFF for i in xrange(4))
    def mask(self, mask):
        return IPv4Addr(self._addr & int(mask))
    def mask_prefix(self, len):
        return IPv4Addr(self._addr & (IPv4_MAX << (32-len)) & IPv4_MAX)

class IPv6Addr(IPAddr):
    __slots__ = []
    def __init__(self, addr):
        if isinstance(addr, IPAddr):
            addr = addr.to_ipv6()
            self._addr = addr._addr
        else:
            self._addr = _parse_ipv6(addr)
    def __cmp__(self, other):
        if not isinstance(other, IPAddr):
            return cmp(self.__class__, other.__class__)
        if not other.is_ipv6():
            other = other.to_ipv6()
        return cmp(self._addr, other._addr)
    def is_ipv6(self):
        return True
    def to_ipv4(self):
        if self._addr >= 0xFFFF00000000 and self._addr <= 0xFFFFFFFFFFFF:
            return IPv4Addr(self._addr & 0xFFFFFFFF)
        return None
    def to_ipv6(self):
        return self
    def __str__(self):
        # special case 0, 1, and IPv4 mappings
        if self._addr == 0:
            return "::"
        elif self._addr == 1:
            return "::1"        # localhost
        elif self._addr < 0x100000000:
            return "::" + _str_dotted_quad(self._addr)
        elif self._addr >= 0xFFFF00000000 and self._addr <= 0xFFFFFFFFFFFF:
            return "::ffff:" + _str_dotted_quad(self._addr)
        # otherwise, normal procedure
        shorts = self._shorts()
        max_len = 0
        max_start = 0
        cur_len = 0
        cur_start = 0
        for i in xrange(8):
            if shorts[i] == 0:
                cur_len += 1
            if cur_len > max_len:
                max_len = cur_len
                max_start = cur_start
            if shorts[i] != 0:
                cur_len = 0
                cur_start = i + 1
        if max_len > 1:
            return (':'.join('%x' % q for q in shorts[:max_start]) + '::' +
                    ':'.join('%x' % q for q in shorts[max_start+max_len:]))
        else:
            return (':'.join('%x' % q for q in shorts))
    def padded(self):
        return ("%04x:%04x:%04x:%04x:%04x:%04x:%04x:%04x" % self._shorts())
    def octets(self):
        a = self._addr
        return tuple((a >> (8*(15-i))) & 0xFF for i in xrange(16))
    def _shorts(self):
        a = self._addr
        return tuple((a >> (16*(7-i))) & 0xFFFF for i in xrange(8))
    def mask(self, mask):
        return IPv6Addr(self._addr & int(mask.to_ipv6()))
    def mask_prefix(self, len):
        return IPv6Addr(self._addr & (IPv6_MAX << (128-len)) & IPv6_MAX)

def _ip_conv(addr):
    if isinstance(addr, IPAddr):
        return addr.to_ipv6()
    if isinstance(addr, basestring):
        try:
            return IPAddr(addr).to_ipv6()
        except:
            pass
    type_error = TypeError(
        "Addr must be an IPAddr or parsable IPAddr string: %r" % addr)
    raise type_error

def _ip_iter(iterable):
    if isinstance(iterable, ip_set):
        for v in iterable._content:
            yield v
    else:
        for v in iterable:
            if isinstance(v, IPAddr):
                yield v.to_ipv6()
                continue
            if isinstance(v, IPWildcard):
                for addr in v:
                    yield addr.to_ipv6()
                continue
            if isinstance(v, basestring):
                try:
                    yield IPAddr(v).to_ipv6()
                    continue
                except ValueError:
                    for addr in IPWildcard(v):
                        yield addr.to_ipv6()
                    continue
            type_error = TypeError(
                "iterables must contain IPAddr, IPWildcard, or parsable "
                "strings: %r" % v)
            raise type_error

def _ip_iters(iterables):
    for iterable in iterables:
        for addr in _ip_iter(iterable):
            yield addr

def _ip_iters_check(iterables, s):
    addrs = _ip_iters(iterables)
    if not s._contains_ipv6:
        while True:
            addr = addrs.next()
            yield addr
            if addr._addr < 0xFFFF00000000 or addr._addr > 0xFFFFFFFFFFFF:
                s._contains_ipv6 = True
                break
    while True:
        yield addrs.next()

ip_iters_check = _ip_iters_check

class ip_set(object):
    __slots__ = ['_content', '_contains_ipv6']
    def __init__(self, iterable=None):
        self._content = set()
        self._contains_ipv6 = False
        if iterable:
            self.update(iterable)
    def cardinality(s):
        return len(s._content)
    def __len__(s):
        return s.cardinality()
    def __contains__(s, addr):
        return _ip_conv(addr) in s._content
    def __iter__(s):
        if s._contains_ipv6:
            for addr in s._content:
                yield addr
        else:
            for addr in s._content:
                yield addr.to_ipv4()
    def __eq__(s1, s2):
        if not isinstance(s2, ip_set):
            return False
        return (s1._content == s2._content)
    def __ne__(s1, s2):
        if not isinstance(s2, ip_set):
            return True
        return (s1._content != s2._content)
    def isdisjoint(s, iterable):
        return s._content.isdisjoint(_ip_iter(iterable))
    def issubset(s, iterable):
        return s._content.issubset(_ip_iter(iterable))
    def __le__(s1, s2):
        if not isinstance(s2, ip_set):
            raise TypeError("can only compare to an ip_set")
        return s1._content <= s2._content
    def __lt__(s1, s2):
        if not isinstance(s2, ip_set):
            raise TypeError("can only compare to an ip_set")
        return s1._content < s2._content
    def issuperset(s, iterable):
        return s._content.issuperset(_ip_iter(iterable))
    def __ge__(s1, s2):
        if not isinstance(s2, ip_set):
            raise TypeError("can only compare to an ip_set")
        return s1._content >= s2._content
    def __gt__(s1, s2):
        if not isinstance(s2, ip_set):
            raise TypeError("can only compare to an ip_set")
        return s1._content > s2._content
    def union(s, *iterables):
        result = s.copy()
        result.update(*iterables)
        return result
    def __or__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented
        return s1.union(s2)
    def intersection(s, *iterables):
        result = s.copy()
        result.intersection_update(*iterables)
        return result
    def __and__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented
        return s1.intersection(s2)
    def difference(s, *iterables):
        result = s.copy()
        result.difference_update(*iterables)
        return result
    def __sub__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented        
        return s1.difference(s2)
    def symmetric_difference(s, iterable):
        result = s.copy()
        result.symmetric_difference_update(iterable)
        return result
    def __xor__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented        
        return s1.symmetric_difference(s2)
    def copy(s):
        return s.__class__(s)
    def update(s, *iterables):
        s._content.update(_ip_iters_check(iterables, s))
    def __ior__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented
        s1.update(s2)
        return s1
    def intersection_update(s, *iterables):
        s._content.intersection_update(_ip_iters(iterables))
    def __iand__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented
        s1.intersection_update(s2)
        return s1
    def difference_update(s, *iterables):
        s._content.difference_update(_ip_iters(iterables))
    def __isub__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented
        s1.difference_update(s2)
        return s1
    def symmetric_difference_update(s, iterable):
        s._content.symmetric_difference_update(_ip_iters_check([iterable], s))
    def __ixor__(s1, s2):
        if not isinstance(s2, ip_set): return NotImplemented
        s1.symmetric_difference_update(s2)
        return s1
    def add(s, addr):
        addr = _ip_conv(addr)
        if addr._addr < 0xFFFF00000000 or addr._addr > 0xFFFFFFFFFFFF:
            s._contains_ipv6 = True
        s._content.add(addr)
    def remove(s, addr):
        addr = _ip_conv(addr)
        s._content.remove(addr)
    def discard(s, addr):
        addr = _ip_conv(addr)
        s._content.discard(addr)
    def pop(s):
        addr = s._content.pop()
        if s._contains_ipv6:
            return addr.to_ipv4()
        else:
            return addr
    def clear(s):
        s._contains_ipv6 = False
        s._content.clear()
    def _range_iter(self):
        sorted_ips = sorted(self)
        while sorted_ips:
            range_min = sorted_ips.pop(0)._addr
            range_max = range_min
            while sorted_ips and sorted_ips[0]._addr == range_max + 1:
                range_max = sorted_ips.pop(0)._addr
            if self._contains_ipv6:
                yield (IPv6Addr(range_min), IPv6Addr(range_max))
            else:
                yield (IPv4Addr(range_min & IPv4_MAX),
                       IPv4Addr(range_max & IPv4_MAX))
    def cidr_iter(s):
        for (range_min, range_max) in s._range_iter():
            range_min = range_min._addr
            range_max = range_max._addr
            if s._contains_ipv6:
                bit, bits = 1, 128
                make_ip = IPv6Addr
            else:
                bit, bits = 1, 32
                range_min &= IPv4_MAX
                range_max &= IPv4_MAX
                make_ip = IPv4Addr
            while bits:
                if range_min + bit > range_max:
                    break
                elif range_min & bit:
                    yield make_ip(range_min & ~(bit - 1)), bits
                    range_min += bit
                bit <<= 1
                bits -= 1
            prefix = range_max & ~(bit - 1)
            while bit:
                if prefix + bit - 1 <= range_max:
                    yield make_ip(prefix), bits
                    prefix += bit
                    if prefix > range_max:
                        break
                bit >>= 1
                bits += 1
    @classmethod
    def supports_ipv6(class_):
        return True
    def __repr__(self):
        if self.cardinality() > 100:
            def start_of(iterator):
                c = 0
                for i in iterator:
                    c += 1
                    yield i
                    if c >= 20:
                        break
            return "%s(%r)" % (self.__class__.__name__,
                               list(start_of(self)))
        return "%s(%r)" % (self.__class__.__name__, list(self))

def _parse_ipv4_ranges(a):
    ipv4_part = _chunk_ipv4(a)
    octet_ranges = []
    for octet in ipv4_part:
        octet_range = []
        ranges = [r for r in octet.split(',') if r]
        for r in ranges:
            if ' ' in r:
                raise ValueError()
            if r == 'x':
                octet_range.append((0, 255))
            elif '-' in r:
                (r_min, r_max) = r.split('-')
                if r_min == '' or r_max == '': raise ValueError()
                r_min = int(r_min, 10)
                r_max = int(r_max, 10)
                if (r_min < 0 or r_min > 255 or r_max < 0 or r_max > 255
                        or r_min > r_max):
                    raise ValueError()
                octet_range.append((r_min, r_max))
            else:
                r = int(r, 10)
                if (r < 0 or r > 255):
                    raise ValueError()
                octet_range.append((r, r))
        octet_ranges.append(octet_range)
    def check(x):
        x = x.to_ipv4()
        if x is None:
            return False
        for (octet, octet_range) in zip(x.octets(), octet_ranges):
            matched = False
            for (r_min, r_max) in octet_range:
                if octet >= r_min and octet <= r_max:
                    matched = True
                    break
            if matched == False:
                return False
        return True
    def gen():
        # inelegant, but all "elegant" solutions are worse
        for (min0, max0) in octet_ranges[0]:
          for o0 in xrange(min0, max0+1):
            a0 = o0 << 8
            for (min1, max1) in octet_ranges[1]:
              for o1 in xrange(min1, max1+1):
                a1= (a0 | o1) << 8
                for (min2, max2) in octet_ranges[2]:
                  for o2 in xrange(min2, max2+1):
                    a2 = (a1 | o2) << 8
                    for (min3, max3) in octet_ranges[3]:
                      for o3 in xrange(min3, max3+1):
                        a = a2 | o3
                        yield IPv4Addr(a)
    return check, gen, False

def _parse_ipv6_ranges(a):
    # already know addr is a string
    # raising a ValueError will produce the proper exc in _parse_wildcard
    ipv6_part, ipv4_part = _chunk_ipv6(a)
    field_ranges = []
    for field in ipv6_part:
        field_range = []
        ranges = [r for r in field.split(',') if r]
        for r in ranges:
            if ' ' in r:
                raise ValueError()
            if r == 'x':
                field_range.append((0, 0xFFFF))
            elif '-' in r:
                (r_min, r_max) = r.split('-')
                if r_min == '': r_min = '0'
                if r_max == '': r_max = 'ffff'
                r_min = int(r_min, 16)
                r_max = int(r_max, 16)
                if (r_min < 0 or r_min > 0xFFFF or r_max < 0 or r_max > 0xFFFF
                        or r_min > r_max):
                    raise ValueError()
                field_range.append((r_min, r_max))
            else:
                r = int(r, 16)
                if (r < 0 or r > 0xFFFF):
                    raise ValueError()
                field_range.append((r, r))
        field_ranges.append(field_range)
    if ipv4_part:
        octet_ranges = []
        for octet in ipv4_part:
            octet_range = []
            ranges = [r for r in octet.split(',') if r]
            for r in ranges:
                if ' ' in r:
                    raise ValueError()
                if r == 'x':
                    octet_range.append((0, 255))
                elif '-' in r:
                    (r_min, r_max) = r.split('-')
                    if r_min == '': r_min = '0'
                    if r_max == '': r_max = '255'
                    r_min = int(r_min, 10)
                    r_max = int(r_max, 10)
                    if (r_min < 0 or r_min > 255 or r_max < 0 or r_max > 255
                            or r_min > r_max):
                        raise ValueError()
                    octet_range.append((r_min, r_max))
                else:
                    r = int(r, 10)
                    if (r < 0 or r > 255):
                        raise ValueError()
                    octet_range.append((r, r))
            octet_ranges.append(octet_range)
    def check(x):
        x = x.to_ipv6()
        x = int(x)
        fields = tuple((x >> (16*(7-i))) & 0xFFFF for i in xrange(8))
        octets = tuple((x >> (8*(3-i))) & 0xFF for i in xrange(4))
        if ipv4_part:
            num_fields = 6
        else:
            num_fields = 8
        for (field, field_range) in zip(fields, field_ranges)[:num_fields]:
            matched = False
            for (r_min, r_max) in field_range:
                if field >= r_min and field <= r_max:
                    matched = True
                    break
            if matched == False:
                return False
        if ipv4_part:
            for (octet, octet_range) in zip(octets, octet_ranges):
                matched = False
                for (r_min, r_max) in octet_range:
                    if octet >= r_min and octet <= r_max:
                        matched = True
                        break
                if matched == False:
                    return False
        return True
    def gen():
        # inelegant, but all "elegant" solutions are worse
        for (min0, max0) in field_ranges[0]:
         for p0 in xrange(min0, max0+1):
          a0 = p0
          for (min1, max1) in field_ranges[1]:
           for p1 in xrange(min1, max1+1):
            a1 = (a0 << 16) | p1
            for (min2, max2) in field_ranges[2]:
             for p2 in xrange(min2, max2+1):
              a2 = (a1 << 16) | p2
              for (min3, max3) in field_ranges[3]:
               for p3 in xrange(min3, max3+1):
                a3 = (a2 << 16) | p3
                for (min4, max4) in field_ranges[4]:
                 for p4 in xrange(min4, max4+1):
                  a4 = (a3 << 16) | p4
                  for (min5, max5) in field_ranges[5]:
                   for p5 in xrange(min5, max5+1):
                    a5 = (a4 << 16) | p5
                    if ipv4_part:
                     for (mino0, maxo0) in octet_ranges[0]:
                      for po0 in xrange(mino0, maxo0+1):
                       ao0 = (a5 << 8) | po0
                       for (mino1, maxo1) in octet_ranges[1]:
                        for po1 in xrange(mino1, maxo1+1):
                         ao1 = (ao0 << 8) | po1
                         for (mino2, maxo2) in octet_ranges[2]:
                          for po2 in xrange(mino2, maxo2+1):
                           ao2 = (ao1 << 8) | po2
                           for (mino3, maxo3) in octet_ranges[3]:
                            for po3 in xrange(mino3, maxo3+1):
                             a = (ao2 << 8) | po3
                             yield IPv6Addr(a)
                    else:
                     for (min6, max6) in field_ranges[6]:
                      for p6 in xrange(min6, max6+1):
                       a6 = (a5 << 16) | p6
                       for (min7, max7) in field_ranges[7]:
                        for p7 in xrange(min7, max7+1):
                         a = (a6 << 16) | p7
                         yield IPv6Addr(a)
    return check, gen, True

def _parse_wildcard(addr):
    a = addr
    # all wildcards are strings
    if not isinstance(a, basestring):
        type_error = TypeError(
            "IPWildcard value must be a string: %r" % addr)
        raise type_error
    a = a.strip()
    try:
        # all non-range addrs contain no '-' or ',' or 'x'
        if '-' not in a and ',' not in a and 'x' not in a:
            # CIDR masks have a '/'
            if '/' in a:
                (a, cidr_len) = a.split('/')
                a = IPAddr(a)
                cidr_len = int(cidr_len)
                a = a.mask_prefix(cidr_len)
                ai = int(a)
                if a.is_ipv6():
                    def check(x):
                        x = x.to_ipv6()
                        return a == x.mask_prefix(cidr_len)
                    def gen():
                        for i in xrange(ai, (ai | (IPv6_MAX >> cidr_len)) + 1):
                            yield IPv6Addr(i)
                    return check, gen, True
                else:
                    def check(x):
                        x = x.to_ipv4()
                        if x is None:
                            return False
                        return a == x.mask_prefix(cidr_len)
                    def gen():
                        for i in xrange(ai, (ai | (IPv4_MAX >> cidr_len)) + 1):
                            yield IPv4Addr(i)
                    return check, gen, False
            else:
                a = IPAddr(a)
                def check(x):
                    return a == x
                def gen():
                    yield a
                return check, gen, a.is_ipv6()
        # ',' or '-', or 'x'  mean it has ranges
        else:
            if ':' in a:
                # IPv6 by parts
                return _parse_ipv6_ranges(a)
            elif '.' in a:
                # IPv4 by parts
                return _parse_ipv4_ranges(a)
            else:
                # IPv4 by integers
                ranges = []
                a_ranges = a.split(',')
                for a_range in a_ranges:
                    if '-' in a_range:
                        (a_min, a_max) = a_range.split('-')
                        a_min = int(IPv4Addr(a_min))
                        a_max = int(IPv4Addr(a_max))
                        ranges.append((a_min, a_max))
                    else:
                        a_range = int(IPv4Addr(a_range))
                        ranges.append((a_range, a_range))
                def check(x):
                    if x.is_ipv6():
                        return False
                    for (a_min, a_max) in ranges:
                        ix = int(x)
                        if ix >= a_min and ix <= a_max:
                            return True
                    return False
                def gen():
                    for (a_min, a_max) in ranges:
                        for a in xrange(a_min, a_max + 1):
                            yield IPv4Addr(a)
                return check, gen, False
    except ValueError:
        value_error = ValueError("IPWildcard is not valid: %r" % addr)
        raise value_error

class IPWildcard(object):
    __slots__ = ['_check', '_gen', '_str', '_is_ipv6']
    def __init__(self, wildcard):
        if isinstance(wildcard, IPWildcard):
            self._check = wildcard._check
            self._gen = wildcard._gen
            self._str = wildcard._str
            self._is_ipv6 = wildcard._is_ipv6
        else:
            self._str = wildcard
            self._check, self._gen, self._is_ipv6 = _parse_wildcard(wildcard)
    def __iter__(self):
        return self._gen()
    def __contains__(self, addr):
        addr = IPAddr(addr)
        return self._check(addr)
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._str)
    def __str__(self):
        return self._str
    def is_ipv6(self):
        return self._is_ipv6

_BITS_FIN = 0x01
_BITS_SYN = 0x02
_BITS_RST = 0x04
_BITS_PSH = 0x08
_BITS_ACK = 0x10
_BITS_URG = 0x20
_BITS_ECE = 0x40
_BITS_CWR = 0x80

_flag_values = {'F': _BITS_FIN, 'f': _BITS_FIN,
                'S': _BITS_SYN, 's': _BITS_SYN,
                'R': _BITS_RST, 'r': _BITS_RST,
                'P': _BITS_PSH, 'p': _BITS_PSH,
                'A': _BITS_ACK, 'a': _BITS_ACK,
                'U': _BITS_URG, 'u': _BITS_URG,
                'E': _BITS_ECE, 'e': _BITS_ECE,
                'C': _BITS_CWR, 'c': _BITS_CWR }

def _parse_tcpflags(value):
    computed_value = 0
    for c in value:
        if c in (' ', '\t', '\n', '\r'):
            continue
        if c not in _flag_values:
            value_error = ValueError(
                "Illegal TCP flag value: %r" % value)
            raise value_error
        computed_value |= _flag_values[c]
    return computed_value

class TCPFlags(object):
    __slots__ = '_value'
    def __init__(self, value):
        if isinstance(value, basestring):
            self._value = _parse_tcpflags(value)
        elif isinstance(value, (int, long)):
            if value < 0 or value > 0xFF:
                overflow_error = OverflowError(
                    "Illegal TCP flag value: %r" % value)
                raise overflow_error
            self._value = value
        elif isinstance(value, TCPFlags):
            self._value = value._value
        else:
            type_error = TypeError(
                "TCP flag value must be string, int, or TCPFlags: %r" % value)
            raise type_error
    def _stringify(self, padding):
        result = ""
        if self._value & _BITS_FIN:
            result += 'F'
        else:
            result += padding
        if self._value & _BITS_SYN:
            result += 'S'
        else:
            result += padding
        if self._value & _BITS_RST:
            result += 'R'
        else:
            result += padding
        if self._value & _BITS_PSH:
            result += 'P'
        else:
            result += padding
        if self._value & _BITS_ACK:
            result += 'A'
        else:
            result += padding
        if self._value & _BITS_URG:
            result += 'U'
        else:
            result += padding
        if self._value & _BITS_ECE:
            result += 'E'
        else:
            result += padding
        if self._value & _BITS_CWR:
            result += 'C'
        else:
            result += padding
        return result
    def __str__(self):
        return self._stringify('')
    def padded(self):
        return self._stringify(' ')
    def __repr__(self):
        return "TCPFlags(%r)" % self.padded()
    def __cmp__(self, other):
        if not isinstance(other, TCPFlags):
            return NotImplemented
        return cmp(self._value, other._value)
    @property
    def fin(self):
        return bool(self._value & 0x01)
    @property
    def syn(self):
        return bool(self._value & 0x02)
    @property
    def rst(self):
        return bool(self._value & 0x04)
    @property
    def psh(self):
        return bool(self._value & 0x08)
    @property
    def ack(self):
        return bool(self._value & 0x10)
    @property
    def urg(self):
        return bool(self._value & 0x20)
    @property
    def ece(self):
        return bool(self._value & 0x40)
    @property
    def cwr(self):
        return bool(self._value & 0x80)
    def __and__(self, other):
        if not isinstance(other, TCPFlags):
            return NotImplemented
        return self.__class__(self._value & other._value)
    def __or__(self, other):
        if not isinstance(other, TCPFlags):
            return NotImplemented
        return self.__class__(self._value | other._value)
    def __xor__(self, other):
        if not isinstance(other, TCPFlags):
            return NotImplemented
        return self.__class__(self._value ^ other._value)
    def __invert__(self):
        return self.__class__((~self._value) & 0xFF)
    def __int__(self):
        return self._value
    def __nonzero__(self):
        return bool(self._value)
    def matches(self, flagmask):
        if not isinstance(flagmask, basestring):
            type_error = TypeError(
                "flag mask not a string in TCPFlags.matches: %r" % flagmask)
            raise type_error
        parts = flagmask.split('/', 3)
        if len(parts) == 1:
            flag_bits = _parse_tcpflags(parts[0])
            mask_bits = flag_bits
        elif len(parts) == 2:
            flag_bits = _parse_tcpflags(parts[0])
            mask_bits = _parse_tcpflags(parts[1])
        else:
            value_error = ValueError(
                "invalid flag mask in TCPFlags.matches: %r" % flagmask)
            raise value_error
        return ((self._value & mask_bits) == flag_bits)

TCP_FIN = TCPFlags('F')
TCP_SYN = TCPFlags('S')
TCP_RST = TCPFlags('R')
TCP_PSH = TCPFlags('P')
TCP_ACK = TCPFlags('A')
TCP_URG = TCPFlags('U')
TCP_ECE = TCPFlags('E')
TCP_CWR = TCPFlags('C')

__all__ = """
    has_IPv6Addr
    IPAddr IPv4Addr IPv6Addr
    ip_set
    IPWildcard
    TCPFlags

    TCP_FIN TCP_SYN TCP_RST TCP_PSH TCP_ACK TCP_URG TCP_ECE TCP_CWR
""".split()
