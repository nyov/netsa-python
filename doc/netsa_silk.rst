=================================================
:mod:`netsa_silk` --- NetSA Python/PySiLK Support
=================================================

.. module:: netsa_silk

The :mod:`netsa_silk` module contains a shared API for working with
common Internet data in both `netsa-python`_ and `PySiLK`_.  If
netsa-python is installed but PySiLK is not, the less efficient but
more portable pure-Python version of this functionality that is
included in netsa-python is used.  If PySiLK is installed, then the
high-performance C version of this functionality that is included in
PySiLK is used.

.. _netsa-python: http://tools.netsa.cert.org/netsa-python/index.html
.. _PySiLK: http://tools.netsa.cert.org/silk/pysilk-ref.html

IPv6 Support
============

Depending on which version of the :mod:`netsa_silk` functionality is
in use, IPv6 support may not be present or may be limited.  The
following functions allow determining what variety of IPv6 support is
available.

.. function:: has_IPv6Addr() -> bool

   Returns ``True`` if the most basic form of IPv6 support---support
   for IPv6 addresses---is available.  If it is not available, then
   this function returns ``False``, :class:`IPAddr` will raise
   :exc:`ValueError <exceptions.ValueError>` when given an IPv6
   address, and any call to :class:`IPv6Addr` will raise
   :exc:`NotImplementedError <exceptions.NotImplementedError>`.

See also :meth:`ip_set.supports_ipv6()`.

IP Addresses
============

An IP address is represented by either an :class:`IPv4Addr` or an
:class:`IPv6Addr`.  Both of these are subclasses of the generic
:class:`IPAddr` class.

.. class:: IPAddr(address : str or IPAddr) -> IPv4Addr or IPv6Addr

  Converts the input into an IP address, either IPv4 or IPv6.  Returns
  either an :class:`IPv4Addr` or :class:`IPv6Addr` object, depending
  on whether the given input is parsed as an IPv4 or an IPv6 address.

  If IPv6 address support is not available (:func:`has_IPv6Addr`
  returns ``False``), then attempting to parse an IPv6 address will
  raise :exc:`ValueError <exceptions.ValueError>`.

  Examples::

      >>> addr1 = IPAddr('192.160.1.1')
      >>> addr2 = IPAddr('2001:db8::1428:57ab')
      >>> addr3 = IPAddr('::ffff:12.34.56.78')
      >>> addr4 = IPAddr(addr1)
      >>> addr5 = IPAddr(addr2)

.. class:: IPv4Addr(address : int or str or IPAddr)

   Converts the input into a new IPv4 address.  If the integer input
   is too large a value, if the string input is unparseable as an IPv4
   address, or if the :class:`IPAddr` input is not convertible to an
   IPv4 address, raises a :exc:`ValueError <exceptions.ValueError>`.

   :class:`IPv4Addr` is a subclass of :class:`IPAddr`.

   Examples::

       >>> addr1 = IPv4Addr('192.160.1.1')
       >>> addr2 = IPv4Addr(IPAddr('::ffff.12.34.56.78'))
       >>> addr3 = IPv4Addr(addr1)
       >>> addr4 = IPv4Addr(0x10000000)

.. class:: IPv6Addr(address : int or str or IPAddr)

   Converts the input into a new IPv6 address.  If the integer input
   is too large a value, or if the string input is unparseable as an
   IPv6 address, raises a :exc:`ValueError <exceptions.ValueError>`.
   If the input is an :class:`IPv4Addr`, the address is converted to
   IPv6 via IPv4-mapped address embedding.  ("1.2.3.4" becomes
   "::ffff:1.2.3.4").

   If IPv6 address support is not available (:func:`has_IPv6Addr`
   returns ``False``), then calling :class:`IPv6Addr` will raise
   :exc:`NotImplementedError <exceptions.NotImplementedError>`.

   :class:`IPv6Addr` is a subclass of :class:`IPAddr`.

   Examples::

       >>> addr1 = IPv6Addr('2001:db8::1428:57ab')
       >>> addr2 = IPv6Addr(IPAddr('192.168.1.1'))
       >>> addr3 = IPv6Addr(addr1)
       >>> addr4 = IPv6Addr(0x100000000000000000000000)

