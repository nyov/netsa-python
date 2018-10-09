#!/usr/bin/env python

# Copyright 2008-2014 by Carnegie Mellon University

# @OPENSOURCE_HEADER_START@
# Use of the Network Situational Awareness Python support library and
# related source code is subject to the terms of the following licenses:
# 
# GNU Public License (GPL) Rights pursuant to Version 2, June 1991
# Government Purpose License Rights (GPLR) pursuant to DFARS 252.227.7013
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

import os.path, sys
import os

# Make sure netsa-python .py files are in the path, since we need them
# for this setup script to operate.
sys.path[:0] = \
    [os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))]

from netsa import dist

dist.set_name("netsa-python")
dist.set_version("1.4.4")
dist.set_copyright("2008-2014 Carnegie Mellon University")

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
dist.add_package_data("netsa.dist", "tools_web")
dist.add_package("netsa.files")
dist.add_package("netsa.files.test")
dist.add_package("netsa.json")
dist.add_package("netsa.json.test")
dist.add_package("netsa.json.simplejson")
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
