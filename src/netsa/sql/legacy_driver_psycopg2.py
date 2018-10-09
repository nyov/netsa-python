# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

from netsa.sql.legacy import register_driver

# For now, we only support psycopg2
from datetime import datetime, timedelta
from time import strptime
import psycopg2
import psycopg2.extensions

extensions_registered = False

def cast_abstime(value, curs):
    if value is not None:
        # Convert from "YYYY-MM-DD HH:MM:SS+ZZ"
        base_time = datetime(*strptime(value[:-3], "%Y-%m-%d %H:%M:%S")[:-3])
        tz_adj = timedelta(hours=int(value[-3:]))
        return base_time - tz_adj

def connect(db_info):
    kwargs = {}
    if db_info['username']: kwargs['user'] = db_info['username']
    if db_info['password']: kwargs['password'] = db_info['password']
    if db_info['host']: kwargs['host'] = db_info['host']
    if db_info['port']: kwargs['port'] = db_info['port']
    if db_info['dbname']: kwargs['database'] = db_info['dbname']
    global extensions_registered
    if extensions_registered:
        result = psycopg2.connect(**kwargs)
        c = result.cursor()
        c.execute("set timezone = 0");
        c.close()
        return result
    else:
        result = psycopg2.connect(**kwargs)
        c = result.cursor()
        c.execute("set timezone = 0");
        c.execute("select null::abstime")
        abstime_oid = c.description[0][1]
        ABSTIME = psycopg2.extensions.new_type((abstime_oid,),
                                               "ABSTIME", cast_abstime)
        psycopg2.extensions.register_type(ABSTIME)
        extensions_registered = True
        return result

register_driver("postgresql", connect)