.. index::
   single: == (netsa_silk.IPAddr operator)
   single: != (netsa_silk.IPAddr operator)
   single: < (netsa_silk.IPAddr operator)
   single: <= (netsa_silk.IPAddr operator)
   single: >= (netsa_silk.IPAddr operator)
   single: > (netsa_silk.IPAddr operator)

Comparisons
-----------

Whenever an IPv4 address is compared to an IPv6 address, the IPv4
address is converted to IPv6 using IPv4-mapped address embedding.
This means that ``IPAddr('0.0.0.0')`` equals
``IPAddr('::ffff:0.0.0.0')``.  You can distinguish IPv4 addresses from
IPv6 address by using the |is_ipv6|_ method.

.. |is_ipv6| replace:: ``is_ipv6()``

.. list-table::
   :header-rows: 1
   :widths: 1, 100

   * - Operation
     - Result
   * - :samp:`{a} == {b}`
     - if *a* is equal to *b*, then ``True``, else ``False``
   * - :samp:`{a} != {b}`
     - if *a* is equal to *b*, then ``False``, else ``True``
   * - :samp:`{a} < {b}`
     - if *a*'s integer representation is less than *b*'s, then
       ``True``, else ``False``
   * - :samp:`{a} <= {b}`
     - if *a*'s integer representation is less than or equal to *b*'s,
       then ``True``, else ``False``
   * - :samp:`{a} >= {b}`
     - if *a*'s integer representation is greater than or equal to
       *b*'s, then ``True``, else ``False``
   * - :samp:`{a} > {b}`
     - if *a*'s integer representation is greater than *b*'s, then
       ``True``, else ``False``

.. index::
   single: is_ipv6() (netsa_silk.IPAddr method)
   single: to_ipv4() (netsa_silk.IPAddr method)
   single: to_ipv6() (netsa_silk.IPAddr method)
   single: int() (netsa_silk.IPAddr operator)
   single: str() (netsa_silk.IPAddr operator)
   single: padded() (netsa_silk.IPAddr method)
   single: octets() (netsa_silk.IPAddr method)

.. _is_ipv6:
.. _octets:

Conversions
-----------

The following operations and methods may be used to convert between
IPv4 and IPv6 addresses and between IP addresses and other types.

.. list-table::
   :header-rows: 1
   :widths: 1, 100, 1

   * - Operation
     - Result
     - Notes
   * - :samp:`{addr}.is_ipv6()`
     - if *addr* is an IPv6 address, then ``True``, else ``False``
     -
   * - :samp:`{addr}.to_ipv4()`
     - the IPv4 equivalent of *addr*, or ``None`` if no such
       equivalent exists
     - \(1)
   * - :samp:`{addr}.to_ipv6()`
     - the IPv6 equivalent of *addr*
     - \(2)
   * - :samp:`int({addr})`
     - the integer representation of *addr*
     - \(3)
   * - :samp:`str({addr})`
     - the human-readable string representation of *addr*
     - \(4)
   * - :samp:`{addr}.padded()`
     - a zero-padded human-readable string representation of *addr*
     - \(5)
   * - :samp:`{addr}.octets()`
     - a tuple containing each octet of *addr* in network byte order
       as an unsigned integer
     -

Notes:

(1)
   If the address is already an IPv4 address, does nothing.  If the
   address is an IPv6 address using IPv4-mapped address embedding
   (e.g. "::ffff:1.2.3.4"), returns the equivalent IPv4 address.
   Otherwise, returns ``None``.

(2)
   If the address is already an IPv6 address, does nothing.  If the
   address is an IPv4 address, returns the address converted to an
   IPv6 address using IPv4-mapped address embedding.

(3)
   If the address is an IPv4 address, returns an unsigned 32-bit
   integer value.  If the address is an IPv6 address, returns an
   unsigned 128-bit integer value.

