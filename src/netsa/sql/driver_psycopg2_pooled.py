# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import psycopg2
import netsa.sql
import threading

# Number of rows to fetch per cursor iteration
_CURSOR_SIZE = 4096

class ppg_driver(netsa.sql.db_driver):
    __slots__ = """
    """.split()

    def can_handle(self, uri_scheme):
        scheme = "postgresql"
        return (uri_scheme == scheme or uri_scheme.startswith(scheme + "-"))

    def connect(self, uri, user=None, password=None, **params):

        parsed_uri = netsa.sql.db_parse_uri(uri)

        params = dict(parsed_uri.get('params', []))

        connparams = {
            'database': parsed_uri['path'].lstrip('/'),
            'host': parsed_uri['host'],
            'user': (user or parsed_uri['user'] or params.get('user', None)),
            'password': (password or parsed_uri['password'] or
                         params.get('password', None))
        }

        if parsed_uri['port']:
            connparams['port'] = parsed_uri['port']

        if params.get('sslmode', None):
            connparams['sslmode'] = params['sslmode']

        conn = psycopg2.connect(**connparams)
        return ppg_connection(self, ['postgres'], conn, connparams=connparams)

    def create_pool(self, uri, user, password, **params):

        parsed_uri = netsa.sql.db_parse_uri(uri)

        if not self.can_handle(parsed_uri['scheme']):
            return None

        parsed_uri = netsa.sql.db_parse_uri(uri)

        uriparams = dict(parsed_uri.get('params', []))

        connparams = {
            'database': parsed_uri['path'].lstrip('/'),
            'host': parsed_uri['host'],
            'user': (user or parsed_uri['user'] or
                     uriparams.get('user', None)),
            'password': (password or parsed_uri['password'] or
                         uriparams.get('password', None))
        }

        if parsed_uri['port']:
            connparams['port'] = parsed_uri['port']

        if uriparams.get('sslmode', None):
            uriparams['sslmode'] = uriparams['sslmode']

        if 'mincached' in uriparams:
            uriparams['mincached'] = int(uriparams['mincached'])
        if 'maxcached' in uriparams:
            uriparams['maxcached'] = int(uriparams['maxcached'])

        poolparams = dict(params.items() + connparams.items() +
                          uriparams.items())

        return ppg_pool(self, poolparams)


class ppg_pool(netsa.sql.db_pool):
    __slots__ = """
        _driver
        _params
    """.split()

    def __init__(self, driver, params):
        try:
            from DBUtils.PooledDB import PooledDB
        except ImportError:
            raise ImportError(
                "Connection pooling requires the DButils Python package.")

        netsa.sql.db_pool.__init__(self, driver)
        self._pool = PooledDB(psycopg2,
                              blocking=True,
                              **params)

    def connect(self):
        conn = self._pool.connection()
        return ppg_connection(self.get_driver(), ['postgres'], conn,
                              pool=self)


class ppg_connection(netsa.sql.db_connection):
    __slots__ = """
        _psycopg2_conn
        _ppg_connparams
        _ppg_pool
        _cursor_counter
        _cursor_counter_lock
    """.split()
    def __init__(self, driver, variants, conn, pool=None, connparams=None):
        netsa.sql.db_connection.__init__(self, driver, variants)
        self._psycopg2_conn = conn
        self._ppg_pool = pool
        self._ppg_connparams = connparams
        self._cursor_counter = 0
        self._cursor_counter_lock = threading.Lock()
        self.execute("set timezone = 0")
    def clone(self):
        if self._ppg_pool != None:
            return self._ppg_pool.connect()
        else:
            conn = psycopg2.connect(**self._ppg_connparams)
            return ppg_connection(self._driver, ['postgres'], conn,
                                  connparams=self._ppg_connparams)
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
