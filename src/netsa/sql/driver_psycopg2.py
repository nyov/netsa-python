# Copyright 2008-2013 by Carnegie Mellon University

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

import psycopg2
import netsa.sql
import threading

# Number of rows to fetch per cursor iteration
_CURSOR_SIZE = 4096

class ppg_driver(netsa.sql.db_driver):
    __slots__ = """
    """.split()
    def can_handle(self, uri_scheme):
        scheme = "nsql-postgres"
        return (uri_scheme == scheme or uri_scheme.startswith(scheme + "-"))
    def connect(self, uri, user, password):
        parsed_uri = netsa.sql.db_parse_uri(uri)
        if not self.can_handle(parsed_uri['scheme']):
            return None
        params = dict(parsed_uri.get('params', []))
        database = parsed_uri['path'].lstrip('/')
        return ppg_connection(
            self, ['postgres'],
            database=parsed_uri['path'].lstrip('/'),
            host=parsed_uri['host'],
            port=parsed_uri['port'],
            user=(user or parsed_uri['user'] or params.get('user', None)),
            password=(password or parsed_uri['password'] or
                      params.get('password', None)),
            sslmode=params.get('sslmode', None)
        )

class ppg_connection(netsa.sql.db_connection):
    __slots__ = """
        _database
        _host
        _port
        _user
        _password
        _sslmode
        _psycopg2_conn
        _cursor_counter
        _cursor_counter_lock
    """.split()
    def __init__(self, driver, variants, database, host, port, user,
                 password, sslmode):
        netsa.sql.db_connection.__init__(self, driver, variants)
        self._database = database
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._sslmode = sslmode
        self._psycopg2_conn = None
        self._cursor_counter = 0
        self._cursor_counter_lock = threading.Lock()
        self._connect()
    def _connect(self):
        kwargs = {}
        if self._database:
            kwargs['database'] = self._database
        if self._host:
            kwargs['host'] = self._host
        if self._port:
            kwargs['port'] = self._port
        if self._user:
            kwargs['user'] = self._user
        if self._password:
            kwargs['password'] = self._password
        if self._sslmode:
            kwargs['sslmode'] = self._sslmode
        self._psycopg2_conn = psycopg2.connect(**kwargs)
        self.execute("set timezone = 0")
    def clone(self):
        return ppg_connection(self._driver, self._variants, self._database,
                              self._host, self._port, self._user,
                              self._password, self._sslmode)
    def execute(self, query_or_sql, **params):
        return ppg_result(self, query_or_sql, params)
    def commit(self):
        self._psycopg2_conn.commit()
    def rollback(self):
        if self._psycopg2_conn:
            self._psycopg2_conn.rollback()
    def _next_cursor_name(self):
        self._cursor_counter_lock.acquire()
        n = self._cursor_counter
        self._cursor_counter += 1
        self._cursor_counter_lock.release()
        return "_netsa_sql_cursor_%d" % n

class ppg_result(netsa.sql.db_result):
    __slots__ = """
        _psycopg2_cursor
        _pg_cursor_name
    """.split()
    def __init__(self, connection, query, params):
        netsa.sql.db_result.__init__(self, connection, query, params)
        self._psycopg2_cursor = self._connection._psycopg2_conn.cursor()
        variants = self._connection.get_variants()
        (query, params) = \
            self._query.get_variant_pyformat_params(variants, params)
        # Does it look like a query?
        if (query.lstrip()[:6].lower() == 'select' or
                query.lstrip()[:4].lower() == 'with'):
            # Yes, let's use a server-side cursor on it.
            self._pg_cursor_name = self._connection._next_cursor_name()
            query = ("declare %s no scroll cursor for %s" %
                     (self._pg_cursor_name, query))
            self._psycopg2_cursor.execute(query, params)
            # If the cursor isn't fetched from, the query will not
            # begin to execute at all, which means side effects won't
            # happen.
            self._psycopg2_cursor.execute(
                "fetch forward %d from %s" %
                (_CURSOR_SIZE, self._pg_cursor_name))
        else:
            # No, run the query as-is.
            self._pg_cursor_name = None
            self._psycopg2_cursor.execute(query, params)
    def __iter__(self):
        if self._pg_cursor_name == None:
            # Non-cursored query, process it directly
            while True:
                r = self._psycopg2_cursor.fetchone()
                if r == None:
                    return
                yield r
        else:
            # New cursored query, process it in chunks
            try:
                while self._psycopg2_cursor.rowcount:
                    for r in self._psycopg2_cursor.fetchall():
                        yield r
                    self._psycopg2_cursor.execute(
                        "fetch forward %d from %s" %
                        (_CURSOR_SIZE, self._pg_cursor_name))
                # Work around try: finally: not allowed in generators in 2.4
            except:
                self._psycopg2_cursor.execute(
                    "close %s" % self._pg_cursor_name)
                raise
            self._psycopg2_cursor.execute(
                "close %s" % self._pg_cursor_name)

netsa.sql.register_driver(ppg_driver())
