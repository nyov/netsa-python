#!/usr/bin/env python

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
# Contract F19628-00-C-0003. Carnegie Mellon University retains 
# copyrights in all material produced under this contract. The U.S. 
# Government retains a non-exclusive, royalty-free license to publish or 
# reproduce these documents, or allow others to do so, for U.S. 
# Government purposes only pursuant to the copyright license under the 
# contract clause at 252.227.7013.
# @OPENSOURCE_HEADER_END@

# Inserts new licensing/warranty text between a line with the marker
#   @<license>_HEADER_START@
# and a line
#   @<license>_HEADER_END@
# (where <license> is the name of the license to be placed), replacing
# any text in between.  The licenses to use are taken from the
# --license-directory command-line argument, or "./licenses" in the
# current directory if none is specified.  Each file in that directory
# with a name of the form "header-<license>.txt" is available for use.

import os
import re
import sys

files = sys.argv[1:]

license_text = {}
license_dir = os.path.dirname(__file__)
if not license_dir:
    license_dir = "."

print "Reading licenses from %s:" % repr(license_dir)

for license_file in os.listdir(license_dir):
    license_path = os.path.join(license_dir, license_file)
    if (license_file.startswith("LICENSE-") and license_file.endswith(".txt")
            and os.path.isfile(license_path)):
        license_text[license_file[8:-4]] = open(license_path, 'r').readlines()
        print "    %s" % license_file

print

def printheader(out, license, prefix):
    for l in license_text[license]:
        out.write(prefix)
        out.write(l)

re_start = re.compile(r"^(?P<prefix>.*)\@(?P<license>[^@]+)_HEADER_START\@")
re_end = re.compile(r"\@(?P<license>[^@]+)_HEADER_END\@")

print "Updating files:"

for f in files:
    in_header = False
    matched = False
    in_file = open(f, 'r')
    out_file = open(f + ".fixed", 'w')
    for l in in_file:
        m = re_start.search(l)
        if m and m.group('license') in license_text:
            # Matched start of header section for a license we know
            in_header = True
            matched = True
            out_file.write(l)
            printheader(out_file, m.group('license'), m.group('prefix'))
            continue
        m = re_end.search(l)
        if m:
            # Matched end of header section
            in_header = False
            out_file.write(l)
            continue
        if in_header:
            # Throw away old header
            continue
        out_file.write(l)
    in_file.close()
    out_file.close()
    if matched:
        # We replaced some stuff
        os.rename(f, f + ".bak")
        os.rename(f + ".fixed", f)
        print "    %s - updated" % f
    else:
        os.unlink(f + ".fixed")
        print "    %s - unchanged" % f

print
print "Done"
