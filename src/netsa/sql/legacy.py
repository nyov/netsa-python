# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

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