(4)
   The address is returned in its canonical form.

(5)
   If the address is an IPv4 address, returns a string of the form
   "xxx.xxx.xxx.xxx", where each field is one octet of the address as
   a zero-padded base-10 integer.  If the address is an IPv6 address,
   returns a string of the form
   "xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx", where each field is two
   octets of the address as a zero-padded base-16 integer.

.. index::
   single: mask() (netsa_silk.IPAddr method)
   single: mask_prefix() (netsa_silk.IPAddr method)

Masking
-------

Masking operations return a copy of the address with all non-masked
bits set to zero.

.. list-table::
   :header-rows: 1
   :widths: 1, 100, 1

   * - Operation
     - Result
     - Notes
   * - :samp:`{addr}.mask({mask})`
     - the address *addr* masked by the bits of the address *mask*
     - \(1)
   * - :samp:`{addr}.mask_prefix({len})`
     - the address *addr* masked to a length of *len* prefix bits
     -

Notes:

(1)
   If *addr* is an IPv6 address but *mask* is an IPv4 address, *mask*
   is converted to IPv6 and then the mask is applied.  If *addr* was
   not an IPv4-mapped embedded IPv6 address, the result may not be
   what was expected.  Prefer :samp:`addr.mask_prefix({len})` for IPv6
   addresses when possible.

IP Sets
=======

While there are multiple different IP set implementations with
different qualities, :mod:`netsa_silk` provides a standard API for
these sets, and a standard mechanism for acquiring a value of some set
when you don't need a specific implementation.

.. class:: ip_set([iterable])

   Returns a new IP set object from an unspecified implementation that
   matches the following API.  The elements of the set must be IP
   addresses.  The values in *iterable* may be :class:`IPAddr`
   objects, strings parsable by :class:`IPAddr`, :class:`IPWildcard`
   objects, or strings parsable by :class:`IPWildcard`.

   In all of the following descriptions, *s*, *s1*, and *s2* must be
   :class:`ip_set` obejcts, *addr* may be an :class:`IPAddr` object or
   a string that is parsable as an :class:`IPAddr`.  *iterable* may be
   any iterable containing :class:`IPAddr` objects,
   :class:`IPWildcard` objects, and strings, as described above.

.. index::
   single: cardinality() (netsa_silk.ip_set method)
   single: len() (netsa_silk.ip_set operator)

Cardinality
-----------

Since IP sets can grow very large, an additional method for querying
the cardinality which supports large values is available.

.. list-table::
   :header-rows: 1
   :widths: 1, 100, 1

   * - Operation
     - Result
     - Notes
   * - :samp:`{s}.cardinality()`
     - the cardinality of *s*
     -
   * - :samp:`len({s})`
     - the cardinality of *s*
     - \(1)

Notes:

(1)
   If the cardinality of *s* is exceptionally large, this may raise
   :exc:`OverflowError <exceptions.OverflowError>` due to limitations
   in Python.  Using :samp:`{s}.cardinality()` is highly preferred for
   IP sets.

.. index::
   single: in (netsa_silk.ip_set operator)
   single: not in (netsa_silk.ip_set operator)

Membership
----------

.. list-table::
   :header-rows: 1
   :widths: 1, 100

   * - Operation
     - Result
   * - :samp:`{addr} in {s}`
     - if *addr* is a member of *s*, then``True``, else ``False``
   * - :samp:`{addr} not in {s}`
     - if *addr* is a member of *s*, then ``False``, else ``True``

.. index::
   single: == (netsa_silk.ip_set operator)
   single: != (netsa_silk.ip_set operator)
   single: isdisjoint() (netsa_silk.ip_set method)
   single: issubset() (netsa_silk.ip_set method)
   single: <= (netsa_silk.ip_set operator)
   single: < (netsa_silk.ip_set operator)
   single: issuperset() (netsa_silk.ip_set method)
   single: >= (netsa_silk.ip_set operator)
   single: > (netsa_silk.ip_set operator)

Comparison
----------

