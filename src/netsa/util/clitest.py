#  Copyright (C) 2010 by Carnegie Mellon University.
#  
#  @OPENSOURCE_HEADER_START@
#  Use of the Network Situational Awareness Python support library and
#  related source code is subject to the terms of the following licenses:
#  
#  GNU Public License (GPL) Rights pursuant to Version 2, June 1991
#  Government Purpose License Rights (GPLR) pursuant to DFARS 252.225-7013
#  
#  NO WARRANTY
#  
#  ANY INFORMATION, MATERIALS, SERVICES, INTELLECTUAL PROPERTY OR OTHER 
#  PROPERTY OR RIGHTS GRANTED OR PROVIDED BY CARNEGIE MELLON UNIVERSITY 
#  PURSUANT TO THIS LICENSE (HEREINAFTER THE "DELIVERABLES") ARE ON AN 
#  "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY 
#  KIND, EITHER EXPRESS OR IMPLIED AS TO ANY MATTER INCLUDING, BUT NOT 
#  LIMITED TO, WARRANTY OF FITNESS FOR A PARTICULAR PURPOSE, 
#  MERCHANTABILITY, INFORMATIONAL CONTENT, NONINFRINGEMENT, OR ERROR-FREE 
#  OPERATION. CARNEGIE MELLON UNIVERSITY SHALL NOT BE LIABLE FOR INDIRECT, 
#  SPECIAL OR CONSEQUENTIAL DAMAGES, SUCH AS LOSS OF PROFITS OR INABILITY 
#  TO USE SAID INTELLECTUAL PROPERTY, UNDER THIS LICENSE, REGARDLESS OF 
#  WHETHER SUCH PARTY WAS AWARE OF THE POSSIBILITY OF SUCH DAMAGES. 
#  LICENSEE AGREES THAT IT WILL NOT MAKE ANY WARRANTY ON BEHALF OF 
#  CARNEGIE MELLON UNIVERSITY, EXPRESS OR IMPLIED, TO ANY PERSON 
#  CONCERNING THE APPLICATION OF OR THE RESULTS TO BE OBTAINED WITH THE 
#  DELIVERABLES UNDER THIS LICENSE.
#  
#  Licensee hereby agrees to defend, indemnify, and hold harmless Carnegie 
#  Mellon University, its trustees, officers, employees, and agents from 
#  all claims or demands made against them (and any related losses, 
#  expenses, or attorney's fees) arising out of, or relating to Licensee's 
#  and/or its sub licensees' negligent use or willful misuse of or 
#  negligent conduct or willful misconduct regarding the Software, 
#  facilities, or other rights or assistance granted by Carnegie Mellon 
#  University under this License, including, but not limited to, any 
#  claims of product liability, personal injury, death, damage to 
#  property, or violation of any laws or regulations.
#  
#  Carnegie Mellon University Software Engineering Institute authored 
#  documents are sponsored by the U.S. Department of Defense under 
#  Contract FA8721-05-C-0003. Carnegie Mellon University retains 
#  copyrights in all material produced under this contract. The U.S. 
#  Government retains a non-exclusive, royalty-free license to publish or 
#  reproduce these documents, or allow others to do so, for U.S. 
#  Government purposes only pursuant to the copyright license under the 
#  contract clause at 252.227.7013.
#  @OPENSOURCE_HEADER_END@

"""
Overview
--------

The :mod:`netsa.util.clitest` module provides an API for driving
automated tests of command-line applications. It doesn't do the work
of a test framekwork; for that, use a framework library such as
unittest or functest.

Enough of :mod:`netsa.util.clitest` has been implemented to fulfill a
minimal set of requirements. Additional features will be added as
necessary to support more complex testing.

This module is influenced by http://pythonpaste.org/scripttest/.

A usage example:

.. sourcecode:: python

    from clitest import *
    env = Environment("./test-output")
    # Run the command
    result = env.run("ryscatterplot --help")
    assert(result.success())
    assert(result.stdout() == "whatever the help output is")
    assert(result.stderr() == "")
    # Clean up whatever detritus the command left
    env.cleanup()
"""

