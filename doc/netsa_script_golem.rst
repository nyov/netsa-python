.. _netsa-script-golem:

:mod:`netsa.script.golem` --- Golem Script Automation
=====================================================

.. automodule:: netsa.script.golem

Overview
--------

    The :ref:`Golem Script Automation <netsa-script-golem>` framework is
    a specialized extension of the
    :ref:`NetSA Scripting Framework <netsa-script>` for constructing
    automated analysis scripts. Such scripts might be launched
    periodically from a cron job in order to produce regular sets of
    results in a data repository. In addition to the golem-specific
    extensions, :mod:`netsa.script.golem` offers the same functionality
    as :mod:`netsa.script`.

    At its heart, Golem is a template engine combined with some
    synchronization logic across analytic time bins. The templates
    define the output paths for result data and the command line
    sequences and pipelines used to generate these results. Template
    variables are known as *tags*. Golem provides certain tags by
    default and others can be added or modified via the golem
    :ref:`configuration functions <golem-config-funcs>`.

    Golem Automation is designed to allow developers to build scripts
    that easily consume the output results of other golem scripts
    without the need for detailed knowledge of the implementation
    details of the external script (e.g. how often it runs or what
    pathnames it uses for populating its data repository). When provided
    the path to the external script in its configuration, a golem script
    will interrogate the external script for information regarding its
    output results, automatically synchronize across processing windows,
    and make the result paths available for use in command templates as
    input paths.

    In addition to analysis automation, Golem scripts also offer a query
    mode so that results in the data repository can be easily examined
    or pulled to local directories.

    Golem offers a number of shortcuts and convenience functions
    specific to the `SiLK Flow Analysis suite <http://tools.netsa.cert.org/netsa-python/index.html>`_,
    but is not limited to using SiLK for analysis.

    See the :ref:`examples <golem-examples>` at the end of this
    chapter to learn how to write a golem script. See the description of
    :ref:`template and tag usage <golem-templates>` for details on tags
    provided for use within templates. See the
    :ref:`API reference <golem-config-funcs>` for more thorough
    documentation of the features and interface. See the
    :ref:`CLI reference <golem-cli>` for the standard command line
    parameters that golem enables.

.. _golem-cli:

Command Line Usage
------------------

    Golem-enabled scripts offer standard command line parameters grouped
    into three categories: :ref:`basic <golem-basic-cli>`,
    :ref:`repository-related <golem-repository-cli>`, and
    :ref:`query-related <golem-query-cli>`. Parameters must be enabled
    by the script author. Parameters can be enabled individually or by
    category. The :func:`add_golem_params` function will enable all
    parameters.

    Golem scripts also have the standard :mod:`netsa.script` command
    line options ``--help``, ``--help-expert``, and ``--verbose``.

.. _golem-basic-cli:

Basic Parameters
^^^^^^^^^^^^^^^^

The following golem command line parameters control the filtering of
processing windows, as well as some input and output behavior. These
options affect both repository and query operations.

.. option:: --last-date <date>

        Date specifying the last time bin of interest. The provided date
        will be rounded down to the first date of the processing
        interval in which it resides. Default: most recent

.. option:: --first-date <date>

        Date specifying the first time bin of interest. The provided
        date will be rounded down to the first date of the
        processing interval in which it resides. Default: value of
        :option:`--last-date`

.. option:: --intervals <count>

        Process or query the last *count* intervals (as defined by
        :func:`set_interval` within the script header) of data from the
        current date. This will override any values provided by
        :option:`--first-date` or :option:`--last-date`.

.. option:: --skip-incomplete

        Skip processing intervals that have incomplete input
        requirements (i.e. ignore the date if any source dependencies
        have incomplete results).

.. option:: --overwrite

        Overwrite output results if they already exist.

.. option:: --<loop-select>

        Each template loop that has been defined in the golem script
        (via the :func:`add_loop` function) has an associated
        parameter that allows a comma-separated selection of a subset
        of that loop's values. For example, if a sensor loop was
        defined under the tag ``sensor``, the parameter would be
        ``--sensor`` by default. If grouping was enabled it would be
        ``--sensor-group`` instead.


.. _golem-repository-cli:

Repository Parameters
^^^^^^^^^^^^^^^^^^^^^

Repository parameters allow maintenance of the result repository,
typically via a cron job. They are categorized as 'expert' options,
therefore showing up in ``--help-expert`` rather than ``--help``.

.. option:: --data-load

        Generate and store incomplete or missing analysis results in the
        data repository, skipping those that are complete (unless
        :option:`--overwrite` is given).

.. option:: --data-status

        Show the status of repository processing bins, for the provided
        options. No processing is performed.

.. option:: --data-queue

        List the dates of all pending repository results for the
        provided options. No processing is performed.

.. option:: --data-complete

        List the dates of all completed repository results, for the
        provided options. No processing is performed.

.. option:: --data-inputs

        Show the status of input dependencies from other golem scripts
        or defined templates, for the provided options. Use ``-v`` or
        ``-vv`` for less abbreviated paths. No processing is performed.

.. option:: --data-outputs

        Show the status of repository output results for the provided
        options. Use ``-v`` or ``-vv`` for less abbreviated paths. No
        processing is performed.

.. _golem-query-cli:

Query Parameters
^^^^^^^^^^^^^^^^

Query parameters control how local copies of results are stored, both
when copying from the repository or when performing a fresh analysis.

.. option:: --output-path <path>

        Generate a single query result in the specified output file for
        the given parameters. Also accepts '-' and 'stdout'.

.. option:: --output-select <arg1[,arg2[,...]]>

        For golem scripts that have more than one output defined, limit
        output results to the comma-separated names provided.

.. option:: --output-dir <path>

        Copy query result files in the specified output directory for
        the given parameters. The files will follow the same naming
        scheme as specified for the repository. These names can be
        previewed via the :option:`--show-outputs` option.

.. option:: --show-inputs

        Show the status of input dependencies from other golem scripts
        or defined templates for the provided options. Use ``-v`` or
        ``-vv`` for less abbreviated paths. No processing is performed.

.. option:: --show-outputs

        Show relative output paths that would be generated within
        :option:`--output-dir`, given the options provided. Use ``-v``
        or ``-vv`` for less abbreviated paths. No processing is
        performed.


.. _golem-metadata-functions:

Metadata Functions
------------------

Golem scripts are an extension of :mod:`netsa.script`. As such, golem
scripts offer the same functions as :mod:`netsa.script`. Script
authors are encouraged to use the following
:ref:`metadata functions <netsa-script-metadata-functions>`:

.. autofunction:: set_title(script_title : str)
    :noindex:

.. autofunction:: set_description(script_description : str)
    :noindex:

.. autofunction:: set_version(script_version : str)
    :noindex:

.. autofunction:: set_package_name(script_package_name : str)
    :noindex:

.. autofunction:: set_contact(script_contact : str)
    :noindex:

.. autofunction:: set_authors(script_authors : str list)
    :noindex:

.. autofunction:: add_author(script_author : str)
    :noindex:

