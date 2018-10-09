# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

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
from netsa.util   import shell

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
    if os.path.exists(script_path):
        if not os.path.isfile(script_path):
            script_error = ScriptError(
                "Script %s is not a regular file" % repr(script_path))
            raise script_error
    else:
        script_error = ScriptError(
            "Script %s does not exist" % repr(script_path))
        raise script_error
    def _error_info():
        return repr(script_path), sys.exc_info()[1]
    try:
        # Okay, now let's try
        sc_out = ""
        sc_err = ""
        (sc_out, sc_err) = shell.run_collect(
            "%(python_path)s %(script_path)s --netsa-script-get-metadata",
            vars={'python_path': sys.executable,
                  'script_path': script_path})
        return model.parse_script_metadata(sc_out)
    except ScriptError:
        raise
    except shell.PipelineException, e:
        msg = "Script %s failed to execute:\n%s" % _error_info()
        msg += "\nstderr[[[%s]]]" % e
        script_error = ScriptError(msg)
        raise script_error
    except ValueError:
        msg = "Script %s failed to return metadata " \
                "-- not a framework script?\n%s" % _error_info()
        if sc_err:
            msg += "\nstderr[[[%s]]]" % sc_err.strip()
        script_error = ScriptError(msg)
        raise script_error
    # never say never
    script_error = ScriptError(
        "Script %s produced an unknown exception\n%s" % _error_info())
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
