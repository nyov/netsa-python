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

import datetime
import pgdb
import netsa.sql

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

class pgs_result(netsa.sql.db_result):
    __slots__ = """
        _pgdb_cursor
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
        self._pgdb_cursor.execute(query, params)
    def __iter__(self):
        while True:
            r = self._pgdb_cursor.fetchone()
            if r == None:
                return
            yield r

netsa.sql.register_driver(pgs_driver())