Please see :mod:`netsa.script` for additional functions, such as those used to
:ref:`add custom command line parameters <netsa-script-parameter-functions>`.

.. _golem-config-funcs:

Configuration Functions
-----------------------

Golem scripts are configured by calling functions from within a
particular imported module. You can either import
:mod:`netsa.script.golem` directly::

    from netsa.script import golem

Or import as :mod:`netsa.script.golem.script`::

    from netsa.script.golem import script

In either case, the imported module will provide identical
functionality. All functions available within :mod:`netsa.script` are
also available from within :mod:`golem <netsa.script.golem>`, with the
addition of the golem-specific functions and classes. Please consult
the :mod:`netsa.script` documentation for details on functions offered
by that module.

The following functions configure the behavior of golem scripts.

.. autofunction:: set_default_home(path : str [, path : str, ...])

.. autofunction:: set_repository(path : str [, path : str, ...])

.. autofunction:: set_suite_name(name : str)

.. autofunction:: set_name(name : str)

.. autofunction:: set_interval([days : int, minutes : int, hours : int, weeks : int])

.. autofunction:: set_span([days : int, minutes : int, hours : int, weeks : int])

.. autofunction:: set_lag([days : int, minutes : int, hours : int, weeks : int])

.. autofunction:: set_realtime(enable=True)

.. autofunction:: set_tty_safe(enable=True)

.. autofunction:: set_passive_mode(enable=False)

.. autofunction:: add_tag(name : str, value : str or func)

.. autofunction:: add_loop(name : str, value : str list or func [, group_by : str or func, group_name : str, sep=','])

.. autofunction:: add_sensor_loop([name='sensor' : str, sensors : str list or func, group_by : str or func, group_name : str, auto_group=False]) 

.. autofunction:: add_flow_tag(name : str [, flow_class : str, flow_type : str, flowtypes : str, sensors : str, start_date : str, end_date : str, input_pipe : str, xargs : str, filenames : str])

.. autofunction:: add_output_template(name : str, template : str [, scope : int, mime_type : str, description : str])

.. autofunction:: add_input_template(name : str, template : str [, required=True, mime_type : str, descriptions : str])