.. list-table::
   :header-rows: 1
   :widths: 1, 100

   * - Operation
     - Result
   * - :samp:`{s1} == {s2}`
     - if *s* has exactly the same elements as *s2*, then ``True``,
       else ``False``
   * - :samp:`{s1} != {s2}`
     - if *s1* does not have exactly the same elements as *s2*, then
       ``True``, else ``False``
   * - :samp:`{s}.isdisjoint({iterable})`
     - if *s* has no elements in common with *iterable*, then
       ``True``, else ``False``
   * - :samp:`{s}.issubset({iterable})`
     - if every element of *s* is also in *iterable*, then ``True``,
       else ``False``
   * - :samp:`{s1} <= {s2}`
     - if every element of *s1* is also in *s2*, then ``True``, else
       ``False``
   * - :samp:`{s1} < {s2}`
     - if :samp:`{s1} < {s2}` and :samp:`{s1} != {s2}`, then ``True``,
       else ``False``
   * - :samp:`{s}.issuperset({iterable})`
     - if every element of *iterable* is also in *s*, then ``True``,
       else ``False``
   * - :samp:`{s1} >= {s2}`
     - if every element of *s2* is also in *s1*, then ``True``, else
       ``False``
   * - :samp:`{s1} > {s2}`
     - if :samp:`{s1} > {s2}` and :samp:`{s1} != {s2}`, then ``True``,
       else ``False``

.. index::
   single: union() (netsa_silk.ip_set method)
   single: | (netsa_silk.ip_set operator)
   single: intersection() (netsa_silk.ip_set method)
   single: & (netsa_silk.ip_set operator)
   single: difference() (netsa_silk.ip_set method)
   single: - (netsa_silk.ip_set operator)
   single: symmetric_difference() (netsa_silk.ip_set method)
   single: ^ (netsa_silk.ip_set operator)
   single: copy() (netsa_silk.ip_set method)


Manipulation
------------

The following operations return a new IP set with the desired changes,
while leaving the original IP set unmodified.

.. list-table::
   :header-rows: 1
   :widths: 1, 100

   * - Operation
     - Result
   * - :samp:`{s}.union({iterable, ...})`
     - a set with all elements that are in *s* or any *iterable*
   * - :samp:`{s1} | {s2}`
     - a set with all elements that are in *s1* or *s2*
   * - :samp:`{s}.intersection({iterable, ...})`
     - a set with only elements that are in *s* and every *iterable*
   * - :samp:`{s1} & {s2}`
     - a set with only elements that are in both *s1* and *s2*
   * - :samp:`{s}.difference({iterable, ...})`
     - a set with all elements that are in *s* but in no *iterable*
   * - :samp:`{s1} - {s2}`
     - a set with all elements that are in *s1* but not in *s2*
   * - :samp:`{s}.symmetric_difference({iterable})`
     - a set with all elements that are in *s* or *iterable* but not
       both
   * - :samp:`{s1} ^ {s2}`
     - a set with all elements that are in *s1* or *s2* but not both
   * - :samp:`{s}.copy()`
     - a shallow copy of *s*

.. index::
   single: update() (netsa_silk.ip_set method)
   single: |= (netsa_silk.ip_set operator)
   single: intersection_update() (netsa_silk.ip_set method)
   single: &= (netsa_silk.ip_set operator)
   single: difference_update() (netsa_silk.ip_set method)
   single: -= (netsa_silk.ip_set operator)
   single: symmetric_difference_update() (netsa_silk.ip_set method)
   single: ^= (netsa_silk.ip_set operator)
   single: add() (netsa_silk.ip_set method)
   single: remove() (netsa_silk.ip_set method)
   single: discard() (netsa_silk.ip_set method)
   single: pop() (netsa_silk.ip_set method)
   single: clear() (netsa_silk.ip_set method)

Modification
------------

The following operations modify the target IP set in place.

