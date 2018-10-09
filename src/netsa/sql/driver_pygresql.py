# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import datetime
import pgdb
import netsa.sql
import threading

# Number of rows to fetch per cursor iteration
_CURSOR_SIZE = 4096

class pgs_driver(netsa.sql.db_driver):
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
        return pgs_connection(
            self, ['postgres'],
            database=parsed_uri['path'].lstrip('/'),
            host=parsed_uri['host'],
            port=parsed_uri['port'],
            user=(user or parsed_uri['user'] or params.get('user', None)),
            password=(password or parsed_uri['password'] or
                      params.get('password', None)),
            sslmode=params.get('sslmode', None)
        )

class pgs_connection(netsa.sql.db_connection):
    __slots__ = """
        _database
        _host
        _port
        _user
        _password
        _sslmode
        _pgdb_conn
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
        self._pgdb_conn = None
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
        self._pgdb_conn = pgdb.connect(**kwargs)
        self.execute("set timezone = 0")
    def clone(self):
        return pgs_connection(self._driver, self._variants, self._database,
                              self._host, self._port, self._user,
                              self._password, self._sslmode)
    def execute(self, query_or_sql, **params):
        return pgs_result(self, query_or_sql, params)
    def commit(self):
        self._pgdb_conn.commit()
    def rollback(self):
        if self._pgdb_conn:
            self._pgdb_conn.rollback()
    def _next_cursor_name(self):
        self._cursor_counter_lock.acquire()
        n = self._cursor_counter
        self._cursor_counter += 1
        self._cursor_counter_lock.release()
        return "_netsa_sql_cursor_%d" % n

class pgs_result(netsa.sql.db_result):
    __slots__ = """
        _pgdb_cursor
        _pg_cursor_name
    """.split()
    def __init__(self, connection, query, params):
        netsa.sql.db_result.__init__(self, connection, query, params)
        self._pgdb_cursor = self._connection._pgdb_conn.cursor()
        variants = self._connection.get_variants()
        (query, params) = \
            self._query.get_variant_pyformat_params(variants, params)
        # Work around mx vs. standard datetime issues
        for k in params:
            if isinstance(params[k], datetime.datetime):
                params[k] = str(params[k])
        # Does it look like a query?
        if (query.lstrip()[:6].lower() == 'select' or
                query.lstrip()[:4].lower() == 'with'):
            # Yes, let's use a server-side cursor on it.
            self._pg_cursor_name = self._connection._next_cursor_name()
            query = ("declare %s no scroll cursor for %s" %
                     (self._pg_cursor_name, query))
            self._pgdb_cursor.execute(query, params)
            # If the cursor isn't fetched from, the query will not
            # begin to execute at all, which means side effects won't
            # happen.
            self._pgdb_cursor.execute(
                "fetch forward %d from %s" %
                (_CURSOR_SIZE, self._pg_cursor_name))
        else:
            # No, run the query as-is.
            self._pg_cursor_name = None
            self._pgdb_cursor.execute(query, params)
    def __iter__(self):
        if self._pg_cursor_name == None:
            # Non-cursored query, process it diretly
            while True:
                r = self._pgdb_cursor.fetchone()
                if r == None:
                    return
                yield r
        else:
            # New cursored query, process it in chunks
            try:
                while self._pgdb_cursor.rowcount:
                    for r in self._pgdb_cursor.fetchall():
                        yield r
                    self._pgdb_cursor.execute(
                        "fetch forward %d from %s" %
                        (_CURSOR_SIZE, self._pg_cursor_name))
                # Work around try: finally: not allowed in generators in 2.4
            except:
                self._pgdb_cursor.execute(
                    "close %s" % self._pg_cursor_name)
                raise
            self._pgdb_cursor.execute(
                "close %s" % self._pg_cursor_name)

netsa.sql.register_driver(pgs_driver())
