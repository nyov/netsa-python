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

import re

drivers = {}

def register_driver(scheme, connect_fn):
    """
    DEPRECATED

    Internal function: Register a driver for the given URI scheme to
    use the given connect function.  connect_fn will be called with a
    dictionary resulting from netsa.sql.parse_uri
    """
    drivers[scheme] = connect_fn

def get_driver(scheme):
    """
    DEPRECATED

    Internal function: Returns the connection function currently
    registered for the given URI scheme.
    """
    return drivers[scheme]

connect_string_re = re.compile(r"""
    ^
    (?P<scheme> [^:/]+ ) ://
    ( (?P<username> [^:/@]+ ) (?: : (?P<password> [^:/@]+ ) )? @ )?
    (?P<host> [^:/]+ ) (?: : (?P<port> \d+ ) )? /
    (?P<dbname> [^/]+ )
    (?: / (?P<additional> .* ) )?
    $
""", re.VERBOSE)

def parse_uri(connect_string):
    """
    DEPRECATED

    Parses a URI of the following form, and returns a dictionary of
    the resulting key, value pairs::

        <scheme>://[<username>[:<password>]@]<host>[:<port>]
            /<dbname>[/<additional>]

    The meaning of portions of this URI may vary from database to
    database, particularly the <additional> section, which has no
    pre-defined semantics.
    """
    m = connect_string_re.match(connect_string)
    if not m:
        return None
    return dict(m.groupdict())

def connect_uri(connect_string):
    """
    *Deprecated.*

    Opens a database connection to the database identified by the
    provided URI.  See netsa.sql.legacy.parse_uri for details on the
    URI syntax.
    """
    db_info = parse_uri(connect_string)
    return get_driver(db_info['scheme'])(db_info)

try:
    import netsa.sql.legacy_driver_psycopg2
except ImportError:
    pass

__all__ = """
    register_driver
    get_driver
    parse_uri
    connect_uri
""".split()
