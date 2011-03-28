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

"""
This module contains utility functions for working with collections of
`netsa.script`-based scripts.  Note that it is not yet complete.
"""

__docformat__ = "restructuredtext en"

import os
import os.path
import sys

import netsa.json
from netsa.script import ScriptError
from netsa.script import model
from netsa.util.shell import run_collect, command

_script_errors = {}

def fetch_script_details(script_path):
    """
    Given the path to an executable script, execute the script in a
    special way to retrieve metadata, and return a
    `netsa.script.model.Script` object.  Note that this may be
    dangerous if the path pointed to by *script_path* is not actually
    a `netsa.script` script.

    Raises a `ScriptError` if the path does not point to an executable
    file, or if the executable file does not produce proper metadata.
    """
    # Check first if the script file exists.
    if not os.path.isfile(script_path):
        script_error = ScriptError(
            "Script %s is not a regular file" % repr(script_path))
        raise script_error
    try:
        # Okay, now let's try
        sc_out = ""
        sc_err = ""
        (sc_out, sc_err) = run_collect(
            "%(python_path)s %(script_path)s --netsa-script-get-metadata",
            vars={'python_path': sys.executable,
                  'script_path': script_path})
        script = model.parse_script_metadata(sc_out)
        return script
    except ScriptError:
        raise
    except:
        script_error = ScriptError(
            "Script %s failed to return metadata--not a framework script?\n"
            "%s\n%s%s"
            % (repr(script_path), sys.exc_info()[1], sc_out, sc_err))
        raise script_error

def fetch_script_directory(path):
    """
    Given the path to a directory full of `netsa.script`-based Python
    scripts, retrieves their metadata and returns a list of
    `netsa.script.model.Script` objects for scripts in that directory.
    Note that it is potentially dangerous to apply this operation to
    directories that contain executables that are not
    `netsa.script`-based scripts.
    """
    result = {}
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            try:
                result[item] = fetch_script_details(item_path)
            except ScriptError, ex:
                _script_errors[item] = str(ex)
                pass
    return result

__all__ = """

    fetch_script_details
    fetch_script_directory

""".split()
