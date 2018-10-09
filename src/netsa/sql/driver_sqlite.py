# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import sqlite
import netsa.sql
import datetime
from netsa.data.format import datetime_iso

class sl_driver(netsa.sql.db_driver):
    __slots__ = """
    """.split()
    def can_handle(self, uri_scheme):
        scheme = "nsql-sqlite"
        return (uri_scheme == scheme or uri_scheme.startswith(scheme + "-"))
    def connect(self, uri, user, password):
        parsed_uri = netsa.sql.db_parse_uri(uri)
        if not self.can_handle(parsed_uri['scheme']):
            return None
        if parsed_uri['host'] and parsed_uri['host'] not in ('', 'localhost'):
            raise Exception("XXX sqlite does not support remote databases")
        return sl_connection(
            self, ['sqlite'],
            database=parsed_uri['path'],
        )

class sl_connection(netsa.sql.db_connection):
    __slots__ = """
        _database

        _sqlite_conn
    """.split()
    def __init__(self, driver, variants, database):
        netsa.sql.db_connection.__init__(self, driver, variants)
        self._database = database
        self._sqlite_conn = None
        self._connect()
    def _connect(self):
        self._sqlite_conn = sqlite.connect(database=self._database)
    def clone(self):
        return sl_connection(self._driver, self._variants, self._database)
    def execute(self, query_or_sql, **params):
        return sl_result(self, query_or_sql, params)
    def commit(self):
        self._sqlite_conn.commit()
    def rollback(self):
        if self._sqlite_conn:
            self._sqlite_conn.rollback()

class sl_result(netsa.sql.db_result):
    __slots__ = """
        _sqlite_cursor
    """.split()
    def __init__(self, connection, query, params):
        netsa.sql.db_result.__init__(self, connection, query, params)
        self._sqlite_cursor = self._connection._sqlite_conn.cursor()
        variants = self._connection.get_variants()
        (query, params) = \
            self._query.get_variant_pyformat_params(variants, params)
        for k in params:
            if isinstance(params[k], datetime.datetime):
                params[k] = datetime_iso(params[k])
        self._sqlite_cursor.execute(query, params)
    def __iter__(self):
        while True:
            r = self._sqlite_cursor.fetchone()
            if r == None:
                return
            yield r

netsa.sql.register_driver(sl_driver())
