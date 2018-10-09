Changes
=======

Version 1.4.4 - 2014-01-29
--------------------------

 * Fixed error in netsa.script that caused a default for file params to
   be checked for before command-line arguments were handled.

 * Fixed default regex for label params in netsa.script.

Version 1.4.3 - 2013-02-18
--------------------------

 * Added server-side cursor support to netsa.sql's psycopg2 driver, so
   that results are streamed back instead of fetched all together.

 * Fixed an exception caused by using num_prefix on values <= 1e-21.

 * Remove netsa_silk support version SiLK versions older than SiLK 3.

 * Provide unnamed arguments to scripts via
   netsa.script.get_extra_args().

 * Better support for finding non-standard Sphinx installs.

Version 1.4.2 - 2012-12-07
--------------------------

 * Fix problem where netsa.dist would not install manpages unless the
   distribution also had install_data.

Version 1.4.1 - 2012-11-09
--------------------------

 * Fail-on-use dummy IPv6Addr added to netsa_silk, so that the symbol
   may still be imported even when IPv6 support is not provided.

 * Minor bug fixes to prevent setup.py from requiring sphinx, and to
   improve documentation generation on projects with different needs.

Version 1.4 - 2011-09-30
------------------------

 * NOTE: Version 1.4 of NetSA Python is the last version that
   will support Python 2.4.  Future major versions of NetSA Python
   will require Python 2.6 or greater.

 * Added new netsa_silk module, which provides a bridge between
   netsa-python and PySiLK.  When PySiLK is available, it uses PySiLK
   to provide a fast C implementation of IP address and related
   functionality.  When PySiLK is not available, a pure Python
   implementation from netsa-python is used instead.

 * Added new netsa.script.golem script automation framework, for
   building scripts to maintain large time-based data sets (among
   other things.)

 * Added regex_help argument to netsa.script.add_text_param and
   add_label_param, to support providing a more useful error message
   when the regex doesn't match the input.

 * Added heapq.merge and os.path.relpath to netsa.util.compat.

 * Replaced all temporary file code with new functions in the
   netsa.files module, to avoid duplication of effort.  Similar
   functions in other locations have been deprecated and are now
   implemented using this version.

 * Replaced PID locking code with new functions in the netsa.files
   module, to avoid duplication of effort.

 * Improved netsa.data.nice's results, particularly for time ticks.

 * Added a large number of new tests to improve compatibility testing
   for different versions of Python in the future.

 * Moved the netsa.script.get_temp_dir... functions into netsa.files,
   with slight renaming.  The old functions are still available but
   deprecated.

 * Deprecated netsa.files.DirLocker, netsa.files.LocalTmpDir, and
   netsa.tools.service.  See the new functions
   netsa.files.acquire_pidfile_lock, examine_pidfile_lock, and
   release_pidfile_lock.

 * Deprecated netsa.files.datefiles.

 * Added documentation for the netsa.dist module, even though it is
   primarily for internal use.

 * Fixed bug involving SIGPIPE handling in netsa.util.shell.

 * Fixed bug that prevented netsa.logging from importing correctly
   under Python 2.7.

Version 1.3 - 2011-03-28
------------------------

 * Switched to new common installation mechanism (based on distutils)

 * Improved error handling in netsa.util.script

 * Added new function netsa.script.get_temp_dir_pipe_name()

 * Added timedelta support to netsa.data.times

 * Added new netsa.util.compat to activity "compatibility features"

Version 1.2 - 2011-01-12
------------------------

 * Added support for Oracle in netsa.sql via cx_Oracle

 * Added support for multi-paragraph help text in netsa.script


Version 1.1 - 2010-10-04
------------------------

 * Added experimental DB connection pooling to netsa.sql

 * Made netsa.script flow_params --help work when site config file is
   missing.

 * Added netsa.util.shell.run_collect_files

 * Fixed a bug with netsa.script.Flow_params.using

 * Fixed a bug involving netsa.script missing metadata causing crashes

Version 1.0 - 2010-09-14
------------------------

 * Added netsa.util.clitest module to support CLI tool testing.

 * Added PyGreSQL support to netsa.sql.

 * Fixed a bug in netsa.sql db_query parsing code.

 * Fixed a bug in netsa.sql database URI parsing code.

 * Fixed bugs in netsa.data.nice nice_time_ticks.

Version 0.9 - 2010-01-19
------------------------

 * First public release.
