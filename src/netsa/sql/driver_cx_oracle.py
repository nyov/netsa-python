# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import cx_Oracle
import netsa.sql

class cxo_driver(netsa.sql.db_driver):
    __slots__ = """
    """.split()
    def can_handle(self, uri_scheme):
        scheme = "nsql-oracle"
        return (uri_scheme == scheme or uri_scheme.startswith(scheme + "-"))
    def connect(self, uri, user, password):
        parsed_uri = netsa.sql.db_parse_uri(uri)
        if not self.can_handle(parsed_uri['scheme']):
            return None
        params = dict(parsed_uri.get('params', []))
        database = parsed_uri['path'].lstrip('/')
        return cxo_connection(
            self, ['oracle'],
            user=(user or parsed_uri['user'] or params.get('user', None)),
            password=(password or parsed_uri['password'] or
                      params.get('password', None)),
            dsn=parsed_uri['path'].lstrip('/'),
        )

class cxo_connection(netsa.sql.db_connection):
    __slots__ = """
        _user
        _password
        _dsn
        _cx_oracle_conn
    """.split()
    def __init__(self, driver, variants, user, password, dsn):
        netsa.sql.db_connection.__init__(self, driver, variants)
        self._user = user
        self._password = password
        self._dsn = dsn
        self._connect()
    def _connect(self):
        kwargs = {}
        if self._user:
            kwargs['user'] = self._user
        if self._password:
            kwargs['password'] = self._password
        if self._dsn:
            kwargs['dsn'] = self._dsn
        kwargs['threaded'] = True
        self._cx_oracle_conn = cx_Oracle.connect(**kwargs)
    def clone(self):
        return cxo_connection(self._user, self._password, self._dsn)
    def execute(self, query_or_sql, **params):
        return cxo_result(self, query_or_sql, params)
    def commit(self):
        self._cx_oracle_conn.commit()
    def rollback(self):
        if self._cx_oracle_conn:
            self._cx_oracle_conn.rollback()

class cxo_result(netsa.sql.db_result):
    __slots__ = """
        _cx_oracle_cursor
    """.split()
    def __init__(self, connection, query, params):
        netsa.sql.db_result.__init__(self, connection, query, params)
        self._cx_oracle_cursor = self._connection._cx_oracle_conn.cursor()
        variants = self._connection.get_variants()
        (query, params) = \
            self._query.get_variant_named_params(variants, params)
        self._cx_oracle_cursor.execute(query, params)
    def __iter__(self):
        while True:
            r = self._cx_oracle_cursor.fetchone()
            if r == None:
                return
            yield r

netsa.sql.register_driver(cxo_driver())
