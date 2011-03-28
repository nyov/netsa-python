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

The :mod:`netsa.util.shell` module provides a facility for securely
and efficiently running UNIX command pipelines from Python.  To avoid
text substitution attacks, it does not actually use the UNIX shell to
process commands.  In addition, it runs commands directly in a way
that allows easier clean-up in the case of errors.

The following standard Python library functions provide similar
capabilities, but without either sufficient text substitution
protections or sufficient error-checking and recovery mechanisms:

  - The :func:`os.system` function
  - The :mod:`subprocess` module
  - The :mod:`popen2` module

Here are some examples, in increasing complexity, of the use of the
:func:`run_parallel` and :func:`run_collect` functions:

Run a single process and wait for it to complete::

    # Shell: rm -rf /tmp/test
    run_parallel("rm -rf /tmp/test")

Start two processes and wait for both to complete::

    # Shell: rm -rf /tmp/test1 & rm -rf /tmp/test2 & wait
    run_parallel("rm -rf /tmp/test_dir_1",
                 "rm -rf /tmp/test_dir_2")

Store the output of a command into a file::

    # Shell: echo test > /tmp/testout
    run_parallel(["echo test", ">/tmp/testout"])

Read the input of a command from a file (and put the ouput into
another file)::

    # Shell: cat < /tmp/test > /tmp/testout
    run_parallel(["</tmp/test", "cat", ">/tmp/testout"])

Append the output of a command to a file::

    # Shell: echo test >> /tmp/testout
    run_parallel(["echo test", ">>/tmp/testout"])

Pipe the output of one command into another command (and put the
output into a file)::

    # Shell: echo test | sed 's/e/f/' > /tmp/testout
    run_parallel(["echo test", "sed 's/e/f/'", ">/tmp/testout"])

Run two pipelines in parallel and wait for both to complete::

    # Shell:
    #    echo test | sed 's/e/f/' > /tmp/testout &
    #    cat /etc/passwd | cut -f1 -d'|' > /tmp/testout2 &
    #    wait
    run_parallel(["echo test", "sed 's/e/f/'", ">/tmp/testout"],
                 ["cat /etc/passwd", "cut -f1 -d'|'", ">/tmp/testout2"])

Run a single pipeline and collect the output and error output in the
variables *out* and *err*::

    # Shell: foo=`cat /etc/passwd | cut -f1 -d'|'`
    (foo, foo_err) = run_collect("cat /etc/passwd", "cut -f1 -d'|'")

The following examples are more complicated, and require the use of
the long forms of :func:`command` and :func:`pipeline` specifications.
(All of the examples above have used the short-hand forms.)  You
should read the documentation for :func:`command` and :func:`pipeline`
to see how the long forms and short-hand forms are related.

Run a pipeline, collect standard output of the pipeline to one file,
and append standard error from all of the commands to another file::

    # Shell: ( gen-data | cut -f1 -d'|' > /tmp/testout ) 2>> /tmp/testlog
    run_parallel(pipeline("gen-data", "cut -f1 -d'|'", ">/tmp/testout",
                          stderr="/tmp/testlog", stderr_append=True))

Run a pipeline, collect standard output of the pipeline to one file,
and collect standard error from one command to another file::

    # Shell: ( gen-data 2> /tmp/testlog ) | cut -f1 -d'|' > /tmp/testout
    run_parallel([command("gen-data", stderr="/tmp/testlog"),
                  "cut -f1 -d'|'", ">/tmp/testout"])

Run a pipeline, collect standard output of the pipeline to a file, and
ignore the potentially non-zero exit status of the ``gen-data``
command::

    # Shell: (gen-data | cut -f1 -d'|' > /tmp/testout) || true
    run_parallel([command("gen-data", ignore_exit_status=True),
                  "cut -f1 -d'|'", ">/tmp/testout"])

Use long pipelines to process data using multiple named pipes::

    # Shell:
    #   mkfifo /tmp/fifo1
    #   mkfifo /tmp/fifo2
    #   tee /tmp/fifo1 < /etc/passwd | cut -f1 -d'|' | sort > /tmp/out1 &
    #   tee /tmp/fifo2 < /tmp/fifo1 | cut -f2 -d'|' | sort > /tmp/out2 &
    #   cut -f3 -d'|' < /tmp/fifo2 | sort | uniq -c > /tmp/out3 &
    #   wait
    run_parallel("mkfifo /tmp/fifo1",
                 "mkfifo /tmp/fifo2")
    run_parallel(
        ["</etc/passwd", "tee /tmp/fifo1", "cut -f1 -d'|'", ">/tmp/out1"],
        ["</tmp/fifo1", "tee /tmp/fifo2", "cut -f2 -d'|'", ">/tmp/out2"],
        ["</tmp/fifo2", "cut -f3 -d'|'", "sort", "uniq -c", ">/tmp/out3"])


