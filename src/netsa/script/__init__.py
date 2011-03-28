# -*- coding: utf-8 -*-

# Copyright 2008-2011 by Carnegie Mellon University

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
Overview
--------

The :mod:`netsa.script` module provides a common framework for
building SiLK-based analysis scripts.  This framework is intended to
make scripts re-usable and automatable without much extra work on the
part of script authors.  The primary concerns of the scripting
framework are providing metadata for cataloging available scripts,
standardizing handling of command-line arguments (particularly for
flow data input), and locating output files.

Here's an example of a simple Python script using the
:mod:`netsa.script` framework.

First is a version without extensive comments, for reading clarity.
Then the script is repeated with comments explaining each section.

.. sourcecode:: python

    #!/usr/bin/env python

    # Import the script framework under the name "script".
    from netsa import script

    # Set up the metadata for the script, including the title, what it
    # does, who wrote it, who to ask questions about it, etc.
    script.set_title("Sample Framework Script")
    script.set_description(\"\"\"
        An example script to demonstrate the basic features of the
        netsa.script scripting framework.  This script counts the
        number of frobnitzim observed in each hour (up to a maximum
        volume of frobs per hour.)
    \"\"\")
    script.set_version("0.1")
    script.set_contact("H. Bovik <hbovik@example.org>")
    script.set_authors(["H. Bovik <hbovik@example.org>"])

    script.add_int_param("frob-limit",
        "Maximum volume of frobs per hour to observe.",
        default=10)

    script.add_float_param("frobnitz-sensitivity",
        "Sensitivity (between 0.0 and 1.0) of frobnitz categorizer.",
        default=0.61, expert=True, minimum=0.0, maximum=1.0)

    script.add_flow_params(require_pull=True)

    script.add_output_file_param("output-path",
        "Number of frobnitzim observed in each hour of the flow data.",
        mime_type="text/csv")

    # See the text for discussion of the next two functions.

    def process_hourly_data(out_file, flow_params, frob_limit, frob_sense):
        ...

    def main():
        frob_limit = script.get_param("frob-limit")
        frobnitz_sensitivity = script.get_param("frobnitz-sensitivity")
        out_file = script.get_output_file("output-path")
        for hour_params in script.get_flow_params().by_hour():
            process_hourly_data(out_file, hour_params, frob_limit,
                                frobnitz_sensitivity)

    script.execute(main)

Let's break things down by section:

.. sourcecode:: python

    #!/usr/bin/env python

    from netsa import script

This is basic Python boilerplate.  Any other libraries we use would
also be imported at this time.

.. sourcecode:: python

    script.set_title("Sample Framework Script")
    script.set_description(\"\"\"
        An example script to demonstrate the basic features of the
        netsa.script scripting framework.  This script counts the
        number of frobnitzim observed in each hour (up to a maximum
        volume of frobs per hour.)
    \"\"\")
    script.set_version("0.1")
    script.set_contact("H. Bovik <hbovik@example.org>")
    script.set_authors(["H. Bovik <hbovik@example.org>"])

Script metadata allows users to more easily find out information about
a script, and browse available scripts stored in a central repository.
The above calls define all of the metadata that the `netsa.script`
framework currently supports.  It is possible that a future version
will include additional metadata fields.

.. sourcecode:: python

    script.add_int_param("frob-limit",
        "Maximum volume of frobs per hour to observe.",
        default=10)

    script.add_float_param("frobnitz-sensitivity",
        "Sensitivity (between 0.0 and 1.0) of frobnitz categorizer.",
        default=0.61, expert=True, minimum=0.0, maximum=1.0)

Script parameters are defined by calling ``netsa.script.add_X_param``
(where *X* is a type) for each parameter.  Depending on the type of
the parameter, there may be additional configuration options (like
*minimum* and *maximum* for the float parameter above) available.  See
the documentation for each function later in this document.

Expert parameters are tuning parameters that are intended for expert
use only.  An expert parameter is created by setting *expert* to
``True`` when creating a new parameter.  This parameter will then be
displayed only if the user asks for ``--help-expert``, and the normal
help will indicate that expert options are available.

.. sourcecode:: python

    script.add_flow_params(require_pull=True)

Parameters involving flow data are handled separately, in order to
ensure that flows are handled consistently across all of our scripts.
The :func:`netsa.script.add_flow_params` function is used to add all
of the flow related command-line arguments at once.  There is
currently only one option.  If the *require_pull* option is set, the
flow data must come from an ``rwfilter`` data pull (including switches
like ``--start-date``, ``--end-date``, ``--class``, etc.)  If
*require_pull* is not set, then it is also possible for input files or
pipes to be given on the command-line.

.. sourcecode:: python

    script.add_output_file_param("output-path",
        "Number of frobnitzim observed in each hour of the flow data.",
        mime_type="text/csv")

Every output file (not temporary working file) that the script
produces must also be defined using calls to the framework—this
ensures that when an automated tool is used to run the script, it can
find all of the relevant output files.  It's preferable, but not
required, for a MIME content-type (like ``"text/csv"``) and a short
description of the contents of the file be included.

.. sourcecode:: python

    def process_hourly_data(out_file, flow_params, frob_limit, frob_sense):
        ...

In this example, the ``process_hourly_data`` function would be
expected to use the functions in :mod:`netsa.util.shell` to acquire
and process flow data for each hour (based on the *flow_params*
argument).  The details have been elided for simplicity in this
example.

.. sourcecode:: python

    def main():
        frob_limit = script.get_param("frob-limit")
        frobnitz_sensitivity = script.get_param("frobnitz-sensitivity")
        out_file = script.get_output_file("output-path")
        for hour_data in script.get_flow_params().by_hour():
            process_hourly_data(out_file, hour_params, frob_limit,
                                frobnitz_sensitivity)

It is important that no work is done outside the ``main`` function
(which can be given any name you wish).  If instead you do work in the
body of the file outside of a function, that work will be done whether
or not the script has actually been asked to do work.  (For example,
if the script is given ``--help``, it will not normally call your
``main`` function.)  So make sure everything is in here.

.. sourcecode:: python

    script.execute(main)

The final statement in the script should be a call to
:func:`netsa.script.execute`, as shown above.  This allows the
framework to process any command-line arguments (including producing
help output, etc.), then call your ``main`` function, and finally do
clean-up work after the completion of your script.

See the documentation for functions in this module for more details on
individual features, including further examples.
"""

import atexit
import datetime
import os.path
import re
import sys
import tempfile
import textwrap
import threading
import weakref

import netsa
import netsa.json
import netsa.util.shell

class ParamError(Exception):
    """
    This exception represents an error in the arguments provided to a
    script at the command-line.  For example, ``ParamError('foo',
    '2x5', 'not a valid integer')`` is the exception generated when
    the value given for an integer param is not parsable, and will
    produce the following error output when thrown from a script's
    ``main`` function::

        <script-name>: Invalid foo '2x5': not a valid integer
    """
    def __init__(self, param, value, message):
        """
        Create a new :class:`ParamError` exception from a parameter
        name, a parameter value, and an error message describing the
        problem with the value.
        """
        Exception.__init__(self, param, value, message)
        self._param = param
        self._value = value
        self._message = message
    def __str__(self):
        """
        Return a human-readable representation of this error, suitable
        for printing as the error output of a script.
        """
        if isinstance(self._param, basestring):
            return "Invalid %s %s: %s" % \
                (self._param, repr(self._value), self._message)
        else:
            return "Invalid %s %s: %s" % \
                (self._param['name'], repr(self._value), self._message)

class UserError(Exception):
    """
    This exception represents an error reported by the script that
    should be presented in a standard way.  For example,
    ``UserError('your message here')`` will produce the following
    error output when thrown from a script's ``main`` function::

        <script-name>: your message here
    """
    pass

class ScriptError(Exception):
    """
    This exception represents an error in script definition or an
    error in processing script data.  This is thrown by some
    :mod:`netsa.script` calls.
    """
    pass

from netsa.script import params
from netsa.data.times import make_datetime, bin_datetime
from netsa.data.format import datetime_silk_hour, datetime_silk_day

import model

_script = model.Script(os.path.abspath(sys.argv[0]))
_script_verbosity = 0
_script_param_values = {}
_script_outputs = {}

def set_title(script_title):
    return _script.set_title(script_title)
set_title.__doc__ = _script.set_title.__doc__

def set_description(script_description):
    return _script.set_description(script_description)
set_description.__doc__ = _script.set_description.__doc__

def set_version(script_version):
    return _script.set_version(script_version)
set_version.__doc__ = _script.set_version.__doc__

def set_package_name(script_package_name):
    return _script.set_package_name(script_package_name)
set_package_name.__doc__ = _script.set_package_name.__doc__

def set_contact(script_contact):
    return _script.set_contact(script_contact)
set_contact.__doc__ = _script.set_contact.__doc__

def set_authors(script_authors):
    return _script.set_authors(script_authors)
set_authors.__doc__ = _script.set_authors.__doc__

def add_author(script_author):
    return _script.add_author(script_author)
add_author.__doc__ = _script.add_author.__doc__

def add_text_param(name, help, required=False, default=None, default_help=None,
                   expert=False, **text_args):
    return _script.add_text_param(name, help, required, default, default_help,
                                  expert, **text_args)
add_text_param.__doc__ = _script.add_text_param.__doc__

def add_int_param(name, help, required=False, default=None, default_help=None,
                  expert=False, **int_args):
    return _script.add_int_param(name, help, required, default, default_help,
                                 expert, **int_args)
add_int_param.__doc__ = _script.add_int_param.__doc__

def add_float_param(name, help, required=False, default=None,
                    default_help=None, expert=False, **float_args):
    return _script.add_float_param(name, help, required, default, default_help,
                                   expert, **float_args)
add_float_param.__doc__ = _script.add_float_param.__doc__

def add_date_param(name, help, required=False, default=None,
                   default_help=None, expert=False):
    return _script.add_date_param(name, help, required, default,
                                  default_help, expert)
add_date_param.__doc__ = _script.add_date_param.__doc__

def add_label_param(name, help, required=False, default=None,
                    default_help=None, expert=False, **label_args):
    return _script.add_label_param(name, help, required, default,
                                   default_help, expert, **label_args)
add_label_param.__doc__ = _script.add_label_param.__doc__

def add_file_param(name, help, required=False, default=None,
                   default_help=None, expert=False, **file_args):
    return _script.add_file_param(name, help, required, default,
                                  default_help, expert, **file_args)
add_file_param.__doc__ = _script.add_file_param.__doc__

def add_dir_param(name, help, required=False, default=None,
                   default_help=None, expert=False):
    return _script.add_dir_param(name, help, required, default,
                                  default_help, expert)
add_dir_param.__doc__ = _script.add_dir_param.__doc__

def add_path_param(name, help, required=False, default=None,
                   default_help=None, expert=False):
    return _script.add_path_param(name, help, required, default,
                                  default_help, expert)
add_path_param.__doc__ = _script.add_path_param.__doc__

def add_flag_param(name, help, default=False,
                   default_help=None, expert=False):
    return _script.add_flag_param(name, help, default,
                                  default_help, expert)
add_flag_param.__doc__ = _script.add_flag_param.__doc__

def add_flow_params(require_pull=False, without_params=[]):
    return _script.add_flow_params(require_pull, without_params)
add_flow_params.__doc__ = _script.add_flow_params.__doc__

def add_output_file_param(name, help, required=True, expert=False,
                          description=None,
                          mime_type="application/octet-stream"):
    return _script.add_output_file_param(name, help, required, expert,
                                         description, mime_type)
add_output_file_param.__doc__ = _script.add_output_file_param.__doc__

def add_output_dir_param(name, help, required=True, expert=False,
                         description=None,
                         mime_type="application/octet-stream"):
    return _script.add_output_dir_param(name, help, required, expert,
                                        description, mime_type)
add_output_dir_param.__doc__ = _script.add_output_dir_param.__doc__

def _print_failure(out, msg):
    script_name = os.path.basename(sys.argv[0])
    out.write("%s: %s\n" % (script_name, msg))
    out.write("Use '%s --help' for usage\n" % script_name)
    sys.exit(1)

def _print_warning(out, msg):
    script_name = os.path.basename(sys.argv[0])
    out.write("%s: %s\n" % (script_name, msg))

_long_wrapper = textwrap.TextWrapper(
    initial_indent="        ", subsequent_indent="        ", expand_tabs=False,
    replace_whitespace=True, width=75)

_short_wrapper = textwrap.TextWrapper(
    initial_indent="", subsequent_indent="        ", expand_tabs=False,
    replace_whitespace=True, width=75)

def _print_long(out, text):
    if isinstance(text, list):
        out.write("\n\n".join(_long_wrapper.fill(t) for t in text))
    else:
        out.write(_long_wrapper.fill(text))
    out.write("\n")

def _print_short(out, text):
    if isinstance(text, list):
        out.write(_short_wrapper.fill(text[0]))
        for t in text[1:]:
            out.write("\n\n")
            out.write(_long_wrapper.fill(t))
    else:
        out.write(_short_wrapper.fill(text))
    out.write("\n")

def _print_usage(out, expert=False):
    script_name = os.path.basename(sys.argv[0])
    if _script._metadata.get('title', None):
        out.write("%s usage:\n" % _script._metadata['title'])
    else:
        out.write("usage:\n")
    text = script_name
    for p in _script._params:
        if p.get('required', False):
            text += " --%s=X" % p['name']
    text += " [SWITCHES]"
    if _script._flow_params and not _script._flow_params_require_pull:
        text += " [FILES]"
    _print_short(out, text)
    if _script._metadata.get('description', None):
        out.write("\n")
        _print_long(out, _script._metadata['description'])
    if not _script._params:
        return
    out.write("\n")
    out.write("SWITCHES:\n")
    out.write("--help No Arg. Print usage output and exit.\n")
    any_expert = False
    for p in _script._params:
        # Only display expert switches if they've been asked for
        if p['expert']:
            any_expert = True
            break
    if any_expert:     
        out.write("--help-expert No Arg. Print expert usage output "
                  "and exit.\n")
    out.write("--verbose Opt. Arg. Set verbose output level. (Also -v[v...].)\n")
    for p in _script._params:
        # Only display expert switches if they've been asked for
        if not p['expert']:
            required = ""
            if p['required'] == True:
                required = "Required. "
            req_arg = ""
            if p['kind'] == params.KIND_FLAG:
                req_arg = "No Arg. "
            else:
                req_arg = "Req. Arg. "
            default_text = ""
            if p['default_help'] != None:
                default_text = " Def. %s" % p['default_help']
            elif p['default'] != None:
                default_text = " Def. %s" % p['default']
            text = list(p['help'])
            text[0] = "--%s %s%s%s" % (p['name'], required, req_arg, text[0])
            text[-1] = "%s%s" % (text[-1], default_text)
            _print_short(out, text)
    if any_expert:     
        if expert:
            out.write("\n")
            out.write("EXPERT SWITCHES:\n")
            for p in _script._params:
                if p['expert']:
                    req_arg = ""
                    if p['kind'] == params.KIND_FLAG:
                        req_arg = "No Arg. "
                    else:
                        req_arg = "Req. Arg. "
                    default_text = ""
                    if p['default_help'] != None:
                        default_text = " Def. %s" % p['default_help']
                    elif p['default'] != None:
                        default_text = " Def. %s" % p['default']
                    text = list(p['help'])                        
                    text[0] = "--%s %s%s%s" % (p['name'], required,
                                               req_arg, text[0])
                    text[-1] = "%s%s" % (text[-1], default_text)
                    _print_short(out, text)
    if expert == 'netsa-script':
        out.write("\n")
        out.write("NETSA SCRIPT FRAMEWORK SWITCHES:\n")
        _print_short(out, "--netsa-script-help No Arg. Print framework "
                     "usage output and exit.")
        _print_short(out, "--netsa-script-get-metadata No Arg. Output meta-"
                     "data and exit.")
        _print_short(out, "--netsa-script-show-metadata No Arg. Pretty print "
                     "meta-data and exit.")

def _print_metadata(out, verbose):
    out.write(model.unparse_script_metadata(_script,
                                            verbose=(verbose or netsa.DEBUG)))
    out.write("\n")

def get_param(name):
    """
    Returns the value of the parameter given by the :class:`str`
    argument *name*.  This parameter will be in the type specified for
    the param when it was added (for example, date parameters will
    return a :class:`datetime.datetime` object.)  Note that a
    parameter with no default that is not required may return
    ``None``.
    """
    return _script_param_values.get(name, None)

def get_verbosity():
    """
    Returns the current verbosity level (default 0) for the script
    invocation.  The :func:`message` function may be used to
    automatically emit messages based on the verbosity level set for
    the script.  Verbosity is set from the command-line via the
    ``--verbose`` or ``-v`` flags.
    """
    return _script_verbosity

def display_message(text, min_verbosity=1):
    """
    Writes the string *text* to ``stderr``, as long as the script's
    verbosity is greater than or equal to *min_verbosity*.  Verbosity
    is set from the command-line via the ``--verbose`` or ``-v``
    flags.  The current verbosity level may be retrieved by using the
    :func:`get_verbosity` function.

    Use this function to write debugging or informational messages
    from your script for command-line use.  For example, writing out
    which file you are processing, or what stage of processing is in
    progress.

    Do not use it to write out important information such as error
    messages or actual output.  (See :exc:`UserError` or
    :func:`add_output_file_param` and :func:`add_output_dir_param` for
    error messages and output.)
    """
    if _script_verbosity >= min_verbosity:
        sys.stderr.write(text)
        sys.stderr.write("\n")
        

_flow_params_filenames = None

Nothing = object()

_flow_params_notes = []

def add_flow_annotation(script_annotation):
    """
    Add a note that will automatically be included in SiLK data pulls
    generated by this script.  This will be included only by rwfilter
    pulls created by this script using :class:`Flow_params`.
    """
    if not isinstance(script_annotation, basestring):
        type_error = TypeError("script_annotation must be string")
        raise type_error
    _flow_params_notes.append(script_annotation)

class Flow_params(object):
    """
    This object represents the flow selection arguments to an
    ``rwfilter`` data pull.  In typical use it is built automatically
    from command-line arguments by the
    :func:`netsa.script.get_flow_params` call.  Afterwards, methods
    such as :meth:`by_hour` are used to modify the scope of the data
    pull, and then the parameters are included in a call to
    ``rwfilter`` using the functions in :mod:`netsa.util.shell`.

    **Example:** Process SMTP data from the user's requested flow
    data:

    .. sourcecode:: python

        netsa.util.shell.run_parallel(
            ["rwfilter %(flow_params)s --protocol=6 --aport=25 --pass=stdout",
             "rwuniq --fields=sip",
             ">>output_file.txt"],
            vars={'flow_params': script.get_flow_params()})

    **Example:** Separately process each hour's SMTP data from the
    user's request flow data:

    .. sourcecode:: python

        flow_params = script.get_flow_params()
        # Iterate over each hour individually
        for hourly_params in flow_params.by_hour():
            # Format ISO-style datetime for use in a filename
            sdate = iso_datetime(hourly_params.get_start_date())
            netsa.util.shell.run_parallel(
                ["rwfilter %(flow_params)s --protocol=6 --pass=stdout",
                 "rwuniq --fields=dport",
                 ">>output_file_%(sdate)s.txt"],
                vars={'flow_params': hourly_params,
                      'sdate': sdate})
    """
    def _check_params(self):
        input_sources = 0
        if self._input_pipe != None:
            input_sources += 1
            if not isinstance(self._input_pipe, basestring):
                script_error = ScriptError(
                    "input_pipe argument %s is not a str"
                        % repr(self._input_pipe))
                raise script_error
        if self._xargs != None:
            input_sources += 1
            if not isinstance(self._xargs, basestring):
                script_error = ScriptError(
                    "xargs argument %s is not a str" % repr(self._xargs))
                raise script_error
        if self._filenames != None:
            input_sources += 1
            try:
                for x in self._filenames:
                    if not isinstance(x, basestring):
                        script_error = ScriptError(
                            "filenames argument %s is not a list of str"
                                % repr(self._filenames))
                        raise script_error
            except TypeError:
                script_error = ScriptError(
                    "filenames argument %s is not a list of str"
                        % repr(self._filenames))
                raise script_error
        if (self._class != None or
                self._type != None or
                self._flowtypes != None or
                self._sensors != None or
                self._start_date != None or
                self._end_date != None):
            input_sources += 1
            if self._class != None:
                if not isinstance(self._class, basestring):
                    script_error = ScriptError(
                        "flow_class argument %s is not a str"
                            % repr(self._class))
                if ',' in self._class:
                    script_error = ScriptError(
                        "flow_class argument %s contains ','"
                            % repr(self._class))
                    raise script_error
            if self._type != None:
                try:
                    for x in self._type:
                        if isinstance(x, basestring):
                            continue
                        script_error = ScriptError(
                            "type argument %s is not a list of str"
                                % repr(self._type))
                        raise script_error
                except TypeError:
                    script_error = ScriptError(
                        "type argument %s is not a list of str"
                            % repr(self._type))
                    raise script_error
            if self._flowtypes != None:
                try:
                    for x in self._flowtypes:
                        if isinstance(x, basestring) and '/' in x:
                            continue
                        script_error = ScriptError(
                            "flowtypes argument %s is not a list of str/str"
                                % repr(self._flowtypes))
                except TypeError:
                    script_error = ScriptError(
                        "flowtypes argument %s is not a list of str/str"
                            % repr(self._flowtypes))
                    raise script_error
            if self._sensors != None:
                try:
                    for x in self._sensors:
                        if isinstance(x, basestring):
                            continue
                        script_error = ScriptError(
                            "sensors argument %s is not a list of str"
                                % repr(self._sensors))
                except TypeError:
                    script_error = ScriptError(
                        "sensors argument %s is not a list of str"
                            % repr(self._sensors))
                    raise script_error
            if self._start_date != None:
                if not isinstance(self._start_date, datetime.datetime):
                    script_error = ScriptError(
                        "start_date argument %s is not a datetime"
                            % repr(self._start_date))
                    raise script_error
            if self._end_date != None:
                if not isinstance(self._end_date, datetime.datetime):
                    script_error = ScriptError(
                        "end_date argument %s is not a datetime"
                            % repr(self._end_date))
                    raise script_error
            if self._start_date != None and self._end_date != None:
                if self._end_date < self._start_date:
                    script_error = ScriptError(
                        "end_date %s precedes start_date %s"
                            % repr(self._start_date), repr(self._end_date))
                    raise script_error
        if input_sources > 1:
            script_error = ScriptError(
                "Multiple input sources in Flow_params")
            raise script_error
        elif input_sources < 1:
            script_error = ScriptError(
                "Flow_params requires at least one input source")
            raise script_error
        if self._class != None or self._type != None:
            if self._flowtypes != None:
                script_error = ScriptError(
                    "Can't use class/type and flowtypes together")
                raise script_error
    def __init__(self, flow_class=None, flow_type=None, flowtypes=None,
                 sensors=None, start_date=None, end_date=None,
                 input_pipe=None, xargs=None, filenames=None):
        """
        Creates a new flow selection parameter bundle from a variety
        of arguments representing command-line parameters of the SiLK
        ``rwfilter`` tool.

        *start_date* and *end_date* arguments should be
        :class:`datetime.datetime` objects, *filenames* should be a
        list of strings, and every other argument should be a single
        string.

        Note that the ``rwfilter`` parameters ``--class`` and
        ``--type`` are given as the named arguments *flow_class* and
        *flow_type* in order to avoid clashes with standard features
        of Python.

        Also note that filenames which would have occurred bare on the
        command-line are given in the *filenames* argument.

        Raises a :class:`ScriptError` if the parameters are
        inconsistent or incorrectly typed.  (For example, if
        *data_rootdir* were an integer, *start_date* were a string, or
        both flow selection parameters and file source parameters were
        given.)
        """
        self._class = flow_class
        self._type = flow_type
        self._flowtypes = flowtypes
        self._sensors = sensors
        self._start_date = start_date
        self._end_date = end_date
        self._input_pipe = input_pipe
        self._xargs = xargs
        try:
            if filenames == None:
                self._filenames = None
            else:
                self._filenames = list(filenames)
        except TypeError:
            raise ScriptError("filenames argument %s is not iterable" %
                              repr(filenames))
        self._check_params()
    def __repr__(self):
        """
        Returns a machine-readable-ish representation of this
        :class:`Flow_params` object.
        """
        return ("netsa.script.Flow_params(%s)" % repr(str(self)))
    def __str__(self):
        """
        Returns a human-readable representation of this
        :class:`Flow_params` object.  The representation used is the
        text of the command-line arguments involved.
        """
        quoted_params = []
        for a in self.get_argument_list(no_meta=True):
            if "'" in a or '\\' in a:
                quoted_params.append('"%s"' % a.replace("\\", "\\\\")
                                               .replace('"', "\\\""))
            elif '"' in a or ' ' in a:
                quoted_params.append("'%s'" % a)
            else:
                quoted_params.append(a)
        return ' '.join(quoted_params)

    def get_class(self):
        """
        Returns the ``rwfilter`` pull ``--class`` argument as a
        :class:`str`.
        """
        return self._class
    def get_type(self):
        """
        Returns the ``rwfilter`` pull ``--type`` argument as a
        :class:`str`.
        """
        return self._type
    def get_flowtypes(self):
        """
        Returns the ``rwfilter`` pull ``--flowtypes`` argument as a
        :class:`str`.
        """
        return self._flowtypes
    def get_sensors(self):
        """
        Returns the ``rwfilter`` pull ``--sensors`` argument as a
        :class:`list` of :class:`str`.
        """
        if self._sensors == None and self._class != None:
            return _get_class_sensors()[self._class]
        return self._sensors
    def get_start_date(self):
        """
        Returns the ``rwfilter`` pull ``--start-date`` argument as a
        :class:`datetime.datetime` object.
        """
        return self._start_date
    def get_end_date(self):
        """
        Returns the ``rwfilter`` pull ``--end-date`` argument as a
        :class:`datetime.datetime` object.
        """
        return self._end_date
    def get_input_pipe(self):
        """
        Returns the ``rwfilter`` pull ``--input-pipe`` argument as a
        :class:`str`.
        """
        return self._input_pipe
    def get_xargs(self):
        """
        Returns the ``rwfilter`` pull ``--xargs`` argument as a
        :class:`str`.
        """
        return self._xargs
    def get_filenames(self):
        """
        Returns any files given on the command-line for an
        ``rwfilter`` pull as a :class:`str`.
        """
        return self._filenames
    def is_pull(self):
        """
        Returns ``True`` if this :class:`Flow_params` object
        represents a data pull from the repository.  (i.e. it contains
        selection switches.)
        """
        if self._input_pipe != None: return False
        if self._xargs != None: return False
        if self._filenames != None: return False
        if (self._class != None or
                self._type != None or
                self._flowtypes != None or
                self._sensors != None or
                self._start_date != None or
                self._end_date != None):
            return True
        return False
    def is_files(self):
        """
        Returns ``True`` if this :class:`Flow_params` object
        represents processing of already retrieved files.
        """
        if self._input_pipe != None: return True
        if self._xargs != None: return True
        if self._filenames != None: return True
        if (self._class != None or
                self._type != None or
                self._flowtypes != None or
                self._sensors != None or
                self._start_date != None or
                self._end_date != None):
            return False
        return False        

    def using(self, flow_class=Nothing, flow_type=Nothing, flowtypes=Nothing,
              sensors=Nothing, start_date=Nothing, end_date=Nothing,
              input_pipe=Nothing, xargs=Nothing, filenames=Nothing):
        """
        Returns a new :class:`Flow_params` object in which the
        arguments in this call have replaced the parameters in *self*,
        but all other parameters are the same.

        Raises a :class:`ScriptError` if the new parameters are
        inconsistent or incorrectly typed.
        """
        result = self.__class__(self._class, self._type, self._flowtypes,
                                self._sensors, self._start_date,
                                self._end_date, self._input_pipe,
                                self._xargs, self._filenames)
        if flow_class != Nothing: result._class = flow_class
        if flow_type != Nothing: result._type = flow_type
        if flowtypes != Nothing: result._flowtypes = flowtypes
        if sensors != Nothing: result._sensors = sensors
        if start_date != Nothing: result._start_date = start_date
        if end_date != Nothing: result._end_date = end_date
        if input_pipe != Nothing: result._input_pipe = input_pipe
        if xargs != Nothing: result._xargs = xargs
        if filenames != Nothing: result._filenames = filenames
        result._check_params()
        return result
        
    def get_argument_list(self, no_meta=False):
        """
        Returns the bundle of flow selection parameters as a list of
        strings suitable for use as command-line arguments in an
        ``rwfilter`` call.  This is automatically called by the
        :mod:`netsa.util.shell` routines when a :class:`Flow_params`
        object is used as part of a command.
        """
        self._check_params()
        args = []
        if not no_meta:
            if _script._metadata.get(
                'title', _script._metadata.get('version', None)) != None:
                script_title = _script._metadata.get('title', "<unknown>")
                script_version = _script._metadata.get('version', "<unknown>")
                args += ["--note-add",
                         "Generated via netsa.script for \"%s/%s\"" %
                         (script_title, script_version)]
            for note in _flow_params_notes:
                args += ["--note-add", note]
        if self._class:
            args += ["--class", self._class]
        if self._type:
            args += ["--type", self._type]
        if self._flowtypes:
            args += ["--flowtypes", self._flowtypes]
        if self._sensors:
            args += ["--sensors", ','.join(self._sensors)]
        if self._start_date:
            args += ["--start-date", datetime_silk_hour(self._start_date)]
        if self._end_date:
            args += ["--end-date", datetime_silk_hour(self._end_date)]
        if self._input_pipe:
            args += ["--input-pipe", self._input_pipe]
        if self._xargs:
            args += ["--xargs", self._xargs]
        if self._filenames:
            args += self._filenames
        return args
    def by_hour(self):
        """
        Given a :class:`Flow_params` object including a ``start-date``
        and an ``end-date``, returns an iterator yielding new
        :class:`Flow_params` object identical to this one specialized
        for each hour in the time period.

        Example (strings are schematic of the :class:`Flow_params`
        involved):

        .. sourcecode:: python

            >>> # Note: Flow_params cannot actually take a str argument like this.
            >>> some_flows = Flow_params('--type in,inweb --start-date 2009/01/01T00 '
            >>>                          '--end-date 2009/01/01T02')
            >>> list(some_flows.by_hour())
            [netsa.script.Flow_params('--type in,inweb --start-date 2009/01/01T00 '
                                      '--end-date 2009/01/01T00'),
             netsa.script.Flow_params('--type in,inweb --start-date 2009/01/01T01 '
                                      '--end-date 2009/01/01T01'),
             netsa.script.Flow_params('--type in,inweb --start-date 2009/01/01T02 '
                                      '--end-date 2009/01/01T02')]

        See also :meth:`by_day` which iterates over the time span of
        the :class:`Flow_params` by days instead of hours.

        Raises a :class:`ScriptError` if the :class:`Flow_params` has
        no date information (for example, the script user specified
        input files rather than a data pull.)  This can be prevented
        by using *require_pull* in your call to
        :func:`script.add_flow_params`.
        """
        # return iterator of Flow_params just like this one, but for each
        # hour in the time period
        if self._start_date == None or self._end_date == None:
            raise ScriptError("Cannot get hourly parts of a pull "
                              "specified without time")
        t = self._start_date
        e = self._end_date
        while t < e:
            yield Flow_params(self._class, self._type,
                              self._flowtypes, self._sensors,
                              t, t + datetime.timedelta(hours=1,
                                                        microseconds=-1),
                              self._input_pipe, self._xargs, self._filenames)
            t = t + datetime.timedelta(hours=1)
    def by_day(self):
        """
        Given a :class:`Flow_params` object including a ``start-date``
        and an ``end-date``, returns an iterator yielding a
        :class:`Flow_params` for each individual day in the time span.

        If the original :class:`Flow_params` starts or ends on an hour
        that is not midnight, the first or last yielded pulls will not
        be for full days.  All of the other pulls will be full days
        stretching from midnight to midnight.

        See also :meth:`by_hour` which iterates over the time span
        of the :class:`Flow_params` by hours instead of days.

        Raises a :class:`ScriptError` if the :class:`Flow_params` has
        no date information (for example, the script user specified
        input files rather than a data pull.)  This can be prevented
        by using *require_pull* in your call to
        :func:`script.add_flow_params`.
        """
        if self._start_date == None or self._end_date == None:
            raise ScriptError("Cannot get daily parts of a pull "
                              "specified without time")
        t = self._start_date
        e = self._end_date
        while t < e:
            # End date for new pull is either e or end of day at t.
            edate = min(e, bin_datetime(
                             datetime.timedelta(days=1),
                             t + datetime.timedelta(days=1)) +
                           datetime.timedelta(microseconds=-1))
            yield Flow_params(self._class, self._type,
                              self._flowtypes, self._sensors,
                              t, edate,
                              self._input_pipe, self._xargs, self._filenames)
            t = bin_datetime(datetime.timedelta(days=1),
                             t + datetime.timedelta(days=1))
    def by_sensor(self):
        """
        Given a :class:`Flow_params` object including a data pull,
        returns an interator yielding a :class:`Flow_params` for each
        individual sensor defined in the system.
        """
        if self._start_date == None:
            raise ScriptError("Cannot get sensor parts from file inputs")
        sensors = self.get_sensors()
        if sensors == None:
            raise ScriptError("Cannot get sensor list without knowing "
                              "class")
        for s in sensors:
            yield Flow_params(self._class, self._type,
                              self._flowtypes, [s],
                              self._start_date, self._end_date,
                              self._input_pipe, self._xargs, self._filenames)

_class_info_lock = threading.Lock()
_default_class = None
_class_sensors = {}
_sensors = set()
_site_config_warned = False

def _generate_class_info():
    global _default_class
    if _default_class != None or _class_sensors:
        return
    _class_info_lock.acquire()
    try:
        if _default_class != None or _class_sensors:
            return
        # Generate default class by parsing rwfilter --help output
        try:
            (rwf_out, rwf_err) = netsa.util.shell.run_collect("rwfilter --help")
            for l in rwf_out.split("\n"):
                if '--class Req Arg.' in l:
                    default_class = l.split(" Def. ")[1]
                    _default_class = default_class
                    break
        except:
            pass
        # Generate list of sensors for each class
        try:
            try:
                (mapsid_out, mapsid_err) = netsa.util.shell.run_collect(
                    "mapsid --print-classes")
            except:
                global _site_config_warned
                if not _site_config_warned:
                    # Failure means no site config file
                    _print_warning(sys.stderr,
                                   "Site configuration file not found")
                    _site_config_warned = True
                #sys.exit(1)
            for l in mapsid_out.split("\n"):
                # Mapping lines have a -> in them.  Skip other lines.
                if ' -> ' not in l:
                    continue
                (sensor_id, _, sensor_name, class_list) = l.split()
                class_list = class_list[1:-1].split(',')
                for c in class_list:
                    class_sensors = _class_sensors.get(c, [])
                    _class_sensors[c] = class_sensors
                    class_sensors.append(sensor_name)
                    _sensors.add(sensor_name)
        except Exception:
            # Make safe for 2.4
            (exc_type, exc_value, exc_tb) = sys.exc_info()
            if exc_type == SystemExit:
                raise
            pass
    finally:
        _class_info_lock.release()

def _get_default_class():
    _generate_class_info()
    return _default_class

def _get_class_sensors():
    _generate_class_info()
    return _class_sensors

def _get_classes():
    _generate_class_info()
    return _class_sensors.keys()

def _get_sensors():
    _generate_class_info()
    return _sensors

def get_flow_params():
    """
    Returns a :class:`Flow_params` object encapsulating the
    ``rwfilter`` flow selection parameters the script was invoked
    with.  This object is filled in based on the command-line
    arguments described in :func:`add_flow_params`.
    """
    return Flow_params(
        get_param("class"), get_param("type"), get_param("flowtypes"),
        get_param("sensors"), get_param("start-date"), get_param("end-date"),
        get_param("input-pipe"), get_param("xargs"), _flow_params_filenames)

def get_output_file_name(name):
    """
    Returns the filename for the output parameter *name*.  Note that
    many SiLK tools treat the names ``stdout``, ``stderr`, and ``-``
    as meaning something special.  ``stdout`` and ``-`` imply the
    output should be written to standard out, and ``stderr`` implies
    the output should be written to standard error.  It is not
    required that you handle these special names, but it helps with
    interoperability.  Note that you may need to take care when
    passing these filenames to SiLK command-line tools for output or
    input locations, for the same reason.

    If you use :func:`netsa.script.get_output_file`, it will
    automatically handle these special filenames.

    If this output file is optional, and the user has not specified a
    location for it, this function will return ``None``.
    """
    out_info = _script._outputs[name]
    fn = get_param(name)
    if fn == None:
        return None
    _script_outputs[name] = {'path': fn,
                             'mime_type': out_info['mime_type'],
                             'description': out_info['description']}
    return fn

_get_output_file_used_stdout = False
_get_output_file_used_stderr = False
_get_output_file_lock = threading.Lock()
_get_output_file_map = {}

def get_output_file(name, append=False):
    """
    Returns an open :class:`file` object for the output parameter
    *name*.  The special names ``stdout``, ``-`` are both translated
    to standard output, and ``stderr`` is translated to standard
    error.

    If you need the output file name, use
    :func:`netsa.script.get_output_file_name` instead.

    If *append* is ``True``, then the file is opened for append.
    Otherwise it is opened for write.
    """
    global _get_output_file_used_stdout
    global _get_output_file_used_stderr
    _get_output_file_lock.acquire()
    try:
        if name in _get_output_file_map:
            out_file = _get_output_file_map[name]
            if out_file != None and out_file.closed:
                # If it's closed, we need to open a new one.
                out_file = None
            else:
                return out_file
        fn = get_output_file_name(name)
        if fn == None:
            out_file = None
        elif fn == '-' or fn == 'stdout':
            # Standard output
            if _get_output_file_used_stdout:
                # We already used standard output.  :X
                output_error = ParamError(name, fn,
                                          "multiple outputs on stdout")
                _print_failure(sys.stderr, str(output_error))
            else:
                _get_output_file_used_stdout = True
                out_file = sys.stdout
        elif fn == 'stderr':
            # Standard error
            if _get_output_file_used_stderr:
                # We already used standard error.
                output_error = ParamError(name, fn,
                                          "multiple outputs on stderr")
                _print_failure(sys.stderr, str(output_error))
            else:
                _get_output_file_used_stderr = True
        else:
            # An actual filename
            mode = 'wb'
            if append:
                mode = 'ab'
            out_file = open(fn, mode)
        _get_output_file_map[name] = out_file
        return out_file
    finally:
        _get_output_file_lock.release()

_get_output_dir_lock = threading.Lock()
_get_output_dir_map = weakref.WeakValueDictionary()

def get_output_dir_file_name(dir_name, file_name,
                             description=None, mime_type=None):
    """
    Returns the path for the file named *file_name* in the output
    directory specified by the parameter *dir_name*.  Also lets the
    :mod:`netsa.script` system know that this output file is about to
    be used.  If provided, the *description* and *mime_type* arguments
    have meanings as described in :func:`add_output_file_param`.  If
    these arguments are not provided, the defaults from the call where
    *dir_name* was defined in :func:`add_output_dir_param` are used.

    If the output directory parameter is optional, and the user has
    not specified a location for it, this function will return
    ``None``.
    """
    out_info = dict(_script._outputs[dir_name])
    if description != None:
        out_info['description'] = description
    if mime_type != None:
        out_info['mime_type'] = mime_type
    dir_path = get_param(dir_name)
    if dir_path == None:
        return None
    path = os.path.join(dir_path, file_name)
    _script_outputs[path] = {'path': path,
                             'mime_type': out_info['mime_type'],
                             'description': out_info['description']}
    return path

def get_output_dir_file(dir_name, file_name,
                        description=None, mime_type=None,
                        append=False):
    """
    Returns the an open :class:`file` object for the file named
    *file_name* in the output directory specified by the parameter
    *dir_name*.  Also lets the :mod:`netsa.script` system know that
    this output file is about to be used.  If provided, the
    *description* and *mime_type* arguments have meanings as described
    in :func:`add_output_file_param`.  If these arguments are not
    provided, the defaults from the call where *dir_name* was defined
    in :func:`add_output_dir_param` are used.

    If the output dir param is optional, and the user has not
    specified a location for it, this function will return ``None``.

    If *append* is ``True``, the file is opened for append.
    Otherwise, the file is opened for write.
    """
    _get_output_dir_lock.acquire()
    try:
        if (dir_name, file_name) in _get_output_dir_map:
            out_file = _get_output_dir_map[(dir_name, file_name)]
            if out_file != None and out_file.closed:
                # Have to re-open
                out_file = None
            else:
                return out_file
        fn = get_output_dir_file_name(dir_name, file_name, description,
                                      mime_type)
        if fn == None:
            out_file = None
        else:
            mode = 'wb'
            if append:
                mode = 'ab'
            out_file = open(fn, mode)
        _get_output_dir_map[(dir_name, file_name)] = out_file
        return out_file
    finally:
        _get_output_dir_lock.release()

_temp_dir = tempfile.mkdtemp()
atexit.register(os.system, ("rm -rf %s" % _temp_dir))
os.environ["TMPDIR"] = _temp_dir
os.environ["TEMP"] = _temp_dir
os.environ["TMP"] = _temp_dir

_get_temp_dir_lock = threading.RLock()
_get_temp_dir_map = weakref.WeakValueDictionary()
_get_temp_dir_filenames = set()
_get_temp_dir_filename_counter = 0

def get_temp_dir_file_name(file_name=None):
    """
    Return the path to a file named *file_name* in a temporary
    directory that will be cleaned up when the process exits.  If
    *file_name* is ``None`` then a new file name is created that has
    not been used before.
    """
    global _get_temp_dir_filename_counter
    _get_temp_dir_lock.acquire()
    try:
        while file_name == None or file_name in _get_temp_dir_filenames:
            # Allocate new filenames until one not in the list of used
            # filenames is found.
            _get_temp_dir_filename_counter += 1
            file_name = "tmp%d.tmp" % _get_temp_dir_filename_counter
        # Remember the filename used.
        _get_temp_dir_filenames.add(file_name)
        return os.path.join(_temp_dir, file_name)
    finally:
        _get_temp_dir_lock.release()

def get_temp_dir_file(file_name=None, append=False):
    """
    Returns an open :class:`file` object for the file named
    *file_name* in the script's temporary working directory.  If
    *append* is ``True``, the file is opened for append.  Otherwise,
    the file is opened for write.  If *file_name* is ``None`` then a
    new file name is used that has not been used before.
    """
    _get_temp_dir_lock.acquire()
    try:
        fn = get_temp_dir_file_name(file_name)
        out_file = _get_temp_dir_map.get(fn, None)
        if out_file == None or out_file.closed:
            out_file = None
        else:
            return out_file
        mode = 'wb'
        if append:
            mode = 'ab'
        out_file = open(fn, mode)
        _get_temp_dir_map[file_name] = out_file
        return out_file
    finally:
        _get_temp_dir_lock.release()

def get_temp_dir_pipe_name(file_name=None):
    """
    Returns the path to a named pipe *file_name* that has been created
    in a temporary directory that will be cleaned up when the process
    exits. If *file_name* is ``None`` then a new file name is created
    that has not been used before.
    """
    _get_temp_dir_lock.acquire()
    try:
        pn = get_temp_dir_file_name(file_name)
        os.mkfifo(pn)
        return pn
    finally:
        _get_temp_dir_lock.release()

def execute(func):
    """
    Executes the ``main`` function of a script.  This should be called
    as the last line of any script, with the script's ``main``
    function (whatever it might be named) as its only argument.

    It is important that all work in the script is done within this
    function.  The script may be loaded in such a way that it is not
    executed, but only queried for metadata information.  If the
    script does work outside of the ``main`` function, this will cause
    metadata queries to be very inefficient.
    """
    global _script_verbosity
    args = sys.argv[1:]
    # Check for special command-line arguments.  If they exist, we ignore
    # everything else and exit.
    for arg in args:
        if arg in ('--help', '-h'):
            _print_usage(sys.stdout)
            sys.exit(0)
        elif arg == '--help-expert':
            _print_usage(sys.stdout, expert=True)
            sys.exit(0)
        elif arg == '--netsa-script-help':
            _print_usage(sys.stdout, expert='netsa-script')
            sys.exit(0)
        elif arg == '--netsa-script-get-metadata':
            _print_metadata(sys.stdout, verbose=False)
            sys.exit(0)
        elif arg == '--netsa-script-show-metadata':
            _print_metadata(sys.stdout, verbose=True)
            sys.exit(0)
    # Fill in defaults
    for param in _script._params:
        if param['required']:
            continue
        if not param['required']:
            if param['default'] != None:
                _script_param_values[param['name']] = \
                    params.parse_value(param, param['default'])
            else:
                _script_param_values[param['name']] = None
    i = 0
    while i < len(args):
        arg = args[i]
        switch = None
        value = None
        # Is it an unnamed argument?
        # Is it a -v[v[v...]] style verbose switch?
        if arg.startswith('-v'):
            count = 1
            for c in arg[2:]:
                if c != 'v':
                    count = None
                    break
                count += 1
            if count != None:
                _script_verbosity = max(_script_verbosity, count)
                del args[i]
                continue
        elif arg.startswith("--verbose="):
            (verbose, num) = arg.split("=", 1)
            try:
                num = int(num)
            except:
                raise ParamError("verbose", num, "not a valid integer")
            _script_verbosity = max(_script_verbosity, num)
            del args[i]
            continue
        elif arg == '--verbose':
            _script_verbosity = max(_script_verbosity, 1)
            del args[i]
            continue
        elif not arg.startswith('--'):
            i += 1
            continue
        # Okay, break it up into --<switch>=<value> if needed
        if '=' in arg:
            (switch, value) = arg.split('=',1)
        else:
            switch = arg
        del args[i]
        # Get the script_param(s) for this switch
        matching_params = _script._find_params(switch)
        if not matching_params:
            # No matching param
            _print_failure(sys.stderr, "unrecognized option %s" % repr(arg))
        if len(matching_params) > 1:
            # Too many matching params
            _print_failure(sys.stderr, "option %s is ambiguous" % repr(arg))
        # Exactly one match!  Excellent.
        param = matching_params[0]
        if param['kind'] == params.KIND_FLAG:
            if value is not None:
                _print_failure(sys.stderr,
                               "option %s takes no arguments" % repr(switch))
        else:
            if value is None:
                if i == len(args):
                    _print_failure(sys.stderr,
                                   "option %s requires an argument" %
                                   repr(switch))
                else:
                    value = args[i]
                    del args[i]
        # Now we have a value if we need it.
        try:
            _script_param_values[param['name']] = \
                params.parse_value(param, value)
        except params.ParamError, ex:
            _print_failure(sys.stderr, str(ex))
    # Check for missing required parameters
    missing_required = []
    for param in _script._params:
        if param['required']:
            if param['name'] not in _script_param_values:
                missing_required.append("'--%s'" % param['name'])
    if missing_required:
        _print_failure(sys.stderr, "missing required options: %s" %
                       (", ".join(missing_required)))
    # Check and normalize flow params
    if _script._flow_params:
        # 0) Check for site config file.  If not, immediately exit.  Warning
        #    has already been printed at this point.
        if _default_class == None:
            sys.exit(1)
        # 1) Check that if input-pipe, xargs, or command-line filenames are
        # given, that no globbing params were given.
        input_sources = 0
        glob_input_source = False
        if not _script._flow_params_require_pull:
            if _script_param_values.get('input-pipe', None) != None:
                input_sources += 1
            if _script_param_values.get('xargs', None) != None:
                input_sources += 1
            if len(args) > 0: input_sources += 1
        if (_script_param_values.get('class', None) != None or
            _script_param_values.get('type', None) != None or
            _script_param_values.get('flowtypes', None) != None or
            _script_param_values.get('sensors', None) != None or
            _script_param_values.get('start-date', None) != None or
            _script_param_values.get('end-date', None) != None):
            input_sources += 1
            glob_input_source = True
        if input_sources > 1:
            _print_failure(sys.stderr, """Multiple input sources were specified
        Input must come from only one of --input-pipe, --xargs, file names on
        the command line, or a combination of the file selection switches""")
        elif input_sources < 1:
            if _script._flow_params_require_pull:
                _print_failure(sys.stderr, """No input was specified.
        Must specify at least one file selection switch""")
            else:
                _print_failure(sys.stderr, """No input was specified.
        No file selection switches were given, neither --input-pipe nor --xargs
        was specified, and no files are present on the command line""")
        # 2) --class and --type are exclusive with --flowtypes
        if (_script_param_values.get('class', None) != None or
            _script_param_values.get('type', None) != None):
            if _script_param_values.get('flowtypes', None) != None:
                _print_failure(sys.stderr, "Cannot use --flowtypes when "
                               "either --class or --type are specified")
        if args:
            if _script._flow_params_require_pull:
                _print_failure(sys.stderr,
                               "Too many arguments or unrecognized "
                               "switch %s" % repr(args[0]))
            else:
                global _flow_params_filenames
                _flow_params_filenames = args
                args = []
        # 2) Make class, sensors, start-date, end-date fully correct
        if glob_input_source:
            if _script_param_values.get('class', None) == None:
                _script_param_values['class'] = _get_default_class()
            if _script_param_values.get('class', None) != None:
                if ',' in _script_param_values['class']:
                    _print_failure(sys.stderr, "Invalid --class: Use "
                                   "--flowtypes to process multiple classes")
                if _script_param_values['class'] not in _get_classes():
                    _print_failure(sys.stderr, "Invalid --class: Cannot find "
                                   "class %s" %
                                   repr(_script_param_values['class']))
#            if _script_param_values.get('sensors', None) == None:
#                if _script_param_values.get('class', None) != None:
#                    _script_param_values['sensors'] = \
#                        ','.join(_get_class_sensors()[
#                                     _script_param_values['class']])
            if _script_param_values.get('sensors', None) != None:
                sl = []
                sensor_failure = False
                global_sensors = _get_sensors()
                class_sensors = None
                if _script_param_values.get('class', None) != None:
                    class_name = _script_param_values['class']
                    class_sensors = _get_class_sensors()[class_name]
                for s in _script_param_values['sensors'].split(','):
                    if s not in global_sensors:
                        _print_warning(sys.stderr, "Invalid sensors %s: "
                                       "Unknown sensor name" % repr(s))
                        sensor_failure = True
                        continue
                    if class_sensors != None:
                        if s not in class_sensors:
                            _print_warning(sys.stderr,
                                           "Ignoring sensor %s that is not "
                                           "used by specified flowtypes" % s)
                            continue
                    sl.append(s)
                if sensor_failure:
                    sys.exit(1)
                _script_param_values['sensors'] = sl
            if _script_param_values.get('start-date', None) == None:
                _script_param_values['start-date'] = \
                    (datetime_silk_day(datetime.datetime.utcnow()),
                     params.PRECISION_DAY)
            (sdate, sdate_prec) = _script_param_values['start-date']
            if sdate_prec > params.PRECISION_HOUR:
                _print_warning(sys.stderr, "start-date precision greater than "
                               "hours ignored")
                sdate_prec = params.PRECISION_HOUR
            if sdate_prec == params.PRECISION_HOUR:
                start_date = bin_datetime(datetime.timedelta(hours=1),
                                          make_datetime(sdate))
            elif sdate_prec == params.PRECISION_DAY:
                start_date = bin_datetime(datetime.timedelta(days=1),
                                          make_datetime(sdate))
            else:
                _print_failure(sys.stderr,
                               "Precision failure parsing start-date")
            _script_param_values['start-date'] = start_date
            if _script_param_values.get('end-date', None) == None:
                _script_param_values['end-date'] = (sdate, sdate_prec)
            (edate, edate_prec) = _script_param_values['end-date']
            if edate_prec > params.PRECISION_HOUR:
                _print_warning(sys.stderr, "end-date precision greater than "
                               "hours ignored")
                edate_prec = params.PRECISION_HOUR
            if edate_prec == params.PRECISION_HOUR:
                end_date = bin_datetime(datetime.timedelta(hours=1),
                                        make_datetime(edate))
                end_date = end_date + \
                    datetime.timedelta(minutes=59, seconds=59,
                                       microseconds=999999)
            elif edate_prec == params.PRECISION_DAY:
                end_date = bin_datetime(datetime.timedelta(days=1),
                                        make_datetime(edate))
                end_date = end_date + \
                    datetime.timedelta(hours=23, minutes=59,
                                       seconds=59, microseconds=999999)
            else:
                _print_failure(sys.stderr,"Precision failure parsing end-date")
            _script_param_values['end-date'] = end_date
            if start_date > end_date:
                _print_failure(sys.stderr, "end-date of %s is earlier than\n"
                               "        start-date of %s" % (edate, sdate))
        
    
    # If argument parsing was correct, execute main function.
    try:
        func()
    except UserError:
        _print_failure(sys.stderr, str(sys.exc_info()[1]))
    except ParamError:
        _print_failure(sys.stderr, str(sys.exc_info()[1]))

__all__ = """

    ParamError
    ScriptError
    UserError

    set_title
    set_description
    set_version
    set_contact
    set_authors
    add_author

    add_text_param
    add_int_param
    add_float_param
    add_date_param
    add_label_param
    add_file_param
    add_dir_param
    add_path_param
    add_flag_param

    add_flow_params

    add_output_file_param
    add_output_dir_param

    get_param

    get_verbosity
    display_message

    add_flow_annotation
    get_flow_params

    Flow_params

    get_output_file_name
    get_output_file
    get_output_dir_file_name
    get_output_dir_file

    get_temp_dir_file_name
    get_temp_dir_file

    get_temp_dir_pipe_name

    execute

""".split()
