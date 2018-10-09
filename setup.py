#!/usr/bin/env python
# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import os.path, sys
import os

# Make sure Python is new enough
if not sys.version_info >= "2.6":
    print >>sys.stderr, "netsa-python 1.5 requires Python 2.6 or greater"

# Make sure netsa-python .py files are in the path, since we need them
# for this setup script to operate.
sys.path[:0] = \
    [os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))]

from netsa import dist

dist.set_name("netsa-python")
dist.set_version("1.5")
dist.set_copyright("2008-2016 Carnegie Mellon University")

dist.set_title("NetSA Python")
dist.set_description("""
    A grab-bag of Python routines and frameworks that we have found
    helpful when developing analyses using the SiLK toolkit.
""")

dist.set_maintainer("NetSA Group <netsa-help@cert.org>")

dist.set_url("http://tools.netsa.cert.org/netsa-python/index.html")

dist.set_license("GPL")

dist.add_package("netsa")
dist.add_package("netsa.data")
dist.add_package("netsa.data.test")
dist.add_package("netsa.dist")
dist.add_package_data("netsa.dist", "netsa_sphinx_config.py.in")
dist.add_package_data("netsa.dist", "tools_web/layout.html")
dist.add_package_data("netsa.dist", "tools_web/theme.conf")
dist.add_package_data("netsa.dist", "tools_web/static/tools.css_t")
dist.add_package("netsa.files")
dist.add_package("netsa.files.test")
dist.add_package("netsa.json")
dist.add_package("netsa.json.test")
dist.add_package("netsa.logging")
dist.add_package("netsa.logging.test")
dist.add_package("netsa.script")
dist.add_package("netsa.script.golem")
dist.add_package("netsa.sql")
dist.add_package("netsa.sql.test")
dist.add_package("netsa.tools")
dist.add_package("netsa.util")
dist.add_package("netsa.util.test")
dist.add_package("netsa._netsa_silk")
dist.add_package("netsa._netsa_silk.test")

dist.add_module_py("netsa_silk")

dist.add_version_file("src/netsa/VERSION")

dist.add_install_data("share/netsa-python/sql", "sql/create-sa_meta-0.9.sql")

dist.add_extra_files("GPL.txt")
dist.add_extra_files("CHANGES")
dist.add_extra_files("netsa-python.spec")
dist.add_extra_files("sql")

dist.add_unit_test_module("netsa.data.test")
dist.add_unit_test_module("netsa.files.test")
dist.add_unit_test_module("netsa.json.test")
dist.add_unit_test_module("netsa.logging.test")
dist.add_unit_test_module("netsa.util.test")
dist.add_unit_test_module("netsa.sql.test")
dist.add_unit_test_module("netsa._netsa_silk.test")

dist.execute()