.. list-table::
   :header-rows: 1
   :widths: 1, 100, 1

   * - Operation
     - Result
     - Notes
   * - :samp:`{s}.update({iterable, ...})`
     - updates *s* by adding all elements from each *iterable*
     -
   * - :samp:`{s1} |= {s2}`
     - updates *s1* by adding all elements from *s2*
     -
   * - :samp:`{s}.intersection_update({iterable, ...})`
     - updates *s* by removing all elements that do not appear in
       every *iterable*
     -
   * - :samp:`{s1} &= {s2}`
     - updates *s1* by removing all elements that do not appear in
       *s2*
     -
   * - :samp:`{s}.difference_update({iterable, ...})`
     - updates *s* by removing all elements that appear in any
       *iterable*
     -
   * - :samp:`{s1} -= {s2}`
     - updates *s1* by removing all elements that appear in *s2*
     -
   * - :samp:`{s}.symmetric_difference_update({iterable})`
     - updates *s*, keeping only elements found in *s* or *iterable*
       but not both
     -
   * - :samp:`{s1} ^= {s2}`
     - updates *s1*, keeping only elements found in *s1* or *s2* but
       not both
     -
   * - :samp:`{s}.add({addr})`
     - adds *addr* to *s*
     -
   * - :samp:`{s}.remove({addr})`
     - removes *addr* from *s*
     - \(1)
   * - :samp:`{s}.discard({addr})`
     - removes *addr* from *s*
     -
   * - :samp:`{s}.pop()`
     - removes and returns an arbitrary element from *s*
     - \(2)
   * - :samp:`{s}.clear()`
     - removes all elements from *s*
     -

Notes:

(1)
   Raises :exc:`KeyError <exceptions.KeyError>` if *addr* is not in
   *s*.

(2)
   Raises :exc:`KeyError <exceptions.KeyError>` if *s* was empty.

CIDR Block Iteration
--------------------

.. method:: ip_set.cidr_iter() -> (IPAddr, int) iter

  Returns an iterator over the CIDR blocks covered by this IP set.
  Each value in the iterator is a pair :samp:`({addr}, {prefix_len})`
  where *addr* is the first IP address in the block, and *prefix_len*
  is the prefix length of the block.

IPv6 Support
------------

Some :class:`ip_set` implementations do not provide IPv6 support.
Such an implementation will raise an :exc:`exception.TypeError` on any
attempt to add an :class:`IPv6Addr` to the set.  The following class
method can be used to determine if a given implementation has IPv6
support:

.. classmethod:: ip_set.supports_ipv6() -> bool

  Returns ``True`` if this IP set implementation provides support for
  IPv6 addresses, or ``False`` otherwise.

IP Wildcards
============

An :class:`IPWildcard` object represents the specification of a set of
IP addresses using SiLK IP wildcard syntax.  Not all sets of IP
addresses can be represented by a single IP wildcard.

.. class:: IPWildcard(wildcard : str or IPWildcard)

  Returns a new :class:`IPWildcard` object constructed from
  *wildcard*.  The string *wildcard* may contain an IP address, an IP
  address with a CIDR prefix designation, an integer, an integer with
  a CIDR prefix designation, or a SiLK wildcard expression.  In SiLK
  wildcard notation, a wildcard is represented as an IP address in
  canonical form with each octet (for IPv4 addresses) or octet pair
  (IPv6) holding a single value, a range of values, a comma-separated
  list of values and ranges, or the character 'x' to accept all
  values.

  Examples::

      >>> wild1 = IPWildcard('1.2.3.0/24')
      >>> wild2 = IPWildcard('ff80::/16')
      >>> wild3 = IPWildcard('1.2.3.4')
      >>> wild4 = IPWildcard('::FFFF:0102:0304')
      >>> wild5 = IPWildcard('16909056')
      >>> wild6 = IPWildcard('16909056/24')
      >>> wild7 = IPWildcard('1.2.3.x')
      >>> wild8 = IPWildcard('1:2:3:4:5:6:7:x')
      >>> wild9 = IPWildcard('1.2,3.4,5.6,7')
      >>> wild10 = IPWildcard('1.2.3.0-255')
      >>> wild11 = IPWildcard('::2-4')
      >>> wild12 = IPWildcard('1-2:3-4:5-6:7-8:9-a:b-c:d-e:0-ffff')

