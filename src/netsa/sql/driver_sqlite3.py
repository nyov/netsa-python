# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import sqlite3
import netsa.sql

class sl3_driver(netsa.sql.db_driver):
    __slots__ = """
    """.split()
    def can_handle(self, uri_scheme):
        scheme = "nsql-sqlite3"
        return (uri_scheme == scheme or uri_scheme.startswith(scheme + "-"))
    def connect(self, uri, user, password):
        parsed_uri = netsa.sql.db_parse_uri(uri)
        if not self.can_handle(parsed_uri['scheme']):
            return None
        if parsed_uri['host'] and parsed_uri['host'] not in ('', 'localhost'):
            raise Exception("XXX sqlite3 does not support remote databases")
        return sl3_connection(
            self, ['sqlite3'],
            database=parsed_uri['path'],
        )

class sl3_connection(netsa.sql.db_connection):
    __slots__ = """
        _database

        _sqlite3_conn
    """.split()
    def __init__(self, driver, variants, database):
        netsa.sql.db_connection.__init__(self, driver, variants)
        self._database = database
        self._sqlite3_conn = None
        self._connect()
    def _connect(self):
        self._sqlite3_conn = sqlite3.connect(
            database=self._database,
            detect_types=sqlite3.PARSE_DECLTYPES)
    def clone(self):
        return sl3_connection(self._driver, self._variants, self._database)
    def execute(self, query_or_sql, **params):
        return sl3_result(self, query_or_sql, params)
    def commit(self):
        self._sqlite3_conn.commit()
    def rollback(self):
        if self._sqlite3_conn:
            self._sqlite3_conn.rollback()

class sl3_result(netsa.sql.db_result):
    __slots__ = """
        _sqlite3_cursor
    """.split()
    def __init__(self, connection, query, params):
        netsa.sql.db_result.__init__(self, connection, query, params)
        self._sqlite3_cursor = self._connection._sqlite3_conn.cursor()
        variants = self._connection.get_variants()
        (query, params) = \
            self._query.get_variant_qmark_params(variants, params)
        self._sqlite3_cursor.execute(query, params)
    def __iter__(self):
        while True:
            r = self._sqlite3_cursor.fetchone()
            if r == None:
                return
            yield r

netsa.sql.register_driver(sl3_driver())
