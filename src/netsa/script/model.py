# -*- coding: utf-8 -*-

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
This module contains the core data model of the :mod:`netsa.script`
scripting framework.  Most users of the framework (those writing
scripts) should not be interested in this module.
"""

import datetime
import re
import textwrap

import netsa
import netsa.script
import netsa.script.params
from netsa.data.format import datetime_silk
import netsa.json
from netsa.util import shell

def process_text(text):
    if text == None:
        return text
    return re.sub(r'\s+', ' ', textwrap.dedent(text)).strip()

def process_long_text(text):
    if text == None:
        return text
    text = textwrap.dedent(text).strip()
    return [re.sub(r'\s+', ' ', s) for s in re.split(r'\n\n+', text)]

class Script(object):
    """
    A :class:`Script` object represents either "a" script or "the"
    script.  In the case of a script written to use the
    :mod:`netsa.script` framework, there is a single :class:`Script`
    object that represents the current script.  In the case of a tool
    that wishes to allow browsing and searching through available
    scripts on a system, there will be one :class:`Script` object for
    each script being examined.
    """
    __slots__ = ('_path', '_params', '_metadata',
                 '_flow_params', '_flow_params_require_pull',
                 '_outputs')
    def __init__(self,
                 script_path=None, script_params={}, script_metadata={},
                 script_flow_params=False,
                 script_flow_params_require_pull=False,
                 script_outputs={}):
        """
        Creates a new :class:`Script` object from the various data
        that make up a script definition.  This should never need to
        be used by anything outside of the :mod:`netsa.script.model`
        module.  See instead
        :func:`netsa.script.model.parse_script_metadata` and the
        :mod:`netsa.script.catalog` module for ways to retrieve script
        information from serialized metadata or existings scripts.
        """
        self._path = script_path
        self._params = script_params
        self._metadata = script_metadata
        self._flow_params = script_flow_params
        self._flow_params_require_pull = script_flow_params_require_pull
        self._outputs = script_outputs
    def __repr__(self):
        """
        Returns a machine-readable representation of this
        :class:`Script` object.
        """
        return "Script(%s)" % repr(self._path)
    def _set_single_metadata(self, key, value):
        if netsa.DEBUG:
            if self._metadata.get(key, None) != None:
                netsa.DEBUG_print('netsa.script: %s meta set multiple '
                                  'times' % key)
        self._metadata[key] = value
    def _set_list_metadata(self, key, value):
        if netsa.DEBUG:
            if self._metadata.get(key, None):
                netsa.DEBUG_print('netsa.script: %s meta set when non-empty'
                                  % key)
        self._metadata[key] = value
    def _add_list_metadata(self, key, value):
        if self._metadata.get(key, None) == None:
            self._metadata[key] = []
        self._metadata[key].append(value)
    def set_title(self, script_title):
        """
        Set the title for this script.  This should be the
        human-readable name of the script, and denote its purpose.
        """
        self._set_single_metadata('title',
                                  process_text(script_title))
    def set_description(self, script_description):
        """
        Set the description for this script.  This should be a longer
        human-readable description of the script's purpose, including
        simple details of its behavior and required inputs.
        """
        self._set_single_metadata('description',
                                  process_long_text(script_description))
    def set_version(self, script_version):
        """
        Set the version number of this script.  This can take any
        form, but the standard *major* . *minor* (. *patch* ) format is
        recommended.
        """
        self._set_single_metadata('version',
                                  process_text(script_version))
    def set_package_name(self, script_package_name):
        """
        Set the package name for this script.  This should be the
        human-readable name of a collection of scripts.
        """
        self._set_single_metadata('package_name',
                                  process_text(script_package_name))
    def set_contact(self, script_contact):
        """
        Set the point of contact email for support of this script,
        which must be a single string.  The form should be suitable
        for treatment as an email address.  The recommended form is a
        string containing::

            Full Name <full.name@contact.email.org>
        """
        self._set_single_metadata('contact', script_contact)
    def set_authors(self, script_authors):
        """
        Set the list of authors for this script, which must be a list
        of strings.  It is recommended that each author be listed in
        the form described for :func:`set_contact`.
        """
        self._set_list_metadata('authors', script_authors)
    def add_author(self, script_author):
        """
        Add another author to the list of authors for this script,
        which must be a single string.  See :func:`set_authors` for
        notes on the content of this string.
        """
        self._add_list_metadata('authors', script_author)
    def _add_param(self, name, help, required, default, default_help,
                   expert, kind, kind_args):
        if netsa.DEBUG:
            for p in self._params:
                if name == p['name']:
                    netsa.DEBUG_print("script: %s param re-defined" % name)
                    break
        # Check param kind
        netsa.script.params.check_param_kind(kind, kind_args)
        # Clear out any conflicting definition
        self._params = [p for p in self._params if p['name'] != name]
        self._params.append(dict(name=name, help=process_long_text(help),
                                 required=required, default=default,
                                 default_help=process_text(default_help),
                                 expert=expert, kind=kind,
                                 kind_args=kind_args))
    def _find_params(self, switch):
        if switch.startswith('--'):
            switch = switch[2:]
        params = self._params
        matches = [p for p in params if p['name'] == switch]
        if not matches:
            # No matches: look for unique prefix matches
            matches = [p for p in self._params if p['name'].startswith(switch)]
        return matches
    def add_text_param(self, name, help, required=False, default=None,
                       default_help=None, expert=False, **text_args):
        """
        Add a text parameter to this script.  This parameter can later
        be fetched as a :class:`str` by the script using
        :func:`netsa.script.get_param`.  The *required*, *default*,
        *default_help*, and *expert* arguments are used by all
        ``add_X_param`` calls, but each kind of parameter also has
        additional features that may be used.  See below for a list of
        these features for text params.

        **Example:** Add a new parameter which is required for the
        script to run.

        .. sourcecode:: python

            add_text_param("graph-title",
                "Display this title on the output graph.",
                required=True)

        It is an error if this parameter is not set, and the script
        will exit with a usage message when it is run at the
        command-line.

        **Example:** Add a new parameter with a default value of ""
        (the empty string):

        .. sourcecode:: python

            add_text_param("graph-comment",
                "Display this comment on the output graph.",
                default="")

        If the parameter is not provided, the default value will be
        used.

        **Example:** Display something different in the help text than
        the actual default value:

        .. sourcecode:: python

            add_text_param("graph-date",
                "Display data for the given date.",
                default=date_for_today(), default_help="today")

        Sometimes a default value should be computed but not displayed
        as the default to the user when they ask for help at the
        command-line.  In this case, a default value should be
        provided (which will be displayed to users of a GUI), while a
        value for *default_help* will be presented in the `--help`
        output.  In addition, GUIs will also display the value of
        *default_help* in some way next to the entry field for this
        parameter.

        It is perfectly legal to provide a value for *default_help*
        and not provide a value for *default*.  This makes sense when
        the only way to compute the default value for the field is at
        actual execution time.  (For example, if the end-date defaults
        to be the same as the provided start-date.)

        **Example:** Add a new "expert" parameter:

        .. sourcecode:: python

            add_text_param("gnuplot-extra-commands",
                "Give these extra command to gnuplot when writing output.",
                expert=True)

        Expert parameters are not listed for users unless they
        explicitly ask for them.  (For example, by using
        ``--help-expert`` at the command line.)

        Other keyword arguments meaningful for text params:

          *regex*
            Require strings to match this regular expression.

        **Example:** Add a new text parameter that is required to
        match a specific pattern for phone numbers:

        .. sourcecode:: python

            add_text_param("phone-number",
                "Send reports to this telephone number.",
                regex=r"[0-9]{3}-[0-9]{3}-[0-9]{4}")
    """
        self._add_param(name, help, required, default, default_help, expert,
                        netsa.script.params.KIND_TEXT, text_args)
    def add_int_param(self, name, help, required=False, default=None,
                      default_help=None, expert=False, **int_args):
        """
        Add an integer parameter to this script.  This parameter can
        later be fetched as an :class:`int` by the script using
        :func:`netsa.script.get_param`.  The *required*, *default*,
        *default_help*, and *expert* arguments are described in the
        help for :func:`netsa.script.add_text_param`.

        Other keyword arguments meaningful for integer parameters:

          *minimum*
            Only values greater than or equal to this value are allowed
            for this param.
          *maximum*
            Only values less than or equal to this value are allowed
            for this param.

        **Example:** Add a new int parameter which is required to be
        in the range 0 <= x <= 65535.

        .. sourcecode:: python

            add_int_param("targeted-port",
                "Search for attacks targeting this port number.",
                required=True, minimum=0, maximum=65535)
    """
        if isinstance(default, (int, long)):
            default = str(default)
        self._add_param(name, help, required, default, default_help, expert,
                        netsa.script.params.KIND_INT, int_args)
    def add_float_param(self, name, help, required=False, default=None,
                        default_help=None, expert=False, **float_args):
        """
        Add a floating-point parameter to this script.  This parameter
        can later be fetched as a :class`float` by the script using
        :func:`netsa.script.get_param`.  The *required*, *default*,
        *default_help* and *expert* arguments are described in the
        help for :func:`netsa.script.add_text_param`.

        Other keyword arguments meaningful for floating-point parameters:

          *minimum*
            Only values greater than or equal to this value are allowed
            for this param.
          *maximum*
            Only values less than or equal to this value are allowed
            for this param.
        """
        if isinstance(default, float):
            default = str(default)
        self._add_param(name, help, required, default, default_help, expert,
                        netsa.script.params.KIND_FLOAT, float_args)
    def add_date_param(self, name, help, required=False, default=None,
                           default_help=None, expert=False):
        """
        Add a date parameter to this script.  This parameter can later
        be fetched by the script as a :class:`datetime.datetime`
        object using :func:`netsa.script.get_param`.  The *required*,
        *default*, *default_help*, and *expert* arguments are
        described in the help for :func:`netsa.script.add_text_param`.
        """
        if isinstance(default, datetime.datetime):
            default = datetime_silk(default)
        self._add_param(name, help, required, default, default_help,
                        expert, netsa.script.params.KIND_DATE, {})
    def add_label_param(self, name, help, required=False, default=None,
                        default_help=None, expert=False, **label_args):
        """
        Add a label parameter to this script.  This parameter can
        later be fetched by the script as a Python :class:`str` using
        :func:`netsa.script.get_param`.  The *required*, *default*,
        *default_help*, and *expert* arguments are described in the
        help for :func:`netsa.script.add_text_param`.

        Other keyword arguments meaningful for label params:

          *regex*
            Require strings to match this regular expression, instead
            of the default ``r"[^\S,]+"`` (no white space or commas).

        **Example:** Add a new label parameter that is required to
        match a specific pattern for phone numbers:

        .. sourcecode:: python

            add_label_param("output-label",
                "Store output to the destination with this label.",
                regex=r"[0-9]{3}-[0-9]{3}-[0-9]{4}")

        """
        self._add_param(name, help, required, default, default_help, expert,
                        netsa.script.params.KIND_LABEL, label_args)
    def add_path_param(self, name, help, required=False, default=None,
                       default_help=None, expert=False):
        """
        Add a path parameter to this script.  This parameter can later
        be fetched by the script as a Python :class:`str` using
        :func:`netsa.script.get_param`.  The *required*, *default*,
        *default_help*, and *expert* arguments are described in the
        help for :func:`netsa.script.add_text_param`.
        """
        self._add_param(name, help, required, default, default_help, expert,
                        netsa.script.params.KIND_PATH, {})
    def add_file_param(self, name, help, required=False, default=None,
                       default_help=None, expert=False, **file_args):
        """
        Add a file parameter to this script.  This parameter can later
        be fetched by the script as a Python :class:`str` filename
        using :func:`netsa.script.get_param`.  The *required*,
        *default*, *default_help*, and *expert* arguments are
        described in the help for :func:`netsa.script.add_text_param`.

        When the script is run at the command-line, an error will be
        reported to the user if they specify a file that does not
        exist, or the path of a directory.

        Other keyword arguments meaningful for file params:

          *mime_type*
             The expected MIME Content-Type of the file, if any.
        """
        self._add_param(name, help, required, default, default_help, expert,
                        netsa.script.params.KIND_FILE, file_args)
    def add_dir_param(self, name, help, required=False, default=None,
                       default_help=None, expert=False):
        """
        Add a directory parameter to this script.  This parameter can
        later be fetched by the script as a Python :class:`str`
        filename using :func:`netsa.script.get_param`.  The
        *required*, *default*, *default_help*, and *expert* arguments
        are described in the help for
        :func:`netsa.script.add_text_param`.

        When the script is run at the command-line, an error will be
        reported to the user if they specify a directory that does not
        exist, or the path of a file.
        """
        self._add_param(name, help, required, default, default_help, expert,
                        netsa.script.params.KIND_DIR, {})
    def add_flag_param(self, name, help, default=False,
                       default_help=None, expert=False):
        """
        Add a flag parameter to this script.  This parameter can later
        be fetched by the script as a :class:`bool` using
        :func:`netsa.script.get_param`.  The *default*,
        *default_help*, and *expert* arguments are described in the
        help for :func:`netsa.script.add_text_param`.
        """
        if default:
            default = True
        else:
            default = False
        self._add_param(name, help, False, default, default_help,
                        expert, netsa.script.params.KIND_FLAG, {})
    def add_flow_params(self, require_pull=False, without_params=[]):
        """
        Add standard flow parameters to this script.  The following
        params are added by default, but individual params may be
        disabled by including their names in the *without_params*
        argument.  You might wish to disable the ``--type`` param, for
        example, if your script will run the same pull multiple times,
        once with ``--type=in,inweb``, then again with
        ``--type=out,outweb``.  (Of course, you might then also want
        to add ``in-type`` and ``out-type`` params to the script.)

          ``--class``
            Req Arg. Class of data to process

          ``--type``
            Req Arg. Type(s) of data to process within the specified
            class.  The type names and default type(s) vary by class.
            Use ``all`` to process every type for the specified class.
            Use `rwfilter --help`` for details on valid class/type
            pairs.

          ``--flowtypes``
            Req Arg. Comma separated list of class/type pairs to
            process.  May use ``all`` for class and/or type.  This is
            alternate way to specify class/type; switch cannot be used
            with ``--class`` and ``--type``

          ``--sensors``
            Req Arg. Comma separated list of sensor names, sensor IDs,
            and ranges of sensor IDs.  Valid sensors vary by class.
            Use `mapsid` to see a mapping of sensor names to IDs and
            classes.

          ``--start-date``
            Req Arg. First hour of data to process.  Specify date in
            ``YYYY/MM/DD[:HH]`` format: time is in UTC.  When no hour
            is specified, the entire date is processed.  Def. Start of
            today

          ``--end-date``
            Req Arg. Final hour of data to process specified as
            ``YYYY/MM/DD[:HH]``.  When no hour specified, end of day
            is used unless `start-date` includes an hour.  When switch
            not specified, defaults to value in `start-date`.

        If the *require_pull* argument to
        :func:`netsa.script.add_flow_params` is not ``True``, input
        filenames may be specified bare on the command-line, and the
        following additional options are recognized:

          ``--input-pipe``
            Req Arg. Read SiLK flow records from a pipe: ``stdin`` or
            path to named pipe. No default

          ``--xargs`` (expert)
            Req Arg. Read list of input file names from a file or pipe
            pathname or ``stdin``. No default

        The values of these parameters can later be retrieved as a
        :class:`netsa.script.Flow_params` object using
        :func:`netsa.script.get_flow_params`.
        """
        if netsa.DEBUG:
            if self._flow_params:
                netsa.DEBUG_print("script: flow params re-defined")
        self._flow_params = True
        self._flow_params_require_pull = require_pull
        default_class = netsa.script._get_default_class()
        default_class_text = "UNKNOWN"
        if default_class != None:
            default_class_text = default_class
        class_list = list(netsa.script._get_class_sensors().keys())
        class_list_text = "UNKNOWN"
        if class_list:
            class_list_text = ','.join(class_list)
        if "class" not in without_params:
            self._add_param("class",
                            ("Class of data to process. Available classes: "
                             "%s" % class_list_text),
                            False, None, default_class_text, False,
                            netsa.script.params.KIND_FLOW_CLASS, {})
        if "type" not in without_params:
            self._add_param("type", """
Type(s) of data to process within the specified class.  The type names
and default type(s) vary by class.  Use 'all' to process every type
for the specified class.  Use 'rwfilter --help' for details on valid
class/type pairs.
                            """, False, None, None, False,
                            netsa.script.params.KIND_FLOW_TYPE, {})
        if ("class" not in without_params and
                "type" not in without_params and
                "flowtypes" not in without_params):
            self._add_param("flowtypes", """
Comma separated list of class/type pairs to process.  May use 'all'
for class and/or type.  This is alternate way to specify class/type;
switch cannot be used with --class and --type
                            """, False, None, None, False,
                            netsa.script.params.KIND_FLOW_FLOWTYPES, {})
        if "sensors" not in without_params:
            self._add_param("sensors", """
Comma separated list of sensor names, sensor IDs, and ranges of sensor
IDs.  Valid sensors vary by class.  Use 'mapsid' to see a mapping of
sensor names to IDs and classes.
                            """, False, None, None, False,
                            netsa.script.params.KIND_FLOW_SENSORS, {})
        if "start-date" not in without_params:
            self._add_param("start-date", """
First hour of data to process.  Specify date in YYYY/MM/DD[:HH]
format: time is in UTC.  When no hour is specified, the entire date is
processed.
                            """, False, None, "Start of today", False,
                            netsa.script.params.KIND_FLOW_DATE, {})
        if "end-date" not in without_params:
            self._add_param("end-date", """
Final hour of data to process specified as YYYY/MM/DD[:HH].  When no
hour specified, end of day is used unless start-date includes an hour.
When switch not specified, defaults to value in start-date.
                            """, False, None, None, False,
                            netsa.script.params.KIND_FLOW_DATE, {})
        if not require_pull:
            if "input-pipe" not in without_params:
                self._add_param("input-pipe", """
Read SiLK flow records from a pipe: 'stdin' or path to named pipe.
                                """, False, None, None, False,
                                netsa.script.params.KIND_PATH, {})
            if "xargs" not in without_params:
                self._add_param("xargs", """
Read list of input file names from a file or pipe pathname or 'stdin'.
                                """, False, None, None, True,
                                netsa.script.params.KIND_PATH, {})
    def add_output_file_param(self, name, help, required=True, expert=False,
                              description=None,
                              mime_type="application/octet-stream"):
        """
        Add an output file parameter to this script.  This parameter
        can later be fetched by the script as a Python :class:`str`
        filename or a Python :class:`file` object using
        :func:`netsa.script.get_output_file_name` or
        :func:`netsa.script.get_output_file`.  Note that if you ask
        for the file name, you may wish to handle the filenames
        ``stdout``, ``stderr``, and ``-`` specially to be consistent
        with other tools.  (See the documentation of
        :func:`netsa.script.get_output_file_name` for details.)
        Unlike most parameters, output file parameters never have
        default values, and are required by default.  If an output
        file parameter is not required, the implication is that if the
        user does not specify this argument, then this output is not
        produced.

        In keeping with the behavior of the SiLK tools, it is an error
        for the user to specify an output file that already exists.
        If the environment variable ``SILK_CLOBBER`` is set, this
        restriction is relaxed and existing output files may be
        overwritten.

        The *mime_type* argument is advisory., but it should be set to
        an appropriate MIME content type for the output file.  The
        framework will not report erroneous types, nor will it
        automatically convert from one type to another.  Examples:

          ``text/plain``
            Human readable text file.

          ``text/csv``
            Comma-separated-value file.

          ``application/x-silk-flows``
            SiLK flow data

          ``application/x-silk-ipset``
            SiLK ipset data

          ``application/x-silk-bag``
            SiLK bag data

          ``application/x-silk-pmap``
            SiLK prefix map data

          ``image/png``
            etc.  Various standard formats, many of which are listed
            `on IANA's website`_.

        .. _`on IANA's website`: http://www.iana.org/assignments/media-types/

        It is by no means necessary to provide a useful MIME type, but
        it is helpful to automated systems that wish to interpret or
        display the output of your script.

        The *description* argument may also be provided, with a
        long-form text description of the contents of this output
        file.  Note that *description* describes the contents of the
        file, while *help* describes the meaning of the command-line
        argument.
        """
        self._add_param(name, help, required, None, None, expert,
                        netsa.script.params.KIND_OUTPUT_FILE, {})
        self._outputs[name] = {'name': name,
                               'kind': 'file',
                               'mime_type': mime_type,
                               'description': description}
    def add_output_dir_param(self, name, help, required=True, expert=False,
                             description=None,
                             mime_type="application/octet-stream"):
        """
        Add an output directory parameter to this script.  This
        parameter can later be used to construct a :class:`str`
        filename or a Python :class:`file` object using
        :func:`netsa.script.get_output_dir_file_name` or
        :func:`netsa.script.get_output_dir_file`.  Unlike most
        parameters, output directory parameters never have default
        values, and are required by default.  If an output directory
        parameter is not required, the implication is that if the user
        does not specify this argument, then this output is not
        produced.

        See :func:`add_output_file_param` for the meanings of the
        *description* and *mime_type* arguments.  In this context,
        these arguments provide default values for files created in
        this output directory.  Each individual file can be given its
        own *mime_type* and *description* when using the
        :func:`netsa.script.get_output_dir_file_name` and
        :func:`netsa.script.get_output_dir_file` functions.
        """
        self._add_param(name, help, required, None, None, expert,
                        netsa.script.params.KIND_OUTPUT_DIR, {})
        self._outputs[name] = {'name': name,
                               'kind': file,
                               'mime_type': mime_type,
                               'description': description}


def parse_script_metadata(metadata_text):
    """
    Given a string containing JSON-encoded script metadata, this
    function creates a new :class:`Script` object.  In the case of
    malformed data or an unsupported version in the metadata, a
    :class:`ScriptError` will be raised.
    """
    script_metadata = netsa.json.loads(metadata_text)
    version = script_metadata.get('netsa_script_version', None)
    if version == 1:
        try:
            return Script(
                script_path=script_metadata['netsa_script_path'],
                script_params=script_metadata['netsa_script_params'],
                script_metadata=script_metadata['netsa_script_metadata'],
                script_flow_params=script_metadata['netsa_script_flow_params'],
                script_flow_params_require_pull=script_metadata[
                    'netsa_script_flow_params_require_pull'],
                script_outputs=script_metadata['netsa_script_outputs'])
        except KeyError:
            script_error = ScriptError("Cannot parse malformed script "
                                       "metadata")
            raise script_error
    else:
        script_error = ScriptError("Cannot parse script metadata for "
                                   "unknown version %s" % repr(version))
        raise script_error

def unparse_script_metadata(script, version=1, verbose=False):
    """
    Given a :class:`Script` object, produces a string containing the
    script's JSON-encoded metadata.  If the *version* parameter
    requests an unsupported version, a :class:`ScriptError` will be
    raised.  If the *verbose* argument is `True`, then an indented
    human-readable form of the JSON will be returned, otherwise a more
    compact form is used.
    """
    if version == 1:
        script_metadata = {
            'netsa_script_version': 1,
            'netsa_script_path': script._path,
            'netsa_script_params': script._params,
            'netsa_script_metadata': script._metadata,
            'netsa_script_flow_params': script._flow_params,
            'netsa_script_flow_params_require_pull':
                script._flow_params_require_pull,
            'netsa_script_outputs': script._outputs,
        }
    else:
        script_error = ScriptError("Cannot unparse script metadata for "
                                   "unknown version %s" % repr(version))
        raise script_error
    if verbose:
        extra_args = dict(sort_keys=True, indent=2)
    else:
        extra_args = dict(separators=(',', ':'))
    return netsa.json.dumps(script_metadata, **extra_args)

class Job(object):
    def __init__(self, job_id=None, job_metadata=None):
        job_id = job_id or job_metadata.get("netsa_job_id", None)
        self._job_id = job_id
        if job_metadata:
            self._job_metadata = job_metadata
        else:
            if not job_id:
                script_error = ScriptError(
                    "No job ID or metadata provided")
                raise script_error
            self._job_metadata = fetch_job_metadata(job_id)
    def update_direct(self): pass
    def update_remote(self, new_metadata):
        "Update this job with new metadata fetched from a remote source."
        self._job_metadata = new_metadata

__all__ = """

    Script

    parse_script_metadata
    unparse_script_metadata

""".split()