.. index::
   single: in (netsa_silk.IPWildcard operator)
   single: not in (netsa_silk.IPWildcard operator)

Membership
----------

The primary operation on :class:`IPWildcard` objects is testing
whether an address is contained in the set covered by the wildcard.
Both :class:`IPAddr` and :class:`str` values may be tested for
membership.

.. list-table::
   :header-rows: 1
   :widths: 1, 100, 1

   * - Operation
     - Results
     - Notes
   * - :samp:`{addr} in {wildcard}`
     - *addr* matches *wildcard*, then ``True``, else ``False``
     - \(1)
   * - :samp:`{addr} not in {wildcard}`
     - *addr* matches *wildcard*, then ``False``, else ``True``
     -  \(1)

Notes:

(1)
   *addr* may be an :class:`IPAddr` or a string.  Strings are
   automatically converted as with :samp:`IPAddr({addr})`

.. index::
   single: str() (netsa_silk.IPWildcard operator)
   single: is_ipv6() (netsa_silk.IPWildcard method)

Other
-----

The following additional operations are available on
:class:`IPWildcard` objects:

.. list-table::
   :header-rows: 1
   :widths: 1, 100

   * - Operation
     - Result
   * - :samp:`str({wildcard})`
     - the string that was used to construct *wildcard*
   * - :samp:`{wildcard}.is_ipv6()`
     - if *wildcard* contains IPv6 addresses then ``True``, else
       ``False``

TCP Flags
=========

A :class:`TCPFlags` object represents the eight bits of flags from a
TCP session.

.. class:: TCPFlags(value : int or str or TCPFlags)

  Returns a new :class:`TCPFlags` object with the given flags set.  If
  *value* is an integer, it is interpreted as the bitwise integer
  representation of the flags.  If *value* is a string, it is
  interpreted as a case-insensitive sequence of letters indicating
  individual flags, and optional white space.  The mapping is
  described below.

.. index::
   single: fin (netsa_silk.TCPFlags attribute)
   single: syn (netsa_silk.TCPFlags attribute)
   single: rst (netsa_silk.TCPFlags attribute)
   single: psh (netsa_silk.TCPFlags attribute)
   single: ack (netsa_silk.TCPFlags attribute)
   single: urg (netsa_silk.TCPFlags attribute)
   single: ece (netsa_silk.TCPFlags attribute)
   single: cwr (netsa_silk.TCPFlags attribute)
   single: TCP_FIN (netsa_silk constant)
   single: TCP_SYN (netsa_silk constant)
   single: TCP_RST (netsa_silk constant)
   single: TCP_PSH (netsa_silk constant)
   single: TCP_ACK (netsa_silk constant)
   single: TCP_URG (netsa_silk constant)
   single: TCP_ECE (netsa_silk constant)
   single: TCP_CWR (netsa_silk constant)

Each supported flag has an assigned letter in string representations,
is available as an attribute on :class:`TCPFlags` values, and is
available as a :class:`TCPFlags` constant in :mod:`netsa_silk`:

.. list-table::
   :header-rows: 1
   :widths: 1, 100, 1, 1, 1

   * - Flag
     - Meaning
     - Letter
     - :class:`TCPFlags` attribute
     - :mod:`netsa_silk` constant
   * - FIN
     - No more data from sender
     - F
     - :samp:`{flags}.fin`
     - :const:`TCP_FIN`
   * - SYN
     - Synchronize sequence numbers
     - S
     - :samp:`{flags}.syn`
     - :const:`TCP_SYN`
   * - RST
     - Reset the connection
     - R
     - :samp:`{flags}.rst`
     - :const:`TCP_RST`
   * - PSH
     - Push Function
     - P
     - :samp:`{flags}.psh`
     - :const:`TCP_PSH`
   * - ACK
     - Acknowledgment field significant
     - A
     - :samp:`{flags}.ack`
     - :const:`TCP_ACK`
   * - URG
     - Urgent Pointer field significant
     - U
     - :samp:`{flags}.urg`
     - :const:`TCP_URG`
   * - ECE
     - ECN-echo (RFC 3168)
     - E
     - :samp:`{flags}.ece`
     - :const:`TCP_ECE`
   * - CWR
     - Congestion window reduced (RFC 3168)
     - C
     - :samp:`{flags}.cwr`
     - :const:`TCP_CWR`