"""

__docformat__ = "restructuredtext en"

import copy
import errno
import netsa
import os
import select
import shlex
import signal
import sys
import time
import traceback
import threading

try:
    MAXFD = os.sysconf("SC_OPEN_MAX")
except:
    MAXFD = 256

# Exception for reporting a pipeline failure (failure during runtime
# of the pipeline, not config failure setting it up.
class PipelineException(Exception):
    """
    This exception represents a failure to process a pipeline in
    either :func:`run_parallel` or :func:`run_collect`.  It can be
    triggered by any of the commands being run by the function failing
    (either because the file was not found or because the command's
    exit status was unacceptable.)  The message contains a summary of
    the status of all of the sub-commands at the time the problem was
    discovered, including stderr output for each sub-command if
    available.
    """
    def __init__(self, message, exit_statuses):
        self._message = message
        self._exit_statuses = exit_statuses
    def get_message(self):
        return self._message
    def get_exit_statuses(self):
        return self._exit_statuses
    def __str__(self):
        return str(self._message)

def format_arg(x):
    if isinstance(x, basestring):
        if '\\' in x or '"' in x or "'" in x or ' ' in x:
            return repr(x)
        return x
    else:
        return repr(x)

def format_args(args):
    return ' '.join(format_arg(x) for x in args)

def format_status(status):
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0:
        return "OK"
    elif os.WIFEXITED(status):
        return "exit(%d)" % os.WEXITSTATUS(status)
    elif os.WIFSIGNALED(status):
        return "signal(%d)" % os.WTERMSIG(status)
    else:
        return "?(%d)" % status

def format_stream(prefix, stream, append=False):
    if stream is None:
        return None
    if isinstance(stream, basestring):
        if prefix[-1] == '>' and append:
            return '%s>%s' % (prefix, format_arg(stream))
        return "%s%s" % (prefix, format_arg(stream))
    elif isinstance(stream, int):
        return '%s&%d' % (prefix, stream)
    else:
        return '%s%s' % (prefix, format_arg(stream))

def open_stream(stream, mode):
    istream = stream
    stream_file = None
    if stream is None:
        stream = '/dev/null'
    if isinstance(stream, basestring):
        stream = open(stream, mode)
    if isinstance(stream, file):
        stream_file = stream
        stream = stream.fileno()
    if not isinstance(stream, int):
        raise TypeError("Invalid type to open as stream (fd)")
    return (stream, stream_file)

class Task(object):
    __slots__ = ['_task_groups', '_name', '_cond_var']
    def __init__(self, name,
                 fin, fout, ferr, fout_append, ferr_append):
        fin_name = format_stream('<', fin)
        fout_name = format_stream('>', fout, fout_append)
        ferr_name = format_stream('2>', ferr, ferr_append)
        self._task_groups = set([])
        self._name = ' '.join(x for x in (name, fin_name, fout_name, ferr_name)
                              if x is not None)
        self._cond_var = threading.Condition()
    def add_task_group(self, task_group):
        self._cond_var.acquire()
        try:
            self._task_groups.add(task_group)
            task_group.add_task(self)
        finally:
            self._cond_var.release()
    def __str__(self):
        return self.get_status()
    def get_name(self):
        "Human readable name for this task."
        return self._name
    def wait(self):
        "Wait for this task to complete."
        self._cond_var.acquire()
        try:
            while self.is_running():
                self._cond_var.wait()
        finally:
            self._cond_var.release()
    def _notify_status_change(self):
        self._cond_var.acquire()
        try:
            self._cond_var.notifyAll()
            for task_group in self._task_groups:
                task_group._check_task(self)
        finally:
            self._cond_var.release()
    def abort(self):
        "Abort processing this task.  Do not wait for abort to complete."
        raise NotImplementedError("Task.abort")
    def is_running(self):
        "True if the task has not yet completed, False otherwise."
        raise NotImplementedError("Task.is_running")
    def is_success(self):
        "True if the task completed successfully, False otherwise."
        raise NotImplementedError("Task.is_success")
    def get_status(self):
        "Human readable status description."
        raise NotImplementedError("Task.get_status")
    def get_exit_status(self):
        """Returns a list of process exit statuses. For groups of
        tasks, each element represents a process in the group, in
        their order in the pipeline; for individual tasks, this method
        returns a one-element list.

        For completed processes, statuses are integers encoded in the
        format defined for the :func:`os.wait` function.  Tasks that
        have not been completed (e.g., due to an error in a pipeline
        before the process was run), will have an exit status of
        ``None``."""
        raise NotImplementedError("Task.get_exit_status")

class Task_group(object):
    __slots__ = ['_name', '_tasks', '_running_tasks', '_failed', '_cond_var']
    def __init__(self, name=None):
        self._name = name
        self._tasks = set([])
        self._running_tasks = set([])
        self._failed = False
        self._cond_var = threading.Condition()
    def __str__(self):
        return self.get_status()
    def get_name(self):
        return self._name
    def wait(self):
        self._cond_var.acquire()
        try:
            try:
                # Wait while there are still running tasks in the group
                while self._running_tasks:
                    self._cond_var.wait()
            except KeyboardInterrupt:
                # If we get a keyboard interrupt while waiting, abort
                self.abort()
                raise
        finally:
            self._cond_var.release()
    def add_task(self, task):
        self._cond_var.acquire()
        try:
            self._tasks.add(task)
            self._running_tasks.add(task)
            # Are we already aborted?
            if self._failed:
                task.abort()
            self._cond_var.notifyAll()
            self._check_task(task)
        finally:
            self._cond_var.release()
    def _check_task(self, task):
        self._cond_var.acquire()
        try:
            if task in self._running_tasks and not task.is_running():
                self._running_tasks.remove(task)
                if not task.is_success():
                    # It was a failure: boom
                    self.abort()
                self._cond_var.notifyAll()
        finally:
            self._cond_var.release()
    def abort(self):
        self._cond_var.acquire()
        try:
            if self._failed:
                # Already aborted, abort aborting
                return
            else:
                self._failed = True
            # Make thread to do the aborting,  Ungh.
            running_tasks = list(self._running_tasks)
            def abort_subtasks():
                for task in running_tasks:
                    task.abort()
            threading.Thread(target=abort_subtasks).start()
        finally:
            self._cond_var.release()
    def is_running(self):
        self._cond_var.acquire()
        try:
            return bool(self._running_tasks)
        finally:
            self._cond_var.release()
    def is_success(self):
        self._cond_var.acquire()
        try:
            return not (self.is_running() or self._failed)
        finally:
            self._cond_var.release()
    def get_status(self):
        return '\n'.join(task.get_status() for task in self._tasks)
    def get_exit_status(self):
        return [s for task in self._tasks for s in task.get_exit_status()]

NUKE_DELAY = 4.0                # Seconds before using SIGKILL after SIGTERM

class Task_process(Task):
    __slots__ = ['_exit_status', '_ignore_exits', '_pid',
                 '_stderr_text', '_aborted']
    def __init__(self, args, fin, fout, ferr, fout_append, ferr_append,
                 ignore_exits):
        Task.__init__(self, format_args(args),
                      fin, fout, ferr, fout_append, ferr_append)
        self._cond_var.acquire()
        try:
            self._aborted = False
            self._exit_status = None
            self._ignore_exits = ignore_exits
            self._pid = None
            self._stderr_text = ""
            
            # If ferr is None, let's set up a collector thread
            used_own_ferr = False
            if ferr is None:
                used_own_ferr = True
                (ferr_in, ferr) = os.pipe()
                def collect_stderr():
                    try:
                        last_read = None
                        while self.is_running():
                            (rl, wl, xl) = select.select([ferr_in], [], [], 1.0)
                            if rl:
                                while last_read != "":
                                    last_read = os.read(ferr_in, 1024)
                                    self._stderr_text += last_read
                    finally:
                        os.close(ferr_in)
                threading.Thread(target=collect_stderr).start()
            # All of our ducks are lined up.
            pid = os.fork()
            if pid == 0:
                # Child
                try:
                    try:
                        if netsa.DEBUG:
                            print >>sys.stderr, "Starting [%d] %s" % \
                                (os.getpid(), self.get_name())
                        (in_fd, in_file) = open_stream(fin, 'r')
                        (out_fd, out_file) = \
                            open_stream(fout, fout_append and 'a' or 'w')
                        # Set up stdin, stdout, stderr
                        if in_fd is not None:
                            os.dup2(in_fd, 0)
                        if out_fd is not None:
                            os.dup2(out_fd, 1)
                        if ferr is not None:
                            # If ferr is None, we don't touch it
                            (err_fd, err_file) = \
                                open_stream(ferr, ferr_append and 'a' or 'w')
                            os.dup2(err_fd, 2)
                        # Close everything else
                        for i in xrange(3, MAXFD):
                            try:
                                os.close(i)
                            except:
                                pass
                        if callable(args[0]):
                            # The "program" is actually a function
                            try:
                                args[0](vars=args[1], *args[2:])
                            finally:
                                sys.stdout.flush()
                                sys.stderr.flush()
                            # If there's an exception, it'll fall through
                            # to the traceback printing below.
                            os._exit(0)
                        else:
                            # The program is a program
                            try:
                                os.execvp(args[0], args)
                            except OSError, e:
                                if e.errno == errno.ENOENT:
                                    raise Exception("%s: command not found" %
                                                    args[0])
                                else:
                                    raise
                    except:
                        traceback.print_exc()
                        os._exit(255)
                finally:
                    print >>sys.stderr, "WARNING: SHOULD NEVER REACH HERE"
                    os._exit(255)
                print >>sys.stderr, "WARNING: REALLY NOTHING SHOULD BE HERE"
                os._exit(254)
            # Parent
            if used_own_ferr:
                os.close(ferr)
            self._pid = pid
            def wait_for_process():
                (result_pid, result_exit) = os.waitpid(self._pid, 0)
                assert result_pid == self._pid
                self._set_status(result_exit)
            threading.Thread(target=wait_for_process).start()
        finally:
            self._cond_var.release()
    def _set_status(self, status):
        self._cond_var.acquire()
        try:
            self._exit_status = status
            if netsa.DEBUG:
                print >>sys.stderr, "Status [%d] %s" % \
                    (self._pid, self)
            self._notify_status_change()
        finally:
            self._cond_var.release()
    def _abort(self, sig):
        self._cond_var.acquire()
        try:
            # Can't abort if there's no PID.  Check if exited or not started
            if not self.is_running():
                # We already completed, do nothing
                return
            while self._pid is None:
                # We're not running yet, wait for startup to complete
                self._cond_var.wait()
            # Now we must be running, try killing it
            try:
                if netsa.DEBUG:
                    print >>sys.stderr, "Killing [%d] %s (%d)" % \
                        (self._pid, self.get_name(), sig)
                os.kill(self._pid, sig)
            except OSError:
                # If we fail to kill it, just ignore the error.
                pass
        finally:
            self._cond_var.release()
    def abort(self):
        # Quick short-cut in case we've already exited
        if not self.is_running():
            return
        # Try SIGTERM
        self._abort(signal.SIGTERM)
        # Set up a thread to try SIGKILL in a short time
        def delayed_nuke():
            time.sleep(NUKE_DELAY)
            self._abort(signal.SIGKILL)
        threading.Thread(target=delayed_nuke).start()
    def is_running(self):
        self._cond_var.acquire()
        try:
            return (self._exit_status is None)
        finally:
            self._cond_var.release()
    def is_success(self):
        self._cond_var.acquire()
        try:
            if self._exit_status == 0:
                return True
            elif self._exit_status == None:
                return False
            else:
                if os.WIFEXITED(self._exit_status):
                    if self._ignore_exits is False:
                        # Aleady checked if exit status is zero, so...
                        return False
                    if self._ignore_exits is True:
                        return True
                    if os.WEXITSTATUS(self._exit_status) in self._ignore_exits:
                        return True
                return False
        finally:
            self._cond_var.release()
    def get_status(self):
        self._cond_var.acquire()
        try:
            if self._exit_status is None:
                stat_line = self.get_name() + " RUNNING"
            else:
                stat_line = self.get_name() + " " + \
                    format_status(self._exit_status)
            if self._stderr_text:
                stderr_text = self._stderr_text
                if stderr_text[-1] == '\n':
                    stderr_text = stderr_text[:-1]
                stat_line = stat_line + "\n  " + \
                    "\n  ".join(stderr_text.split('\n'))
            return stat_line
        finally:
            self._cond_var.release()
    def get_exit_status(self):
        return [self._exit_status]
                

def _interpolate_vars(arg_list, vars):
    # First interpolate any "argument list" variables
    for (k, v) in vars.iteritems():
        try:
            # Attempt to get an arg list
            new_args = v.get_argument_list()
            key_string = '%%(%s)s' % k
            new_arg_list = []
            for a in arg_list:
                if not isinstance(a, basestring):
                    new_arg_list.append(a)
                    continue
                while True:
                    i = a.find(key_string)
                    while i != -1 and i < len(a):
                        # Check if we have a % in front to escape it
                        if i != 0 and a[i-1] == '%':
                            # Yeah.  Find the next one.
                            i = a.find(key_string, i + 1)
                            continue
                        else:
                            # We found a real one
                            break
                    if i == -1:
                        # No match found
                        new_arg_list.append(a)
                        break
                    # Substitution target
                    # Put any preceding stuff into arg list
                    if i > 0:
                        # Strip it to avoid putting in whitespace
                        s = a[:i].strip()
                        if s: new_arg_list.append(s)
                    for b in new_args:
                        # Quote %s to avoid double-interpolation
                        new_arg_list.append(b.replace('%','%%'))
                    # Now work on the remainder
                    a = a[i+len(key_string):].strip()
                    # Unless it's empty
                    if a == '':
                        break
            arg_list = new_arg_list
        except AttributeError:
            # If there's no method, that's fine.
            pass
    # That's done.  Do the easy part.
    return [isinstance(x, basestring) and (x % vars) or x
            for x in arg_list]

# Fork off a single child for a command
# Returns a tuple (pid, ignore, ignore_status) to allow for ignoring
# exit status if options indicate.
def fork_child(task_group, command, stdin, stdout, stdout_append,
               vars, defaults):
    # Apply substitutions
    args = _interpolate_vars(command.argv, vars)
    if callable(args[0]):
        args = [args[0], vars] + args[1:]
    stderr = command.get_options(defaults).get('stderr', None)
    if isinstance(stderr, basestring):
        stderr = stderr % vars
    stderr_append = command.get_options(defaults).get('stderr_append', False)
    ignore = command.get_options(defaults).get('ignore_exit_status', False)
    ignore_status = command.get_options(defaults).get('ignore_exit_statuses',[])
    ignore_exits = False
    if ignore_status: ignore_exits = ignore_status
    if ignore: ignore_exits = True
    # Fork an individual child in a pipeline
    task = Task_process(args, stdin, stdout, stderr,
                        stdout_append, stderr_append, ignore_exits)
    task.add_task_group(task_group)
    return task

# Fork off children for a pipeline, and return a Pipeline_waiter
def fork_children(task_group, pipeline, vars={}, defaults={}):
    commands = pipeline.commands
    in_file = pipeline.get_options(defaults).get('stdin', '/dev/null')
    if isinstance(in_file, basestring):
        in_file = in_file % vars
    out_file = pipeline.get_options(defaults).get('stdout', '/dev/null')
    if isinstance(out_file, basestring):
        out_file = out_file % vars
    out_append = pipeline.get_options(defaults).get('stdout_append', False)
    # fd of the output side of the last pipe that was opened
    last_pipe = None
    for i, cmd in enumerate(commands):
        if i == 0:
            # The first command's input is in_file
            stdin = in_file
        else:
            # All other commands read from the output side of the last command
            stdin = last_pipe
        if i == len(commands) - 1:
            # The last command's output is out_file
            stdout = out_file
        else:
            # Everybody else outputs to the input side of a fresh pipe
            (last_pipe, stdout) = os.pipe()
        fork_child(task_group, cmd, stdin, stdout, out_append, vars, defaults)
        if isinstance(stdin, int):
            os.close(stdin)
        if isinstance(stdout, int):
            os.close(stdout)

# Do not use this to make command lines for the shell.  It's intended
# only for use in producing human-readable output.
def display_argv(argv):
    quoted_argv = []
    for a in argv:
        if callable(a):
            quoted_argv.append(repr(a))
        elif ' ' in a or "'" in a or '\\' in a:
            quoted_argv.append('"%s"' % a.replace("\\", "\\\\")
                                         .replace('"', "\\\""))
        elif '"' in a:
            quoted_argv.append("'%s'" % a)
        else:
            quoted_argv.append(a)
    return ' '.join(quoted_argv)

def display_options(options):
    return ', '.join("%s=%s" % (o, repr(options[o]))
                     for o in sorted(options))

def display_commands(commands, stdin, stdout, stdout_append):
    command_list = list(commands)
    if stdin:
        command_list.insert(0, '<%s' % stdin)
    if stdout:
        if stdout_append:
            command_list.append('>>%s' % stdout)
        else:
            command_list.append('>%s' % stdout)
    return ", ".join(repr(x) for x in command_list)

class OptionHolder(object):
    __slots__ = ['options']
    def __init__(self, options):
        self.options = dict(options)
    def with_options(self, options):
        result = copy.copy(self)
        merged_options = dict(self.options)
        merged_options.update(options)
        result.options = merged_options
        return result
    def get_options(self, defaults={}):
        merged_options = dict(defaults)
        merged_options.update(self.options)
        return merged_options

class CommandSpec(OptionHolder):
    __slots__ = ['argv']
    def __init__(self, argv, options):
        OptionHolder.__init__(self, options)
        self.argv = list(argv)
        if len(argv) == 0:
            raise TypeError("Commands must contain a program name")
        for i, x in enumerate(argv):
            if i == 0:
                if not isinstance(x, basestring) and not callable(x):
                    msg = "First command argument must be a string or callable"
                    raise TypeError(msg, x)
            else:
                if not isinstance(x, basestring):
                    msg = "Command arguments must be strings"
                    raise TypeError(msg, x)
    def __repr__(self):
        if self.options == {}:
            return repr(display_argv(self.argv))
        else:
            return "command(%s, %s)" % (repr(display_argv(self.argv)),
                                        display_options(self.options))
    def expand(self, vars, defaults):
        result = copy.copy(self)
        result.argv = list(result.argv)
        for (i, arg) in enumerate(result.argv):
            try:
                result.argv[i] = arg % vars
            except TypeError:
                pass
        result.options = result.get_options(defaults)
        if 'stderr' in result.options:
            if isinstance(result.options['stderr'], basestring):
                result.options['stderr'] = result.options['stderr'] % vars
        return result

class PipelineSpec(OptionHolder):
    __slots__ = ['commands']
    def __init__(self, commands, options):
        OptionHolder.__init__(self, options)
        self.commands = commands
        if len(commands) == 0:
            raise TypeError("Pipeline must contain at least one command")
        for x in commands:
            if not isinstance(x, CommandSpec):
                msg = "All items in a pipeline must be commands"
                raise TypeError(msg, x)
    def __repr__(self):
        options = dict(self.options)
        if 'stdin' in options: del options['stdin']
        if 'stdout' in options: del options['stdout']
        if 'stdout_append' in options: del options['stdout_append']
        stdin = self.options.get('stdin', None)
        stdout = self.options.get('stdout', None)
        stdout_append = self.options.get('stdout_append', None)
        if options == {}:
            return "[%s]" % display_commands(self.commands,
                                             stdin, stdout, stdout_append)
        else:
            return "pipeline(%s, %s)" % (display_commands(self.commands,
                                                          stdin, stdout,
                                                          stdout_append),
                                         display_options(options))

def command(*argv, **options):
    """
    Interprets the arguments as a "command specification", and returns
    that specification as a value.

    If there is only a single argument and it is a :func:`command`,
    then a new command is returned with the options provided by this
    call.  For example::

        new_command = command(old_command, ignore_exit_status=True)

    If there is only a single argument and it is a :class:`str`, the
    string is parsed as if it were a simple shell command.
    (i.e. respecting single and double quotation marks, backslashes,
    etc.)  For example::

        new_command = command("ls /etc")

    If there is only a single argument and it is a :class:`list` or a
    :class:`tuple`, interpret it as being the argument vector for the
    command (with the first argument being the command to be
    executed.)  For example::

        new_command = command(["ls", "/etc"])

    If there are multiple arguments, each argument is taken as being
    one element of the argument vector, with the first bring the
    command to be executed.  For example::

        new_command = command("ls", "/etc")

    The following keyword arguments may be given as options to a
    command specification:

      *stderr*
        Filename (:class:`str`) or open :class:`file` object of
        destination for stderr.
      *stderr_append*
        ``True`` if *stderr* should be opened for append.  Does
        nothing if *stderr* is already an open file.
      *ignore_exit_status*
        If ``True``, then the exit status for this command is
        completely ignored.
      *ignore_exit_statuses*
        A list of numeric exit statuses that should not be considered
        errors when they are encountered.

    In addition, these options may be "handed down" from the
    :func:`pipeline` call, or from :func:`run_parallel` or
    :func:`run_collect`.  If so, then options given locally to the
    command take precedence.

    Example: Define a command spec using a single string::

        c = command("ls -lR /tmp/foo")

    Example: Define a command as the same as an old command with
    different options::

        d = command(c, ignore_exit_status=True)

    Example: Define a command using a list of strings::

        e = command(["ls", "-lR", "/tmp/foo"])

    Example: Define a command using individual string arguments::

        f = command("ls", "-lR", "/tmp/foo")

    **Short-hand Form:**
    
    In the :func:`pipeline`, :func:`run_parallel`, and
    :func:`run_collect` functions, commands may be given in a
    short-hand form where convenient.  The short-hand form of a
    command is a single string.  Here are some examples:

    .. sourcecode:: python

        "ls -lR"              =>  command(["ls", "-lR"])
        "echo test test a b"  =>  command(["echo", "test", "test", "a", "b"])
        "echo 'test test' a"  =>  command(["echo", "test test", "a"])
        "'weird program'"     =>  command(["weird program"])

    There is no way to associate options with a short-hand
    :func:`command`.  If you wish to redirect error output or ignore
    exit statuses, you will need to use the long form.

    **Variable Expansion:**

    When commands are executed, variable expansion is performed.  The
    expansions are provided by the argument `vars` to
    :func:`run_parallel` or :func:`run_collect`.  Note that commands
    are split into arguments *before* this expansion occurs, which is
    a security measure.  This means that no matter what whitespace or
    punctuation is in an expansion, it can't change the sense of the
    command.  The down side of that is that on occasions when you
    would like to add multiple arguments to a command, you must
    construct the :func:`command` using the list syntax.

    Expansion variable references are placed using the `Python String
    formatting operations`_.

    .. _`Python String formatting operations`:
        http://docs.python.org/library/stdtypes.html#string-formatting

    Here is an example substitution, showing how ``%(target)s``
    becomes a single argument before the subsitution occurs.

    .. sourcecode:: python

        ("ls -lR %(target)s", vars={'target': 'bl ah"'}) =>
        ("ls", "-lR", "%(target)s", vars={'target': 'bl ah"'}) =>
        ("ls", "-lR", 'bl ah "')

    If the value to be substituted implements the method
    ``get_argument_list``, which takes no arguments and returns a list
    of strings, then those strings are included as multiple separate
    arguments.  This is an expert technique for extending commands at
    call-time for use internal to APIs.

    .. sourcecode:: python

        ("ls -lR %(targets)s", vars={'targets': special_container}) =>
        ("ls", "-lR", "target1", "target2", ...)

    **Functions as Commands:**

    In addition to executable programs, Python functions may also be
    used as commands.  This is useful if you wish to do processing of
    data in a sub-process as part of a pipeline without needing to
    have auxilliary Python script files.  However, this is an advanced
    technique and you should fully understand the subtleties before
    making use of it.

    When a Python function is used as a command, the process will
    `fork` as normal in preparation for executing a new command.
    However, instead of `exec`-ing a new executable, the Python
    function is called.  When the Python function completes (either
    successfully or unsuccessfully), the child process exits
    immediately.

    If you intend to use this feature, be sure that you know how the
    lifecycles of various objects will behave when the Python
    interpreter is forked and two copies are running at once.

    The command function is called with *vars* (as given to
    :func:`run_parallel` or :func:`run_collect`) as its first
    argument, and the remainder of *argv* from calling :func:`command`
    as its remaining arguments.
    """
    # Already a command spec?  Re-use, possibly with new options
    if len(argv) == 1 and isinstance(argv[0], CommandSpec):
        return argv[0].with_options(options)
    # A single string?  Parse with shlex and turn into a command spec.
    if len(argv) == 1 and isinstance(argv[0], basestring):
        argv = shlex.split(argv[0])
        return CommandSpec(argv, options)
    # A single list or tuple?  Treat it as the arguments
    if len(argv) == 1 and isinstance(argv[0], (list, tuple)):
        argv = argv[0]
    # A list? The first item should be a string or function. All other
    # items should be strings, separate items in argv.
    return CommandSpec(argv, options)

def pipeline(*commands, **options):
    """
    Interprets the arguments as a "pipeline specification", and
    returns that specification as a value.

    If there is only a single argument and it is a :func:`pipeline`,
    then a new pipeline is returned with the options provided by this
    call.  For example::

        new_pipeline = pipeline(old_pipeline, stdout="/tmp/newfile")

    If there is only a single argument and it is a :class:`list` or a
    :class:`tuple`, interpret it as being a list of commands and I/O
    redirection short-hands to run in the pipeline.  For example::

        new_pipeline = pipeline(["ls /etc", "tac"])

    If there are multiple arguments, these arguments are treated as a
    list of commands and I/O redirection short-hands (as if they were
    passed as a single list.)  For example::

        new_pipeline = pipeline("ls /etc", "tac")

    The following keyword arguments may be given as options to a
    pipeline specification:

      *stdin*
        Filename (:class:`str`) or open :class:`file` object of source
        for stdin.

      *stdout*
        Filename (:class:`str`) or open :class:`file` object of
        destination for stdout.

      *stdout_append*
        ``True`` if *stdout* should be opened for append.  Does
        nothing if *stdout* is already an open file.

    Because these options are so common, they may also be given in
    short-hand form.  If the first command in the pipeline is a string
    starting with ``<``, the remainder of the string is intepreted as
    a filename for stdin.  If the last command in the pipeline is a
    string starting with ``>`` or ``>>``, the remainder of the string
    is interpreted as a filename for stdout (and if ``>>`` was used,
    it is opened for append.)

    In addition, any unrecognized keyword arguments will be provided
    as defaults for any :func:`command` specifications used in this
    pipeline.  (So, for example, if you give the *ignore_exit_status*
    option to :func:`pipeline`, all of the commands in that pipeline will
    use the same value of *ignore_exit_status* unless they have their
    own overriding setting.)

    Example: Define a pipeline using a list of commands::

        a = pipeline(command("ls -lR /tmp/foo"),
                     command("sort"),
                     stdout="/tmp/testout")

    Example: Define the same pipeline using the short-hand form of
    commands, and the shorthand method of setting stdout::

        b = pipeline("ls -lR /tmp/foo",
                     "sort",
                     ">/tmp/testout")

    Example: Define the same pipeline using a list instead of multiple
    arguments::

        c = pipeline(["ls -lR /tmp/foo",
                      "sort",
                      ">/tmp/testout"])

    Example: Define a new pipeline which is the same as an old
    pipeline but with different options::

        d = pipeline(c, stdout="/tmp/newout")

    **Short-hand Form:**

    In the :func:`run_parallel` command, pipelines may be given in a
    short-hand form where convenient.  The short-hand form of a
    pipeline is a list of commands and I/O redirection short-hands.
    Here are some examples::

        ["ls /tmp/die", "xargs rm"]  =>  pipeline(["ls /tmp/die", "xargs rm"])
        ["</tmp/testin", "sort", ">/tmp/testsort"]  =>
                 pipeline(["sort"], stdin="/tmp/testin", stdout="/tmp/testsort")

    Note that although you can set *stdin*, *stdout*, and
    *stdout_append* using the short-hand form (by using the I/O
    redirection strings at the start and end of the list), you cannot
    set these options to open :class:`file` objects, only to
    filenames.  You also set other options to be passed down to the
    individual commands.

    **Variable Expansion:**

    As in :func:`command`, pipelines have variable expansion.  Most
    variable expansion happens inside the actual commands in the
    pipeline.  However, variable expansion also occurs in filenames
    provided for the *stdin* and *stdout* options.  For example::

        pipeline("ls -lR", ">%(output_file)s")
        pipeline("ls -lR", stdout="%(output_file)s")

    
    """
    # Already a pipeline spec?  Re-use, possibly with new options
    if len(commands) == 1 and isinstance(commands[0], PipelineSpec):
        return commands[0].with_options(options)
    # A single list or tuple?  Treat it as the arguments
    if len(commands) == 1 and isinstance(commands[0], (list, tuple)):
        commands = commands[0]
    # A list?  Each item should parse with command(x), except perhaps
    # the first and last, which can be redirection.
    if (len(commands) >= 1 and isinstance(commands[0], basestring) and
            commands[0].strip().startswith("<")):
        options['stdin'] = commands[0].strip()[1:].strip()
        commands = commands[1:]
    if (len(commands) >= 1 and isinstance(commands[-1], basestring) and
            commands[-1].strip().startswith(">>")):
        options['stdout_append'] = True
        options['stdout'] = commands[-1].strip()[2:].strip()
        commands = commands[:-1]
    elif (len(commands) >= 1 and isinstance(commands[-1], basestring) and
              commands[-1].strip().startswith(">")):
        options['stdout_append'] = False
        options['stdout'] = commands[-1].strip()[1:].strip()
        commands = commands[:-1]
    commands = [command(x) for x in commands]
    return PipelineSpec(commands, options)



def run_parallel(*args, **options):
    """
    Runs a series of commands (as specified by the arguments provided)
    by forking and establishing pipes between commands.  Raises
    :exc:`PipelineException` and kills off all remaining subprocesses
    if any one command fails.

    Each argument is passed to the :func:`pipeline` function to create
    a new pipeline, which allows the short-hand form of pipelines (as
    :class:`list` short-hands) to be used.

    The following keyword arguments may be given as *options* to
    :func:`run_parallel`:

      *vars*
        A dictionary of variable substitutions to make in the
        :func:`command` and :func:`pipeline` specifications in this
        `run_parallel` call.

    Additional keyword arguments will be passed down as default values
    to the :func:`pipeline` and :func:`command` specifications making
    up this :func:`run_parallel` call.

    The :func:`run_parallel` function returns the list of exit codes
    of the processes in each pipeline as a list of lists. Each list
    corresponds to a pipeline, in the order in which they were passed
    into the function. Each element represents a process in the
    pipeline, in the order they were defined in the pipeline. If a
    process is not run (e.g., because a process preceding it in the
    pipeline fails), the exit status will be `None`.

    Example: Run three mkdirs in parallel and fail if any of them fails::

        run_parallel("mkdir a", "mkdir b", "mkdir c")

    Example: Make a fifo, then afterwards, use it to do some work.
    (Try making a typo in here and watch it kill everything off
    instead of hanging forever.)

    .. sourcecode:: python

        run_parallel("mkfifo test.fifo")
        run_parallel(["cat /etc/passwd", "sort -r", "cut -f1 -d:", ">%(f)s"],
                     ["cat %(f)s", "sed -e 's/a/b/g'", ">%(f2)s"],
                     vars={'f': 'test.fifo', 'f2': 'test.

    Example: run two pipelines in parallel, then investigate their
    processes' exit statuses::

        exits = run_parallel(["ls -l", "grep ^d"],
                             ["cat /etc/passwd", "sort -r", "cut -f1 -d:"])
        # If all complete successfully, exits will be:
        #  [[0, 0], [0, 0, 0]]
    """

    # By default, provide no substitutions
    vars = options.get('vars', {})

    # Don't pass this one down to be part of the pipeline definition
    if 'vars' in options:
        del options['vars']

    # Parse the arguments into pipeline specifications
    pipelines = [pipeline(x) for x in args]

    def chew_exit_statuses(statuses):
        # Note that this _destructively edits_ the exit statuses
        # list....
        all_exits = []
        for p in pipelines:
            p_exits = []
            for c in p.commands:
                if len(statuses) == 0:
                    p_exits.append(None)
                else:
                    p_exits.append(statuses.pop(0))
                    all_exits.append(p_exits)
        return all_exits

    task_group = Task_group()
    for p in pipelines:
        fork_children(task_group, p, vars, options)
    task_group.wait()
    exit_statuses = chew_exit_statuses(task_group.get_exit_status())
    if not task_group.is_success():
        # It failed, raise an exception
        pipeline_failure = \
            PipelineException("Failure processing pipeline\n" +
                              task_group.get_status(), exit_statuses)
        raise pipeline_failure
    else:
        return exit_statuses

def run_collect_files(*args, **options):
    """
    Runs a series of commands like :func:`run_collect`, but returns
    open file objects for `stdout` and `stderr` instead of strings.

    Example: Iterate over the lines of ``ls -l | sort -r`` and print
    them out with line numbers::

        (f_stdout, f_stderr) = run_collect_files("ls -l", "sort -r")
        for (line_no, line) in enumerate(f_stdout):
            print ("%3d %s" % (line_no, line[:-1]))

    """
    # Create temporary files to collect output
    stdout_tmp = os.tmpfile()
    stderr_tmp = os.tmpfile()
    # Replace any existing "stdout" and "stderr" definitions
    options["stdout"] = stdout_tmp
    options["stderr"] = stderr_tmp
    # Use run_parallel to run *args as a single pipeline
    try:
        run_parallel(pipeline(*args), **options)
    except PipelineException, e:
        msg = e.get_message()
        stderr_tmp.flush()
        stderr_tmp.seek(0)
        msg = "\n".join(filter(None, [msg, stderr_tmp.read().strip()]))
        raise PipelineException(msg, e.get_exit_statuses())
    # Seek back to the start of the temporary files
    stdout_tmp.seek(0)
    stderr_tmp.seek(0)
    # Return the files as output
    return (stdout_tmp, stderr_tmp)


def run_collect(*args, **options):
    """
    Runs a series of commands specifying a single pipeline by forking
    and establishing pipes between commands.  The output of the final
    command is collected and returned in the result.  stderr across
    all commands is returned in the result.  The final result is a
    tuple (`stdout`, `stderr`)

    Raises :exc:`PipelineException` and kills off all remaining
    subprocesses if any one command fails.

    The arguments are passed as arguments to a single call of the
    :func:`pipeline` function to create a pipeline specification.
    That is: each argument is a :func:`command` specification.  Note
    that this is not the same as :func:`run_parallel`, which
    interprets its arguments as multiple :func:`pipeline`
    specifications.

    You can also redirect stderr independently for each command if
    needed, allowing you to send some stderr to ``/dev/null`` or
    another destination instead of collecting it.

    Example: Reverse sort the output of ``ls -1`` and store the output
    and error in the variables `a_stdout` and `a_stderr`::

        # Reverse sort the output of ls -1
        (a_stdout, a_stderr) = run_collect("ls -1", "sort -r")

    Example: Do the same as the above, but run ``ls -1`` on a named
    directory instead of the current working directory::

        # The same with a named directory
        (b_stdout, b_stderr) = run_collect("ls -1 %(dir)s", "sort -r",
                                           vars={'dir': 'some_directory'})

    Example: The following *does not collect output*, but instead
    writes it to a file.  If there were any error output, it would be
    returned in the variable `c_stderr`::
                                           
        (empty_stdout, c_stderr) = run_collect("ls -1", "sort -r", ">test.out")

    """
    (stdout_tmp, stderr_tmp) = run_collect_files(*args, **options)
    # Return the full contents as output
    return (stdout_tmp.read(), stderr_tmp.read())


__all__ = """

    PipelineException

    command
    pipeline

    run_parallel
    run_collect
    run_collect_files

""".split()
