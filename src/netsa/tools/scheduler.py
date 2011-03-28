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

from __future__ import division

from datetime import datetime, timedelta
from netsa.data.times import make_datetime, bin_datetime
import random
from netsa import logging

log = logging.getLogger("netsa.util.scheduler")

class job_manager(object):
    """

    A :class:`job_manager` provides a framework to run multiple jobs
    which may take a long amount of time to run, and which may be told
    when they last ran and when they're currently running.  Each job
    is given a name (which allows for persistent tracking), a period
    between runs (a :class:`datetime.timedelta` object), and a
    function to run to execute the job (which receives two arguments:
    first, the last time the job was run or ``None``.  Second, the
    current time rounded down to the beginning of the time interval.
    For example, a job that is to be run hourly will be told the
    beginning of the current hour when it is run.  A job that is to be
    run every five minutes will be told the beginning of the current
    five-minute period.

    Whenever the :class:`job_manager` is asked to run jobs, it will
    perform the jobs in random order, to ensure fairness.  When each
    job is run, it is expected to update any information needed
    between the last time it ran and the current time it is running.
    For example, an hourly job might digest data for all of the hours
    between the last run and the current time.

    An external script should be used to manage the jobs that are to
    be run, while this object is used to decide what items need to be
    run at the current time, and to run them.

    The wrapper script should create a :class:`job_manager`, then read
    any appropriate configuration files and call :meth:`add_job` for
    each job to be registered.  Then it should register the
    last-run-times of each job using :meth:`set_last_run_time` for
    each job.

    Then the wrapper should call :meth:`run` to execute any jobs that
    need to be run.

    After :meth:`run` returns, the wrapper should call
    :meth:`get_last_run_time` for each job and write the results out
    to permanent storage for the next time the jobs need to be run.

    Note that it's suggested that only one process be running jobs at
    a time: otherwise, some jobs might be run more than once.
    """
    __slots__ = ['_jobs', '_last_run_times']
    def __init__(self):
        """
        Creates a new :class:`job_manager` with no jobs registered.
        """
        self._jobs = {}
        self._last_run_times = {}
    def run(self, force_current_time="no", force_last_time="no"):
        """
        Runs all registered jobs that currently need to perform
        updates.  If the optional *force_current_time* or
        *force_last_time* arguments are included, jobs will be run as if
        working at those times.  (This is useful for testing or force
        loading old data.)
        """
        jobs = list(self._jobs)
        random.shuffle(jobs)
        for job_name in jobs:
            if force_current_time == "no" or force_current_time == None:
                start_time = make_datetime(datetime.utcnow())
            else:
                start_time = make_datetime(force_current_time)
            (period, func) = self._jobs[job_name]
            current_time = bin_datetime(period, start_time)
            if force_last_time == "no" or force_last_time == None:
                last_time = self._last_run_times.get(job_name, None)
            else:
                last_time = make_datetime(force_last_time)
            if last_time is None or last_time < current_time:
                try:
                    log.debug("%s %s %s %s %s" % (job_name, period, last_time,
                                                  current_time, func))
                    func(last_time, current_time)
                    self._last_run_times[job_name] = current_time
                except:
                    # We don't fail on errors.  The func has to do something
                    # if it wants to be special.
                    log.exception("Job manager: error running %s" % job_name)
                    pass
    def add_job(self, name, period, func):
        """
        Adds a job to the list of jobs to be performed.  *name* is the
        name of the job.  *period* is a :class:`datetime.timedelta`
        object representing the frequency with which the job runs.
        *func* is the function to be called to perform the task.

        *func* is called as ``func(last_run_time, current_run_time)``.
        *last_run_time* is ``None`` if the job has never been run
        before.  Both *last_run_time* and *current_run_time* are
        rounded to the beginning of a bin the size of the period.
        """
        self._jobs[name] = (period, func)
    def set_last_run_time(self, name, t):
        """
        Sets the last run time for a named job in order to restore
        state before processing.
        """
        self._last_run_times[name] = t
    def get_last_run_time(self, name):
        """
        Retrieves the last run time for a named job in order to save
        state before ending processing.
        """
        return self._last_run_times.get(name, None)

__all__ = """
    job_manager
""".split()
