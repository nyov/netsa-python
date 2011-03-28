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