from __future__ import division
import os
import sys
import tempfile
import StringIO

import shell

def dbgmsg(debug, message):
    if debug:
        print >>sys.stderr, message

class TestingException(Exception):
    """Class of exceptions raised by the :mod:`clitest` module."""
    pass


def format_envars(envars, delim=" "):
    return delim.join("%s=%s" % (k,v) for k,v in sorted(envars.items()))

class Result(object):
    """
    Contains information on a command's exit status and output.
    """
    def __init__(self, command, envars,
                 exit_codes, stdout, stderr, debug=False):
        self._command = command
        self._envars = envars
        self._exit_code = exit_codes[0][0]
        self._stdout = stdout
        self._stderr = stderr
        self._should_debug = debug
    def _debug(self, message):
        return dbgmsg(self._should_debug, "ENV: %s" % message)
    def success(self):
        """
        Returns ``True`` if the exit code of the process was 0. This
        usually, but not always, indicates that the process ran
        successfully. Know Your Tool before relying on this function.
        """
        return self._exit_code == 0
    def exited(self, code=None):
        """
        Returns ``True`` if the process exited with the specified exit
        code. If the exit code is ``None`` or unsupplied, returns
        ``True`` if the process terminated normally (e.g., not on a
        signal).
        """
        if os.WIFEXITED(self._exit_code):
            if code is None:
                return True
            if os.WEXITSTATUS(self._exit_code) == code:
                return True
            return False
        return False
    def exit_status(self):
        """
        Returns the exit status of the process, if the process exited
        normally (e.g., was not terminated on a signal). Otherwise,
        this function returns ``None``.
        """
        if os.WIFEXITED(self._exit_code):
            return os.WEXITSTATUS(self._exit_code)
        return None
    def signal(self):
        """
        Returns the signal on which the process terminated, if the
        process terminated on a signal. Otherwise, this function
        returns ``None``.
        """
        if os.WIFSIGNALED(self._exit_code):
            return os.WTERMSIG(self._exit_code)
        return None
    def signaled(self, signal=None):
        """
        Returns ``True`` if the process terminated on the specified
        signal. If the signal is ``None`` or unsupplied, returns
        ``True`` if the process terminated on a signal.
        """
        if os.WIFSIGNALED(self._exit_code):
            if signal is None:
                return True
            if os.WTERMSIG(self._exit_code) == signal:
                return True
            return False
        return False
    def format_status(self):
        """
        Returns a human-readable representation of how the process
        exited.
        """
        # Cribbed from netsa.util.shell
        if self._exit_code is None:
            return "Not run"
        elif (os.WIFEXITED(self._exit_code) and
              os.WEXITSTATUS(self._exit_code) == 0):
            return "OK"
        elif os.WIFEXITED(self._exit_code):
            return "exit(%d)" % os.WEXITSTATUS(self._exit_code)
        elif os.WIFSIGNALED(self._exit_code):
            return "signal(%d)" % os.WTERMSIG(self._exit_code)
        else:
            return "?(%d)" % self._exit_code
    def get_status(self):
        """Returns the raw exit status of the process, as an integer
        formatted in the style of :func:`os.wait`."""
        return self._exit_code
    def get_stdout(self):
        "Returns the standard output of the process as a string."
        return self._stdout
    def get_stderr(self):
        "Returns the standard error of the process as a string."
        return self._stderr
    def get_info(self):
        """
        Returns the information contained in the result as a
        human-readable string.
        """
        s = StringIO.StringIO()
        s.write("Command: %s\n" % self._command)
        s.write("Status: %s\n" % self.format_status())
        s.write("Environment --------------\n")
        s.write("%s\n" % format_envars(self._envars, delim="\n\n"))
        s.write("--------------------------\n")
        s.write("Stdout: ------------------\n")
        s.write(self.get_stdout())
        s.write("Stderr: ------------------\n")
        s.write(self.get_stderr())
        s.write("--------------------------\n")
        return s.getvalue()
                
                
            

