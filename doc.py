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

import codecs
import os
import os.path
import sys

sys.path[:0] = \
    [os.path.abspath(os.path.join(os.path.dirname(__file__), "python"))]

if 'PYTHONPATH' in os.environ:
    os.environ['PYTHONPATH'] = sys.path[0] + ":" + os.environ['PYTHONPATH']
else:
    os.environ['PYTHONPATH'] = sys.path[0]

from netsa.util.shell import *
from netsa import script

script.set_title("netsa-python Documentation Builder")
script.set_description("""
    Build the documentation for the netsa-python package, including
    both HTML and PDF output.
""")
script.set_contact("NetSA Help <netsa-help@cert.org>")
script.add_author("J. Prevost <prevost1@cert.org>")

script.add_flag_param("realclean",
                      "Clean up any old outputs (before generating)")

script.add_flag_param("html",
                      "Produce HTML output")

script.add_flag_param("site-html",
                      "Produce HTML output for tools.netsa.cert.org",
                      expert=True)

script.add_flag_param("latex",
                      "Produce LaTeX output")

script.add_flag_param("pdf",
                      "Produce PDF output (via LaTeX)")

script.add_flag_param("coverage",
                      "Produce list of items with missing documentation")

script.add_flag_param("clean",
                      "Clean up intermediate files (after generating)")

def convert_file_to_8859_1(filename):
    out_filename = filename + ".fixed"
    sys.stdout.write(filename +": ")
    f = codecs.open(filename, 'r', 'utf-8')
    s = f.read()
    f.close()
    out = codecs.open(out_filename, 'w', 'iso-8859-1')
    for c in s:
        if ord(c) < 128:
            out.write(c)
        else:
            sys.stdout.write("*")
            out.write("&#%d;" % ord(c))
    out.close()
    sys.stdout.write(" ok\n")
    os.rename(out_filename, filename)

def convert_html_to_8859_1(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(".html"):
                convert_file_to_8859_1(os.path.join(dirpath, filename))

def main():
    # Get into the doc directory
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "doc")))

    if script.get_param("realclean"):
        run_parallel(["rm -rf coverage html latex site-html"])

    if script.get_param("coverage"):
        # Build the coverage data
        run_parallel(["sphinx-build -b coverage . coverage"],
                     stdout=sys.stdout, stderr=sys.stderr)

    if script.get_param("html"):
        run_parallel(["sphinx-build -b html . html"],
                     stdout=sys.stdout, stderr=sys.stderr)

    if script.get_param("site-html"):
        run_parallel(["sphinx-build -b html -D html_theme=tools"
                      "    -D html_style=tools.css . site-html"],
                     stdout=sys.stdout, stderr=sys.stderr)
        # Okay.  Now run over everything and convert it to 8859-1.  Ugh.
        print "converting non-ASCII to entities..."
        convert_html_to_8859_1("site-html")

    if script.get_param("latex") or script.get_param("pdf"):
        run_parallel(["sphinx-build -b latex . latex"],
                     stdout=sys.stdout, stderr=sys.stderr)

    if script.get_param("pdf"):
        # Build the latex version into PDF (multiple times for indexing)
        os.chdir("latex")
        run_parallel(["pdflatex netsa-python.tex"])
        run_parallel(["pdflatex netsa-python.tex"])
        run_parallel(["pdflatex netsa-python.tex"])
        run_parallel(["cp netsa-python.pdf .."])

    if script.get_param("clean"):
        run_parallel(["rm -rf coverage site-html/.buildinfo "
	              "    site-html/.doctrees html/.buildinfo "
	              "    html/.doctrees latex"])

script.execute(main)
