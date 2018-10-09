# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import dircache
import os
import re
import sys
from netsa.sql import connect_uri

piece_re = re.compile(r"""
    (?:\.)?
  ( (?:\d+) | (?:\D+) )
""", re.VERBOSE)

def parse_version(version_text):
    """
    Break a version number represented as a string down into a tuple.
    Each piece of the tuple is optionally separated by .s, and
    consists entirely of numeric or non-numeric values.  For example,
    1.1 become (1, 1), 1.1a becomes (1, 1, 'a'), 1.1b1 becomes (1, 1,
    'b', 1), and so on.
    """
    if version_text == None:
        return None
    pos = 0
    end = len(version_text)
    res = []
    while pos < end:
        m = piece_re.match(version_text, pos, end)
        if not m:
            break
        res.append(m.group(1))
        pos = m.end()
    for i in xrange(len(res)):
        try:
            res[i] = int(res[i])
        except:
            pass
    return res

def compare_versions(v1, v2):
    """
    Compare two version numbers, represented as strings, tuples, or
    None.
    """
    # Assumption: Versions are tuples of strings and integers, or None
    if isinstance(v1, basestring):
        v1 = parse_version(v1)
    if isinstance(v2, basestring):
        v2 = parse_version(v2)
    if v1 is None and v2 is not None:
        return -1
    elif v2 is None:
        return 1
    else:
        for i in xrange(min(len(v1), len(v2))):
            if v1[i] < v2[i]:
                return -1
            elif v1[i] > v2[i]:
                return 1
            else:
                pass
    return cmp(len(v1), len(v2))

file_re = re.compile(r"""
(?: .* / )?
    (?P<mode>create|update) -
    (?P<schema_name>[^-]+) -
(?: (?P<old_version>[^-]+) - )?
    (?P<version>.+)
    \.sql
""", re.VERBOSE)

schema_latest = {}              # schema_name -> version
schema_upgrades = {}            # schema_name -> old -> version -> path

def analyze_paths(paths):
    """
    Analyze the schema files available in the given paths (list of
    directories) to determine what versions are available for install
    or upgrade.
    """
    if not isinstance(paths, basestring):
        for path in paths:
            analyze_paths(path)
        return
    for p in dircache.listdir(paths):
        p = os.path.join(paths, p)
        if os.path.isdir(p):
            analyze_paths(p)
        elif os.path.isfile(p):
            m = file_re.match(p)
            if m:
                m_mode = m.group('mode')
                m_schema_name = m.group('schema_name')
                m_old_version = m.group('old_version')
                m_version = m.group('version')
                if m_schema_name not in schema_upgrades:
                    schema_upgrades[m_schema_name] = {}
                if m_old_version not in schema_upgrades[m_schema_name]:
                    schema_upgrades[m_schema_name][m_old_version] = {}
                schema_upgrades[m_schema_name][m_old_version][m_version] = p
                if m_schema_name not in schema_latest:
                    schema_latest[m_schema_name] = m_version
                else:
                    if compare_versions(
                        parse_version(m_version),
                        parse_version(schema_latest[m_schema_name])) > 0:
                        schema_latest[m_schema_name] = m_version

def get_installed_version(db_uri, schema_name):
    """
    Return the currently installed version number of the given schema
    in this database, or None if it is not currently installed.
    """
    db = connect_uri(db_uri)
    try:
        c = db.cursor()
        # First: Check to be sure the sa_meta schema and versions tables exist
        c.execute("""
            select exists
             (select true from pg_tables
                where schemaname = 'sa_meta' and tablename = 'versions')
        """)
        if not c.fetchall()[0][0]:
            # The meta-schema is not installed, so surely nothing else is.
            return None
        c.execute("""
            select version from sa_meta.versions
              where schema_name = %(schema_name)s
            order by schema_name
        """, {'schema_name': schema_name})
        r = c.fetchone()
        if r is None:
            return None
        return r[0]
    finally:
        db.close()

def get_latest_version(paths, schema_name):
    """
    Return the latest version number of the given schema available in
    the given paths (list of directories.)
    """
    analyze_paths(paths)
    return schema_latest.get(schema_name, None)

def get_available_schemas(paths):
    """
    Return a list of (name, version) pairs describing what schemas are
    available for installation in the given paths (list of
    directories).
    """
    analyze_paths(paths)
    return [(schema_name, get_latest_version(paths, schema_name))
            for schema_name in sorted(schema_latest.keys())]

def get_installed_schemas(db_uri):
    """
    Return a list of (name, verson, load_time) triples describing what
    schemas are currently installed in this database, and when they
    were last installed or updated.
    """
    # Check that sa_meta is installed:
    sa_meta_ver = get_installed_version(db_uri, "sa_meta")
    if not sa_meta_ver:
        # Nothing is installed
        return []
    db = connect_uri(db_uri)
    try:
        c = db.cursor()
        c.execute("""
            select schema_name, version, load_time from sa_meta.versions
        """)
        result = []
        for r in c:
            result.append((r[0], r[1], r[2]))
        return result
    finally:
        db.close()

def update_or_install_schema(db_uri, paths, schema_name):
    """
    Connect to this database and Update the named schema to the latest
    version available in paths (a list of directories), or install it
    if it is not currently installed.
    """
    analyze_paths(paths)
    installed_ver = get_installed_version(db_uri, schema_name)
    latest_ver = schema_latest.get(schema_name, None)
    if installed_ver == latest_ver:
        # Already done--do nothing.
        return None
    if latest_ver is None:
        raise Exception(
            "No install script for schema %s is available" % schema_name)
    # Find an upgrade script
    try:
        upgrade_file = \
            schema_upgrades[schema_name][installed_ver][latest_ver]
    except KeyError:
        raise Exception(
            "No upgrade script from %s to %s for schema %s is available" %
            (installed_ver, latest_ver, schema_name))
    sql = open(upgrade_file, 'r').read()
    db = connect_uri(db_uri)
    try:
        try:
            c = db.cursor()
            c.execute(sql)
            c.execute("""
                delete from sa_meta.versions where schema_name = %(schema_name)s
            """, {'schema_name': schema_name})
            c.execute("""
                insert into sa_meta.versions ( schema_name, version, load_time )
                  values ( %(schema_name)s, %(version)s, current_timestamp );
            """, {'schema_name': schema_name, 'version': latest_ver})
            db.commit()
            return latest_ver
        except:
            db.rollback()
            raise
    finally:
#       for notice in db.notices:
#           sys.stdout.write(notice)
        db.close()

__all__ = [
    "update_or_install_schema",
]
