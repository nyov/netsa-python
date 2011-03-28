Changes
=======

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