class Environment(object):
    """
    An environment for running commands, including a set of
    environment variables and a working directory.
        
    The *work_dir* argument is the working directory in which the
    commands are run. If *work_dir* is ``None``, a directory will be
    made using :func:`tempfile.mkdtemp` with default values.

    *work_dir* must not already exist or :func:`run` will raise a
    :exc:`TestingException`. If *save_work_dir* is ``False``,
    :func:`cleanup` will remove this directory when it is called.

    If *debug* is ``True``, several debug messages will be emitted on
    ``stderr``.

    Any additional keyword arguments are used as environment
    variables.
    """
    def __init__(self, work_dir=None, save_work_dir=False, debug=False,
                 **envars):
        self._should_debug = debug
        if work_dir is None:
            self._work_dir = tempfile.mkdtemp()
        else:
            try:
                os.mkdir(work_dir)
                self._work_dir = work_dir
            except OSError, e:
                if e.errno == errno.EEXIST:
                    raise TestingException("%s already exists" % work_dir)
        self._debug("Created %s" % self._work_dir)
        self._save_work_dir = save_work_dir
        self._envars = envars
    def _debug(self, message):
        return dbgmsg(self._should_debug, "ENV: %s" % message)
    def get_env(self, env_name):
        """
        Returns the value of *env_name* in the environment. If
        *env_name* does not exist in the environment, this method
        returns ``None``.
        """
        return self._envars.get(env_name, None)
    def set_env(self, env_name, env_val):
        """
        Sets the value of *env_name* in the environment to
        *env_val*. *env_val* must be a string.
        """
        if not isinstance(env_val, BaseString):
            raise TestingException(
                "env_val argument to set_env must be a string")
        self._envars[env_name] = env_val
    def del_env(self, env_name):
        """
        Removes *env_name* from the environment. If *env_name* doesn't
        exist, this method has no effect.
        """
        try:
            del self._envars[env_name]
        except KeyError:
            pass
    def get_work_dir(self):
        """
        Returns the working directory in which the commands are run.
        """
        return self._work_dir
    def run(self, command, **command_options):
        """
        Runs a single command, capturing and returning result
        information.  Keyword arguments are passed to
        :func:`netsa.util.shell.run_parallel`.  See the documentation
        of that function for an explanation of how such arguments are
        interpreted.

        Returns a :class:`Result` object representing the outcome.
        """
        self._debug("Running %s" % command)
        self._debug("Options: %s" % command_options)

        # Wrap command in an env call
        envars = format_envars(self._envars)
        env_command = "env -i %s %s" % (envars, command)

        # Create a temporary file to collect output
        stdout_tmp = os.tmpfile()
        stderr_tmp = os.tmpfile()
        # Replace any existing "stdout" and "stderr" definitions
        command_options["stdout"] = stdout_tmp
        command_options["stderr"] = stderr_tmp
        # chdir to working directory
        orig_directory = os.getcwd()
        try:
            os.chdir(self._work_dir)
            try:
                exit_codes = shell.run_parallel([env_command],
                                                **command_options)
            except shell.PipelineException, e:
                exit_codes = e.get_exit_statuses()
        finally:
            os.chdir(orig_directory)
        # Seek back to the start of the temporary file
        stdout_tmp.seek(0)
        stderr_tmp.seek(0)
        res = Result(command, self._envars, exit_codes,
                     stdout_tmp.read(), stderr_tmp.read())
        return res
    def cleanup(self):
        """
        Cleans up resources left behind by the test process.
        """
        if self._save_work_dir:
            print >>sys.stderr, ("Env cleanup: "
                                 "command output at %s" % self._work_dir)
        else:
            os.system("rm -rf %s" % self._work_dir)


__all__ = """

    TestingException
    Environment
    Result

""".split()