.. autofunction:: add_golem_input(golem_script : str, name : str [, output_name : str, count : int, cover=False, offset : int, span : timedelta, join_on : str or str list, join : dict, required=True)

.. autofunction:: add_query_handler(name : str, query_handler : func)

.. autofunction:: add_self_input(name : str, output_name : str [, count : int, offset : int, span : timedelta])

.. autofunction:: add_golem_source(path : str)

.. autofunction:: get_script_path() -> str

.. autofunction:: get_script_dir() -> str

.. autofunction:: get_home() -> str

.. autofunction:: get_repository() -> str


.. _golem-param-funcs:

Parameter Functions
-------------------

The following functions are used to enable and modify the standard
command-line parameters available for golem scripts. No command line
parameters are enabled by default, so at least one of these should be
invoked in a typical golem script:

.. autofunction:: add_golem_params([without_params : str list])

.. autofunction:: add_golem_basic_params([without_params : str list])

.. autofunction:: add_golem_query_params([without_params : str list])

.. autofunction:: add_golem_repository_params([without_params : str list])

.. autofunction:: add_golem_param(name : str [, alias : str])

.. autofunction:: modify_golem_param(name : str [, enabled : bool, alias : str, help : str, ...])


.. _golem-processing-funcs:

Processing and Status Functions
-------------------------------

The following functions are intended for use within the :func:`main`
function during processing or examination of status.

.. autofunction:: execute(func)

.. autofunction:: process([golem_view : GolemView])

.. autofunction:: loop([golem_view : GolemView])

.. autofunction:: inputs([golem_view : GolemView])

.. autofunction:: outputs([golem_view : GolemView])

.. autofunction:: is_complete([golem_view : GolemView])

.. autofunction:: script_view()

.. autofunction:: current_view([golem_view : GolemView])


.. _golem-utility-funcs:

Utility Functions
-----------------

The following functions provide some SiLK-specific tools and other
potentially useful features for script authors.

.. autofunction:: get_sensors() -> str list

.. autofunction:: get_sensor_group(sensor : str) -> str

.. autofunction:: get_sensors_by_group([grouper : func, sensors : str list])

.. autofunction:: get_args() -> GolemArgs

Additional Functions
--------------------

Please see the following sections in the :mod:`netsa.script`
documentation for details regarding other functions available within
:mod:`netsa.script.golem`:

    * :ref:`Adding Script Parameters <netsa-script-parameter-functions>`
    * :ref:`netsa-script-verbosity-functions`
    * :ref:`netsa-script-flowdata-functions`
    * :ref:`Adding Additional Output <netsa-script-output-functions>`


.. _golem-templates:

Usage of Tags, Loops, and Templates
-----------------------------------

Golem is a templating engine. Based on a script's configuration, the
processing loop will iterate over time bins (processing intervals) and
the values of any other loops defined for tags in the script. For each
iteration, a dictionary of template tags is produced for use with such
utilities as :mod:`netsa.util.shell`. A typical golem script looks
something like this::

    #!/usr/bin/env python

    from netsa.script import golem
    from netsa.util import shell

    # golem configuration and command line parameter
    # configuration up here

    def main():

        # All 'real' work should happen in this function.
        # Before invoking the processing loop, perhaps do some
        # configuration and prep work

        for tags in golem.process():

            # Set up per-iteration prep work, such as perhaps
            # some temp files

            # maybe modify contents of tags
            tags['temp_file'] = ...

            # set up command templates

            cmd1 = ...
            cmd2 = ...
            ...

            # run the commands
            shell.run_parallel(cmd1, cmd2, vars=tags)

    # pass main function to module for invocation and handling
    golem.execute(main)

The following template tags are automatically available to each
iteration over a golem processing loop:

=========================== ===================================================
Tag Name                    Contents
=========================== ===================================================
``golem_name``              golem script name
``golem_suite``             suite name, if any
``golem_span``              timedelta obj for span
``golem_interval``          timedelta obj for interval
``golem_span_iso``          iso string repr of ``golem_span``
``golem_interval_iso``      iso string repr of ``golem_interval``
--------------------------- ---------------------------------------------------
--------------------------- ---------------------------------------------------
``golem_bin_date``          start datetime for this interval
``golem_bin_year``          interval datetime component 'year'
``golem_bin_month``         interval datetime component 'month'
``golem_bin_day``           interval datetime component 'day'
``golem_bin_hour``          interval datetime component 'hour'
``golem_bin_second``        interval datetime component 'second'
``golem_bin_microsecond``   interval datetime component 'microsecond'
``golem_bin_iso``           iso string repr for ``golem_bin_date``
``golem_bin_basic``         iso basic string repr for ``golem_bin_date``
``golem_bin_silk``          silk string repr for ``golem_bin_date``
--------------------------- ---------------------------------------------------
--------------------------- ---------------------------------------------------
``golem_start_date``        start datetime for this span
``golem_start_year``        start datetime component 'year'
``golem_start_month``       start datetime component 'month'
``golem_start_day``         start datetime component 'day'
``golem_start_hour``        start datetime component 'hour'
``golem_start_second``      start datetime component 'second'
``golem_start_microsecond`` start datetime component 'microsecond'
``golem_start_iso``         iso string repr for ``golem_start_date``
``golem_start_basic``       iso basic string repr for ``golem_start_date``
``golem_start_silk``        silk string repr for ``golem_start_date``
--------------------------- ---------------------------------------------------
--------------------------- ---------------------------------------------------
``golem_end_date``          end datetime for this span
``golem_end_year``          end datetime component 'year'
``golem_end_month``         end datetime component 'month'
``golem_end_day``           end datetime component 'day'
``golem_end_hour``          end datetime component 'hour'
``golem_end_second``        end datetime component 'second'
``golem_end_microsecond``   end datetime component 'microsecond'
``golem_end_iso``           iso string repr for ``golem_end_date``
``golem_end_basic``         iso basic string repr for ``golem_end_date``
``golem_end_silk``          silk string repr for ``golem_end_date``
--------------------------- ---------------------------------------------------
--------------------------- ---------------------------------------------------
``golem_view``              the GolemView object which produced these tags
=========================== ===================================================

For both intervals and spans, time bins are represented by the first
date within that bin. For details on how intervals and spans relate
to one another and format precisions, see
:ref:`golem-interval-span-explained`.

In addition to the standard golem tags defined above, all other tags,
loops, inputs, and outputs defined in the initial script configuration
are available for use in templates. For example, assume a script makes
the following declarations::

    script.add_tag('in_types',  'in,inweb')
    script.add_tag('out_types', 'out,outweb')
    script.add_tag('month', "%(golem_month)02d/%(golem_year)d")
    script.add_sensor_loop()
    script.add_flow_tag('in_flow',  flow_type='in_types')
    script.add_flow_tag('out_flow', flow_type='out_types')
    script.add_output_template('juicy_set', ext='.set',
        description="Target 'juicy' set to generate.",
        mime_type='application/x-silk-ipset')

During each iteration of the processing loop, the tags dictionary will
now include the following additional template entries:

``in_types``
    ::

        "in,inweb"

``out_types``
    ::

        "out,outweb"

``month``
    ::

        "%(golem_month)02d/%(golem_year)d" \
            % (tags['golem_month'], tags['golem_year'])

``sensor``

    the current iteration value of ``script.get_sensors()``

``in_flow``
    ::

        Flow_params(
            start_date = tags['golem_start_date'],
            end_date   = tags['golem_end_date'],
            sensors    = tags['sensor'],
            flow_type  = tags['in_types'])

``out_flow``
    ::

        Flow_params(
            start_date = tags['golem_start_date'],
            end_date   = tags['golem_end_date'],
            sensors    = tags['sensor'],
            flow_type  = tags['out_types'])

``juicy_set``
    ::

        "%(golem_name)s/%(sensor)s/"                             \
        "%(golem_name)s.%(sensor)s.%(golem_start_date_iso)s.set" \
            % (tags['golem_name'], tags['sensor'],               \
               tags['golem_start_date_iso'])

Sometimes, depending on how loops and dependencies are arranged and how
views are being manipulated, an input or output tag for the current view
might contain multiple values (e.g. multiple filenames). In these cases,
the resolved values are bundled into a :class:`GolemArgs` object, which
in turn resolves as a string of paths separated by spaces in the final
command template.


.. _golem-interval-span-explained:

Intervals and Spans Explained
-----------------------------

Intervals and spans represent two different concepts.

An interval is a *processing interval* which represents how frequently
the script is intended to produce results. This is roughly analogous
to how frequently the script might be invoked via a cron job, except
that golem scripts will back-fill missing results upon request and
ignore intervals that appear to already have results present. An
interval is always represented by the *first* timestamp contained
within the interval.

A span, on the other hand, is a *data window* which represents how much
input data the script is expected to consume, whether it be from a SiLK
repository, results from other golem scripts, or other sources.

By default, the span of a golem script is the same as its interval. Not
much surprising happens when the values are equal. They can be
different, however. For example, a script might have a weekly interval
yet consume 4 weeks worth of data for each of those weeks.
Alternatively, a script might run every 4 weeks yet consume only a day's
worth of data, akin to a monthly snapshot.

Intervals are *anchored* relative to a particular epoch. Intervals are
always relative to midnight of the first Monday after January 1st, 1970
which was January 5th. Weeks therefore begin with Monday and multiples
of weeks are always relative to that particular Monday.

Spans are always anchored relative to the *end* of the processing
interval.

In the tags dictionary provided for each processing loop, the
interval is represented by the ``golem_bin_date`` entry and the span
is represented by ``golem_start_date`` and ``golem_end_date``. Given
a 3 week interval and a 4 week span, for example, these values are
aligned like so::

    interval:             bin_date             next_bin_date
                             |                       |
                     |-------|-------|-------|-------|
                     |                               |
    span:       start_date                        end_date

Note that ``end_date`` is not inclusive---its actual value is
the value of ``next_bin_date`` minus one millisecond.

Each of these entries are represented by :class:`datetime.datetime`
objects along with an assortment of formatted string representations. If
both the interval and span have a magnitude of at least a day or more,
the formatted string variations look like so:

========= =================
Variation Format
========= =================
iso       ``YYYY-MM-DD``
basic     ``YYYYMMDD``
silk      ``YYYY/MM/DD``
========= =================

If either the interval or span is less than a day, hours are included:

========= =================
Variation Format
========= =================
iso       ``YYYY-MM-DDTHH``
basic     ``YYYYMMDDTHH``
silk      ``YYYY/MM/DDTHH``
========= =================

In all of the examples covered in this documentation, result templates
are all based on the ``golem_bin_date`` values, i.e. the processing
interval. As the example diagram above illustrates, this may not be
intuitive as to what data is represented in the results. It is up to
script authors to decide how to name their results, but they should
choose a convention, stay consistent with it, and document the decision.


.. _golem-examples:

Examples
--------

.. _golem-trivial-example:

Trivial Example
^^^^^^^^^^^^^^^

The following is a simple example using the Golem API that demonstrates
basic templating. The script monitors an "incoming" directory for daily
text files containing IP addresses and converts them into rwset files. A
line by line explanation follows after the script::

    #!/usr/bin/env python

    from netsa.script.golem import script
    from netsa.util import shell

    script.set_title('Daily IP Sets')
    script.set_description("""
        Convert daily IP lists into rwset files.
    """)
    script.set_version("0.1")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

    script.set_name('daily_set')
    script.set_interval(days=1)
    script.set_span(days=1)

    script.add_golem_params()

    script.set_repository('dat')

    script.add_input_template('daily_txt',
        "/data/incoming/daily.%(golem_bin_iso)s.txt",
        description="Daily IP text files",
        mime_type='text/plain')

    script.add_output_template('daily_set',
        "daily/daily.%(golem_bin_iso)s.set",
        description="Daily IP Sets",
        mime_type='application/x-silk-ipset')

    def main():
        cmd = "rwsetbuild %(daily_txt)s %(daily_set)s"
        for tags in script.process():
            shell.run_parallel(cmd, vars=tags)

    script.execute(main)

Here is the breakdown, line by line::

    from netsa.script.golem import script
    from netsa.util import shell

The first two lines import golem itself as well as
:mod:`netsa.util.shell`, which assists in constructing command line
templates and executing the resulting system commands and pipelines.

Next are some lines for configuring meta information about the script::

    script.set_title('Daily IP Sets')
    script.set_description("""
        Convert daily IP lists into rwset files.
    """)
    script.set_version("0.1")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

Setting the title, description, and other meta-data of the
script is the same as with the regular :mod:`netsa.script`
:ref:`metadata functions <netsa-script-metadata-functions>`.

Now for the golem-specific configuration::

    script.set_name('daily_set')

Though optional, every golem script should have a short name, suitable
for inclusion withing directory paths and filenames. It will be made
available for use in templates as the ``%(golem_name)s`` tag. For groups
of related scripts, the :func:`set_suite_name` function is also
available.

Next, the script must be told the size of its processing intervals and
the size of its data window::

    script.set_interval(days=1)
    script.set_span(days=1)

These two parameters, *interval* and *span*, are the core configuration
parameters for any golem script. The *interval* represents 'how often'
this script is expected to generate results. Typically this would
correspond to the schedule by which the script is invoked via a cron
job. The *span* represents how far back the script will look for input
data. The interval and span do not have to match as they do here---for
example, a script might have a 'daily' interval which processes one week
of data for each of those days.

Next, the script author will almost always want to enable the standard
golem command line parameters::

    script.add_golem_params()

There are three general categories of parameters
(:ref:`basic <golem-basic-cli>`,
:ref:`repository-related <golem-repository-cli>`, and
:ref:`query-related <golem-query-cli>`) which can be separately enabled;
the line above enables all of these.

Next, the script can be told where its results will live::

    script.set_repository('dat')

This line defines the location of the scripts output data repository.
Note that some scripts can be designed for query purposes only and will
therefore not need to define a repository location.

If the path provided is a relative path, it is assumed to be relative to
the script's *home* path. See the :func:`set_default_home` function for
details on how the home path is configured or determined.

The script then defines a template for its input data::

    script.add_input_template('daily_txt',
        "/data/incoming/daily.%(golem_bin_iso)s.txt",
        description="Daily IP text files",
        mime_type='text/plain')

This template assumes that the incoming files will correspond to the
standard ISO-formatted datetime ('YYYY-MM-DD').

Next, an output template is defined::

    script.add_output_template('daily_set',
        "daily/daily.%(golem_bin_iso)s.set",
        description="Daily IP Sets",
        mime_type='application/x-silk-ipset')

For each day of processing, a single rwset file will be generated. Once
again, the standard ISO-formatted date is chosen for the template.

In both the input and output templates, the script uses the tag
``%(golem_bin_iso)s``. This tag is an implicit template tag,
automatically available for use within golem scripts. Other timestamps
are also available, including portions of each timestamp (such as year,
month, and day) for constructing more elaborate templates. For more
details about the rest of these 'implicit' template tags, see
:ref:`golem-templates`.

Now for the actual processing loop::

    def main():
        cmd = "rwsetbuild %(daily_txt)s %(daily_set)s"
        for tags in script.process():
            shell.run_parallel(cmd, vars=tags)

    script.execute(main)

All 'real work' in a golem script should take place in a :func:`main`
function, which is subsequently passed to the :func:`execute` function.
In order for golem scripts to work properly, this must always be the
case. Using the :func:`netsa.script.execute` function instead will not
work for a golem script.

The main entry point for looping across template values is the
:func:`process` function. This construct does a number of things,
including creating output paths and checking for the existence of
required inputs. On each iteration, a dictionary of template tags with
resolved values is provided.

Every golem script has an intrinsic loop over processing intervals. In
this example, our processing interval is once a day. If, via the
command line parameters :option:`--first-date` and
:option:`--last-date`, a window of 1 week had been specified, it would
result in seven main iterations with the tag ``%(golem_bin_iso)s``
corresponding to a string representation of the beginning timestamp of
each daily interval covered in the requested range. Unless told
otherwise, a golem script will skip iterations which have already
generated results.


.. _golem-basic-example:

Basic Example
^^^^^^^^^^^^^

The :ref:`golem-trivial-example` defined an input
template that described daily text files without any explanation about
where or how those files were produced. The following example assumes
that the resulting set of addresses represent "observed internal hosts"
and illustrates how the daily set files might be produced directly from
queries to a SiLK repository. In order to do so, the script relies on a
couple of SiLK command line tools::

    #!/usr/bin/env python

    from netsa.script.golem import script
    from netsa.util import shell
    from netsa.data.format import datetime_silk_day

    script.set_title('SiLK Daily Active Internal Hosts')
    script.set_description("""
        Daily inventory of observed internal host activity.
    """)
    script.set_version("0.1")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

    script.set_name('daily_set')
    script.set_interval(days=1)
    script.set_span(days=1)

    script.add_golem_params()

    script.set_repository('dat')

    script.add_tag('in_types',  'in,inweb')
    script.add_tag('out_types', 'out,outweb')

    script.add_output_template('daily_set',
        "internal/daily/daily.%(golem_bin_iso)s.set",
        description="Daily Internal host activity",
        mime_type='application/x-silk-ipset')

    def main():
        for tags in script.process():
            tags['silk_start'] = datetime_silk_day(tags['golem_start_date'])
            tags['silk_end']   = datetime_silk_day(tags['golem_end_date'])
            tags['out_fifo']   = script.get_temp_dir_pipe_name()
            tags['in_fifo']    = script.get_temp_dir_pipe_name()
            cmd1 = [
                "rwfilter --start-date=%(silk_start)s"
                    " --end-date=%(silk_end)s"
                    " --type=%(in_types)s"
                    " --proto=0-255 --pass=stdout",
                "rwset --sip=%(out_fifo)s"]
            cmd2 = [
                "rwfilter --start-date=%(silk_start)s"
                    " --end-date=%(silk_end)s"
                    " --type=%(out_types)s"
                    " --proto=0-255 --pass=stdout",
                "rwset --dip=%(in_fifo)s"]
            cmd3 = [
                "rwsettool --union --output-path=%(internal_set)s"
                    " %(out_fifo)s %(in_fifo)s"]
            shell.run_parallel(cmd1, cmd2, cmd3, vars=tags)

    script.execute(main)

There are a couple of new techniques to note with this script. Below the
standard meta-configuration are the following lines::

    script.add_tag('in_types',  'in,inweb')
    script.add_tag('out_types', 'out,outweb')

These two statements add a couple of simple template tags. All templates
will now have access to the tags ``%(in_types)s`` and ``%(out_types)s``,
which will resolve to the strings ``'in,inweb'`` and ``'out,outweb'``,
respectively. This is equivalent to manually adding these entries to the
``tags`` dictionary down in the processing loop; predefining them here
is a matter of style preference.

Next comes the main processing loop, which illustrates some more
advanced usage of the :mod:`netsa.util.shell` module::

    def main():
        for tags in script.process():
            tags['silk_start'] = datetime_silk_day(tags['golem_start_date'])
            tags['silk_end']   = datetime_silk_day(tags['golem_end_date'])
            tags['out_fifo']   = script.get_temp_dir_pipe_name()
            tags['in_fifo']    = script.get_temp_dir_pipe_name()

As mentioned earlier, a ``tags`` dictionary is provided for each
processing interval and sensor. In the first four lines within the
processing loop, some additional tags are added to the dictionary. The
first two are reformatted date parameters destined to be used in the
|rwfilter|_ commands. The ``%(golem_start_date)s`` and
``%(golem_end_date)s`` are template tags automatically provided by
golem. The second two lines illustrate how the :mod:`netsa.script`
module can be used to create temporary named pipes so that data can be
fed from one command to another.

These new template additions are then used in the construction of some
command templates used to pull data from the SiLK repository::

            cmd1 = [
                "rwfilter --start-date=%(silk_start)s"
                    " --end-date=%(silk_end)s"
                    " --type=%(in_types)s"
                    " --proto=0-255 --pass=stdout",
                "rwset --sip=%(out_fifo)s"]
            cmd2 = [
                "rwfilter --start-date=%(silk_start)s"
                    " --end-date=%(silk_end)s"
                    " --type=%(out_types)s"
                    " --proto=0-255 --pass=stdout",
                "rwset --dip=%(in_fifo)s"]
            cmd3 = [
                "rwsettool --union --output-path=%(internal_set)s"
                    " %(out_fifo)s %(in_fifo)s"]
            shell.run_parallel(cmd1, cmd2, cmd3, vars=tags)

The first two command templates utilize the template definitions defined
earlier, ``%(in_types)s`` and ``%(out_types)s``, along with the date
ranges associated with each processing loop. Each of these commands
sends its results into its respective named pipe. Finally, the third
command uses |rwsettool|_ to create a union from the output of these
named pipes and creates the rwset file defined by the output template.
All three commands are run in parallel using the facilities of the
:mod:`netsa.util.shell` module.


.. _golem-golem-basic-dependency-example:

Basic Golem Dependency Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :ref:`golem-basic-example` provides a golem
script that produces daily rwset files produced from queries to a SiLK
repository. What if a weekly, rather than daily, summary of IP
addresses is desired? One option would be to adjust the processing
interval and span of the script, thereby pulling an entire week's
worth of data from SiLK in the calls to |rwfilter|_. An alternative is
to utilize the daily sets from the original script as inputs and
construct a weekly summary via the union of the daily sets for the
week in question.

One of the core features of golem scripts is that they can be assigned
as inputs to one other. Details such as how often the inputs are
produced, the naming scheme, and synchronization across time bins is
sorted out automatically by the golem scripts involved. Assume that the
script in the :ref:`golem-basic-example` is called
``daily_set.py``. The following example illustrates how to configure the
dependency on this external script::

    #!/usr/bin/env python

    from netsa.script.golem import script
    from netsa.util import shell

    script.set_title('Weekly Active Internal Host Set')
    script.set_description("""
        Aggregate daily internal activity sets over the last week.
    """)
    script.set_version("0.1")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

    script.set_name('weekly_set')
    script.set_interval(weeks=1)
    script.set_span(weeks=1)

    script.add_golem_params()

    script.set_repository('dat')

    script.add_golem_input('daily_set.py', 'daily_set', cover=True)

    script.add_output_template('weekly_set',
        "weekly/weekly.%(golem_bin_iso)s.set",
        description="Aggregated weekly sets.",
        mime_type='application/x-silk-ipset')

    def main():
        cmd = "rwsettool --union --output-path=%(weekly_set)s %(daily_set)s"
        for tags in script.process():
            shell.run_parallel(cmd, vars=tags)

    script.execute(main)

The first thing to note is that this script has a different interval
and span::

    script.set_interval(weeks=1)
    script.set_span(weeks=1)

The script will produce weekly results and will expect to consume a week
of data while doing so.

The input template is now defined as a dependency on the external
script like so::

    script.add_golem_input('daily_set.py', 'daily_set', cover=True)

The first argument is the name of the external script. For details on
how relative paths to scripts are resolved, see the
:func:`add_golem_source` function.

The second argument is the output as defined within that external
script. Golem scripts can have multiple outputs, so the specific output
desired must be explicitly defined.

The third argument, the *cover* parameter, controls how this external
output is synchronized across local processing intervals---in this
case the processing interval of 1 week will be 'covered' by 7 days
worth of inputs.

After the configuration of the weekly output template comes the main
processing loop::

    def main():
        cmd = "rwsettool --union --output-path=%(weekly_set)s %(daily_set)s"
        for tags in script.process():
            shell.run_parallel(cmd, vars=tags)

    script.execute(main)

The output tag ``%(weekly_set)s`` is based on the ``%(golem_bin_iso)s``
timestamp, which in this case ends up being the date of the first Monday
of each week in question. The ``%(daily_set)s`` tags represents 7 days
of results---this will resolve to 7 individual filenames separated by
whitespace in the eventual call to |rwsettool|_.


.. _golem-loop-interval-span-example:

Loop, Interval and Span Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Golem scripts can define additional loops addition to the intrinsic loop
over processing intervals. The following script is a modification of the
script in the :ref:`golem-basic-example` which builds
daily inventories by directly querying the SiLK repository.
Rather than construct a monolithic inventory across all sensors, this
version will construct inventories on a per-sensor basis by defining a
template loop over a list of sensor names. Finally, it will illustrate
the difference between intervals and spans by using a less frequent
interval and a larger data window::

    #!/usr/bin/env python

    from netsa.script.golem import script
    from netsa.util import shell
    from netsa.data.format import datetime_silk_day

    script.set_title('Active Internal Hosts')
    script.set_description("""
        Per-sensor inventory of observed internal host activity over a
        four week window of observation, generated every three weeks.
    """)
    script.set_version("0.1")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

    script.set_name('internal')
    script.set_interval(weeks=3)
    script.set_span(weeks=4)

    script.add_golem_params()

    script.set_repository('dat')

    script.add_tag('in_types',  'in,inweb')
    script.add_tag('out_types', 'out,outweb')

    script.add_loop('sensor', ["S0", "S1", "S2", "S3"])

    script.add_output_template('internal_set',
        "internal/internal.%(sensor)s.%(golem_bin_iso)s.set",
        description="Internal host activity",
        mime_type='application/x-silk-ipset')

    def main():
        for tags in script.process():
            tags['silk_start'] = datetime_silk_day(tags['golem_start_date'])
            tags['silk_end']   = datetime_silk_day(tags['golem_end_date'])
            tags['out_fifo']   = script.get_temp_dir_pipe_name()
            tags['in_fifo']    = script.get_temp_dir_pipe_name()
            cmd1 = [
                "rwfilter --start-date=%(silk_start)s"
                    " --end-date=%(silk_end)s"
                    " --type=%(in_types)s"
                    " --sensors=%(sensor)s"
                    " --proto=0-255 --pass=stdout",
                "rwset --sip=%(out_fifo)s"]
            cmd2 = [
                "rwfilter --start-date=%(silk_start)s"
                    " --end-date=%(silk_end)s"
                    " --type=%(out_types)s"
                    " --sensors=%(sensor)s"
                    " --proto=0-255 --pass=stdout",
                "rwset --dip=%(in_fifo)s"]
            cmd3 = [
                "rwsettool --union --output-path=%(internal_set)s"
                    " %(out_fifo)s %(in_fifo)s"]
            shell.run_parallel(cmd1, cmd2, cmd3, vars=tags)

    script.execute(main)

The first thing to note is the new interval and span definitions::

    script.set_interval(weeks=3)
    script.set_span(weeks=4)

The script will produce results every 3 weeks and will expect to consume
4 weeks of data while doing so. This is the first example in which the
interval and span are not equal. For more detail on the implications of
this see :ref:`golem-interval-span-explained`.

Further down in the script is the new loop definition::

    script.add_loop('sensor', ["S0", "S1", "S2", "S3"])

With the addition of this line, for each 3-week processing interval, the
script will return a separate ``tags`` dictionary for each sensor,
setting the value of the ``sensor`` entry accordingly. Logically
speaking this is equivalent to having two embedded 'for' loops, one for
intervals and one for sensors.

This newly defined ``%(sensor)s`` tag is then used in the modified
definition of the output template::

    script.add_output_template('internal_set',
        "internal/internal.%(sensor)s.%(golem_bin_iso)s.set",
        description="Internal host activity",
        mime_type='application/x-silk-ipset')

Next comes the main processing loop. Note that it is *identical* to the
processing loop in the earlier incarnation of the script. The interval
and span were changed, an extra loop was introduced, and the output
template was modified, but the essential processing logic remains
unchanged.


.. _golem-silk-integration-example:

SiLK Integration Example
^^^^^^^^^^^^^^^^^^^^^^^^

The Golem API and :ref:`NetSA Scripting Framework <netsa-script>`
include a number of convenience functions and classes for interacting
with a SiLK repository. The
:ref:`golem-loop-interval-span-example`
can be simplified using a few of these features as illustrated below::

    #!/usr/bin/env python

    from netsa.script.golem import script
    from netsa.util import shell
    from netsa.data.format import datetime_silk_day

    script.set_title('Active Internal Hosts')
    script.set_description("""
        Per-sensor inventory of observed internal host activity over a
        four week window of observation, generated every three weeks.
    """)
    script.set_version("0.2")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

    script.set_name('internal')
    script.set_interval(weeks=3)
    script.set_span(weeks=4)

    script.add_golem_params()

    script.set_repository('dat')

    script.add_tag('in_types',  'in,inweb')
    script.add_tag('out_types', 'out,outweb')

    script.add_sensor_loop()

    script.add_flow_tag('in_flow',  flow_type='in_types')
    script.add_flow_tag('out_flow', flow_type='out_types')

    script.add_output_template('internal_set',
        "internal/internal.%(sensor)s.%(golem_bin_iso)s.set",
        description="Internal host activity",
        mime_type='application/x-silk-ipset')

    def main():
        for tags in script.process():
            tags['out_fifo'] = script.get_temp_dir_pipe_name()
            tags['in_fifo']  = script.get_temp_dir_pipe_name()
            cmd1 = [
                "rwfilter %(out_flow)s --proto=0-255 --pass=stdout",
                "rwset --sip=%(out_fifo)s"]
            cmd2 = [
                "rwfilter %(in_flow)s --proto=0-255 --pass=stdout",
                "rwset --dip=%(in_fifo)s"]
            cmd3 = [
                "rwsettool --union --output-path=%(internal_set)s"
                    " %(out_fifo)s %(in_fifo)s"]
            shell.run_parallel(cmd1, cmd2, cmd3, vars=tags)

    script.execute(main)

The first difference to note is that rather than manually defining a
loop over sensors, the following shorthand is used::

    script.add_sensor_loop()

This line sets up a loop on the template tag ``sensor`` as before, but
the list of sensors is automatically determined from the SiLK repository
itself (see the |mapsid|_ command). The script also remembers that this
particular loop involves sensors.

The next modification to note is the definition of two special
SiLK-related compound tags::

    script.add_flow_tag('in_flow',  flow_type='in_types')
    script.add_flow_tag('out_flow', flow_type='out_types')

These statements create template entries bound to
:class:`netsa.script.Flow_params` objects which serve to simplify the
construction of |rwfilter|_ command line templates.

Each call to :func:`add_flow_tag` implicitly binds the
``start_date`` and ``end_date`` object attributes to the value of the
template tags ``golem_start_date`` and ``golem_end_date``. Given that
a sensor-specific loop was declared earlier, the function calls will
also bind the ``sensors`` attribute to the value of the ``sensor``
tag for each loop.

Additional tags can be bound to :class:`netsa.script.Flow_params`
attributes using keyword arguments. In this example, the ``in_types``
and ``out_types`` tags defined earlier in the script are bound to the
``flow_type`` attribute of each object.

The rest of the script proceeds as before, except that in the
processing loop the |rwfilter|_ command templates are far more
compact::

            cmd1 = [
                "rwfilter %(out_flow)s --proto=0-255 --pass=stdout",
                "rwset --sip=%(out_fifo)s"]
            cmd2 = [
                "rwfilter %(in_flow)s --proto=0-255 --pass=stdout",
                "rwset --dip=%(in_fifo)s"]

The ``%(out_flow)s`` and ``%(in_flow)s`` tags will each expand into four
parameters in the eventual command string.


.. _golem-synchro-example:

Synchronization Example
^^^^^^^^^^^^^^^^^^^^^^^

The following example will build a daily inventory of internal addresses
that exhibit activity on source port 25. In order to limit the pool of
addresses under consideration, it will utilize the internal inventory
results generated by the
:ref:`golem-silk-integration-example`.
Furthermore, it will utilize some additional SiLK-related tools in order
to organize results into 'sensor groups' rather than under individual
sensors. The following assumes that the prior inventory script is called
``internal.py``::

    #!/usr/bin/env python

    from netsa.script.golem import script
    from netsa.util import shell

    script.set_title('Daily Internal Port 25 Activity')
    script.set_description("""
        Daily per-sensor-group inventory of observed internal host
        activity on port 25.
    """)
    script.set_version("0.1")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

    script.set_name('p25')
    script.set_interval(days=1)
    script.set_span(days=1)

    script.add_golem_params()

    script.set_repository('dat')

    script.add_sensor_loop(auto_group=True)

    script.add_tag('out_type', 'out,outweb')
    script.add_flow_tag('out_flow', flow_type='out_type')

    script.add_golem_input('internal.py', 'internal_set', join_on='sensor')

    script.add_output_template('p25_set',
        "p25/p25.%(sensor_group)s.%(golem_bin_iso)s.set",
        description="Daily IP set for internal port 25 activity",
        mime_type='application/x-silk-ipset')

    def main():
        for tags in script.process():
            tags['in_fifo'] = script.get_temp_dir_pipe_name()
            cmd1 = [
                "rwsettool --union"
                    " --output-path=%(in_fifo)s
                    " %(internal_set)s"]
            cmd2 = [
                "rwfilter %(out_flow)s"
                    " --proto=6"
                    " --sport=25"
                    " --packets=2-"
                    " --sipset=%(in_fifo)s"
                    " --pass=stdout",
                "rwset --sip-set=%(p25_set)s"]
            shell.run_parallel(cmd1, cmd2, vars=tags)

    script.execute(main)

First, the script is configured to generate once per day using a span
of one day::

    script.set_interval(days=1)
    script.set_span(days=1)

Next, the sensor loop is configured::

    script.add_sensor_loop(auto_group=True)

This invocation of :func:`add_sensor_loop` uses a new named parameter,
*auto_group*, which loops over *groups* of related sensors rather than
individual sensors. Normally, a single template tag ``sensor`` is added.
When grouping is enabled for a sensor loop another tag ``sensor_group``
is added in addition to the ``sensor`` tag. So, for example, if there
are three sensors in a group labeled 'LAB0', 'LAB1', and 'LAB2', these
two template tags would expand into strings like so:

==================== ==================
Tag                  Value
==================== ==================
``%(sensor)s``       ``LAB0,LAB1,LAB2``
``%(sensor_group)s`` ``LAB``
==================== ==================

See the :func:`add_loop` function for the details of how the above
features work for generic, non-sensor-related, loops.

Next the script sets up the input dependency from the script in the
:ref:`golem-basic-example` called
``internal.py``::

    script.add_golem_input('internal.py', 'internal_set', join_on='sensor')

When golem scripts use other golem script results as inputs, they are
automatically synchronized across processing intervals. The basic rule
is to synchronize on the latest external interval containing an end-point
less than or equal to the end-point of the local interval under
consideration.

The synchronization of any loops other than intervals must be explicitly
configured. In this case, the *join_on* parameter is used to indicate
that the external sensor loop and local sensor loop should align on each
value of the ``sensor`` tag. This synchronization happens per-sensor and
does not affect the eventual sensor grouping behavior.

Next, the output template is defined. Note the use of the ``sensor_group``
tag rather than ``sensor``::

    script.add_output_template('p25_set',
        "p25/p25.%(sensor_group)s.%(golem_bin_iso)s.set",
        description="Daily IP set for internal port 25 activity",
        mime_type='application/x-silk-ipset')

Followed by the processing loop::

    def main():
        for tags in script.process():
            tags['in_fifo'] = script.get_temp_dir_pipe_name()
            cmd1 = [
                "rwsettool --union"
                    " --output-path=%(in_fifo)s
                    " %(internal_set)s"]
            cmd2 = [
                "rwfilter %(out_flow)s"
                    " --proto=6"
                    " --sport=25"
                    " --packets=2-"
                    " --sipset=%(in_fifo)s"
                    " --pass=stdout",
                "rwset --sip-set=%(p25_set)s"]
            shell.run_parallel(cmd1, cmd2, vars=tags)

    script.execute(main)

Since sensors are being grouped, the ``%(internal_set)s`` tag for each
loop potentially represents multiple input files, one for each
individual sensor. The first command defines a template for |rwsettool|_
that sends a union of these per-sensor sets into the named pipe. The
second command pipeline uses this merged set to filter the initial flows
being examined by the |rwfilter|_ query.

When invoked on a regular basis, this script will produce a daily subset
of the most recent per-sensor-group inventory for those internal IP
addresses that have exhibited activity on source port 25.


Self Dependency Example
^^^^^^^^^^^^^^^^^^^^^^^

The :ref:`golem-synchro-example` demonstrates how to
configure an input dependency on the results of another golem script. It
is also possible to configure dependencies on a golem script's *own*
past results.

Recall that the :ref:`golem-silk-integration-example` is
configured with a 3-week interval and 4-week span. The 3-week interval
was chosen due to the resource-intensive query across 4 weeks of data.
Whereas this does produce internal inventories, the information is
potentially less accurate over time (particularly during the final few
days of the 3-week processing interval).

The inventory script can be modified to consume its own outputs and
produce *delta encoded* results on a daily basis::


    #!/usr/bin/env python

    from netsa.script.golem import script
    from netsa.util import shell
    from netsa.data.format import datetime_silk_day

    script.set_title('Active Internal Hosts')
    script.set_description("""
        Daily per-sensor inventory of observed internal host activity,
        delta-encoded using the prior four weeks of results.
    """)
    script.set_version("0.3")
    script.set_contact("H.P. Fnord <fnord@example.com>")
    script.set_authors(["H.P. Fnord <fnord@example.com>"])

    script.set_name('internal')
    script.set_interval(days=1)
    script.set_span(days=1)

    script.add_golem_params()

    script.set_repository('dat')

    script.add_tag('in_types',  'in,inweb')
    script.add_tag('out_types', 'out,outweb')

    script.add_sensor_loop()

    script.add_flow_tag('in_flow',  flow_type='in_types')
    script.add_flow_tag('out_flow', flow_type='out_types')

    script.add_output_template('internal_set',
        "internal/internal.delta.%(sensor)s.%(golem_bin_iso)s.set",
        description="Delta set of internal host activity",
        mime_type='application/x-silk-ipset',
        scope=28)

    script.add_self_input('prior_set', 'internal_set', offset=0)

    def main():
        for tags in script.process():
            tags['out_fifo'] = script.get_temp_dir_pipe_name()
            tags['in_fifo']  = script.get_temp_dir_pipe_name()
            cmds = []
            cmds.append([
                "rwfilter %(out_flow)s --proto=0-255 --pass=stdout",
                "rwset --sip=%(out_fifo)s"])
            cmds.append([
                "rwfilter %(in_flow)s --proto=0-255 --pass=stdout",
                "rwset --dip=%(in_fifo)s"])
            cmds.append([
                "rwsettool --union --output-path=%(current_set)s"
                    " %(out_fifo)s %(in_fifo)s"])
            if tags['prior_set']:
                tags['current_set'] = script.get_temp_dir_pipe_name()
                cmds.append([
                  "rwsettool --difference"
                      " --output-path=%(internal_set)s"
                      " %(current_out)s %(prior_set)s"])
            else:
                tags['current_set'] = tags['internal_set']

            shell.run_parallel(vars=tags, *cmds)

    script.execute(main)

The goal is to generate a viable internal inventory on a daily basis
with minimal overhead. The naive approach would be to define and
interval of 1 day and leave the span as 4 weeks. This would pull 4 weeks
of data *every single day* and construct a full inventory for that day.
This is inefficient in terms of processing and storage. Instead,
this script introduces a new concept called *scope*. Scope is used to indicate situations where a single interval
of processing does not represent a complete analysis result.

First, the basics are configured::

    script.set_interval(days=1)
    script.set_span(days=1)

The script produces a daily result and expects to consume a single day's
worth of 'regular' data while doing so. Next, the script must define its
daily output template::

    script.add_output_template('internal_set',
        "internal/internal.delta.%(sensor)s.%(golem_bin_iso)s.set",
        description="Delta set of internal host activity",
        mime_type='application/x-silk-ipset',
        scope=28)

This declaration shows the use of the new ``scope`` parameter. The scope
indicates the number of processing interval outputs required to
represent a *complete* result. Here, the scope is defined as 28
intervals (days in this case).

Now when other golem scripts use this script output as an input
dependency, they will see 4 weeks of files relative to each day of
interest. This also applies in cases where a golem script asks *itself*
for prior results. An example of this is shown next::

    script.add_self_input('prior_set', 'internal_set', offset=0)

This self-referential input dependency maps ``internal_set`` to a new
template tag called ``prior_set``.

By default, self-referential inputs have an offset of ``-1`` which
excludes the results for the current processing interval. In cases
such as this, where the goal is delta-encoding, the offset should be
``0``. (The daily result being generated for the current day represents
addresses not present in the last 27 days).

Next is the main processing loop::

    def main():
        for tags in script.process():
            tags['out_fifo'] = script.get_temp_dir_pipe_name()
            tags['in_fifo']  = script.get_temp_dir_pipe_name()
            cmds = []
            cmds.append([
                "rwfilter %(out_flow)s --proto=0-255 --pass=stdout",
                "rwset --sip=%(out_fifo)s"])
            cmds.append([
                "rwfilter %(in_flow)s --proto=0-255 --pass=stdout",
                "rwset --dip=%(in_fifo)s"])
            cmds.append([
                "rwsettool --union --output-path=%(current_set)s"
                    " %(out_fifo)s %(in_fifo)s"])
            if tags['prior_set']:
                tags['current_set'] = script.get_temp_dir_pipe_name()
                cmds.append([
                  "rwsettool --difference"
                      " --output-path=%(internal_set)s"
                      " %(current_out)s %(prior_set)s"])
            else:
                tags['current_set'] = tags['internal_set']

            shell.run_parallel(vars=tags, *cmds)

    script.execute(main)

The core logic is similar to the earlier version. A new template tag,
``current_set`` is added to the ``tags`` dictionary for each iteration.
Depending on circumstances, the value of this tag is set to one of two
things: If no prior results are available, a regular rwset is
constructed just as it was before. If prior results are available,
however, the difference is taken between the current day's results and
the union of up to 27 days of prior results.

This technique allows the reconstruction of an accurate 4-week internal
inventory, for any particular day, by taking the union over the 28 days
ending on that day.

Having made these changes, what now needs to be changed in the script
from the :ref:`golem-synchro-example` which
depends on these internal sets as input?

Not a single thing.

The script in the :ref:`golem-synchro-example` is already performing a
union with |rwsettool|_ on the tag ``%(internal_set)s`` in order to
merge data across sensors into sensor groups. Due to the ``scope``
declaration, the ``%(internal_set)s`` tag will now also include paths to
the files for each of the 28 days required to reconstruct results.


.. _golem-classes:

Classes
-------

GolemView
^^^^^^^^^

.. autoclass:: GolemView(golem : Golem [, first_date : datetime, last_date : datetime])

    .. autoattribute:: golem
    .. autoattribute:: first_bin
    .. autoattribute:: last_bin
    .. autoattribute:: start_date
    .. autoattribute:: end_date

    .. automethod:: using([golem : Golem, first_date : datetime, last_date : datetime])

    .. automethod:: bin_dates() -> datetime iter

    .. automethod:: by_bin_date() -> GolemView iter

    .. automethod:: group_by(key : str [, ...]) -> (str tuple, GolemView) iter

    .. automethod:: by_key(key : str) -> (str, GolemView) iter

    .. automethod:: product() -> GolemView iter

    .. automethod:: bin_count() -> int

    .. automethod:: loop_count() -> int

    .. automethod:: sync_to(other : GolemView [, count : int, offset : int, cover=False) -> GolemView

    .. automethod:: loop() -> GolemTags

    .. automethod:: outputs() -> GolemOutputs

    .. automethod:: inputs() -> GolemInputs

    .. automethod:: __len__() -> int

    .. automethod:: __iter__() -> GolemView iter


GolemTags
^^^^^^^^^
.. autoclass:: GolemTags(golem : Golem [, first_date : datetime, last_date : datetime])
    :show-inheritance:

    As well as the methods and attributes of :class:`GolemView`, the
    following additional and overridden methods are available:

    .. automethod:: tags() -> dict

    .. method:: __iter__() -> dict iter


GolemOutputs
^^^^^^^^^^^^

.. autoclass:: GolemOutputs(golem : Golem [, first_date : datetime, last_date : datetime])
    :show-inheritance:

    As well as the methods and attributes of :class:`GolemView`, the
    following additional and overridden methods are available:

    .. automethod:: expand() -> GolemArgs

    .. automethod:: __len__() -> int

    .. automethod:: __iter__() -> str iter


GolemInputs
^^^^^^^^^^^

.. autoclass:: GolemInputs(golem : Golem [, first_date : datetime, last_date : datetime])
    :show-inheritance:

    As well as the methods and attributes of :class:`GolemView`, the
    following additional and overridden methods are available:

    .. automethod:: expand() -> GolemArgs

    .. automethod:: members() -> GolemOutputs iter

    .. automethod:: __len__() -> int

    .. automethod:: __iter__() -> str iter

GolemArgs
^^^^^^^^^

.. autoclass:: GolemArgs(item : str or str iter [, ...])

GolemProcess
^^^^^^^^^^^^

.. autoclass:: GolemProcess(gview : GolemView [,  overwrite_outputs=False, skip_complete=True, keep_empty_outputs=False, skip_missing_inputs=False, optional_inputs : dict])

    Most methods and attributes available from the :class:`GolemTags`
    class are available through this class as well, with some behavioral
    changes as noted below. The following methods are in addition to
    those available from :class:`GolemTags`:

    .. automethod:: is_complete() -> bool

    .. automethod:: status(label : str) -> (str, bool) iter

    The following methods have slightly different behavior than
    that of :class:`GolemTags`:

    .. automethod:: using([gview : GolemView, overwrite_outputs=False, skip_complete=True, keep_empty_outputs=False, skip_missing_inputs=False, create_slots=True, optional_inputs : dict])

    .. automethod:: product() -> GolemProcess iter

    .. automethod:: by_bin_date() -> GolemProcess iter

    .. automethod:: group_by(key : str [, ...]) -> (str tuple, GolemProcess) iter

    .. automethod:: by_key(str) -> GolemProcess iter

    .. automethod:: __iter__() -> dict iter


.. |rwfilter| replace:: ``rwfilter``
.. _rwfilter: http://tools.netsa.cert.org/silk/rwfilter.html

.. |rwsettool| replace:: ``rwsettool``
.. _rwsettool: http://tools.netsa.cert.org/silk/rwsettool.html

.. |mapsid| replace:: ``mapsid``
.. _mapsid: http://tools.netsa.cert.org/silk/mapsid.html