.. index::
   single: ~ (netsa_silk.TCPFlags operator)
   single: & (netsa_silk.TCPFlags operator)
   single: | (netsa_silk.TCPFlags operator)
   single: ^ (netsa_silk.TCPFlags operator)

Bit-Manipulation
----------------

The following bit-manipulation operations are available on
:class:`TCPFlags` objects:

.. list-table::
   :header-rows: 1
   :widths: 1, 100

   * - Operation
     - Result
   * - :samp:`~{flags}`
     - the bitwise inversion (not) of *flags*
   * - :samp:`{flags1} & {flags2}`
     - the bitwise intersection (and) of *flags1* and *flags2*
   * - :samp:`{flags1} | {flags2}`
     - the bitwise union (or) of *flags1* and  *flags2*
   * - :samp:`{flags1} ^ {flags2}`
     - the bitwise exclusive disjunction (xor) of *flags1* and *flags2*

.. index::
   single: int() (netsa_silk.TCPFlags operator)
   single: str() (netsa_silk.TCPFlags operator)
   single: padded() (netsa_silk.TCPFlags method)
   single: bool() (netsa_silk.TCPFlags operator)

Conversions
-----------

The following operations and methods may be used to convert
:class:`TCPFlags` objects into other types.

.. list-table::
   :header-rows: 1
   :widths: 1, 100

   * - Operation
     - Result
   * - :samp:`int({flags})`
     - the integer value of the flags set in *flags*
   * - :samp:`str({flags})`
     - a string representation of the flags set in *flags*
   * - :samp:`{flags}.padded()`
     - a space-padded column aligned string representation of the
       flags set in *flags*
   * - :samp:`bool({flags})`
     - if any flag is set in *flags*, then ``True``, else ``False``

Matching
--------

.. method:: TCPFlags.matches(flagmask : str) -> bool

  The :meth:`TCPFlags.matches` method may be used to determine if a
  :class:`TCPFlags` value matches a given flag/mask specification.
  The specification is given as a string containing a set of flags
  that must be set, optionally followed by a slash and a set of flags
  that must be checked.  (i.e. if "A" is not in the flag list but is
  in the mask, it must be false.  If "U" is not in either, it may have
  any value.)  For example, :samp:`{flags}.matches('S/SA')` would
  return ``True`` if SYN was set and ACK was not set in *flags*.

  Examples::

    >>> flags = TCPFlags('SAU')
    >>> flags.matches('S')
    True
    >>> flags.matches('SA/SA')
    True
    >>> flags.matches('S/SP')
    True
    >>> flags.matches('S/SA')
    False
    >>> flags.matches('SP/SP')
    False
    >>> flags.matches('A/SA')
    False

Support for SiLK versions before 3.0
====================================

Although :mod:`netsa_silk` is only fully supported by SiLK as of
version 3.0, some legacy support for older versions of PySiLK is
available.  Some specific things to watch for if you need to work with
older SiLK versions:

1) In :class:`IPv6Addr` the |octets|_ method is not available.
   Other conversion operations still work, however.

.. |octets| replace:: ``octets``

2) For :class:`TCPFlags`, the lower-case flag name attributes
   (e.g. :samp:`{flags}.syn`) on the object are not available.  To
   work around this, use the :meth:`TCPFlags.matches` method, or
   perform bitwise operations on the constants in the module.  (For
   example, instead of :samp:`if {flags}.fin: {stuff...}`, use
   :samp:`if {flags} & TCP_FIN: {stuff ...}`.)
