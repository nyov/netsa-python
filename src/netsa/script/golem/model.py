# Copyright 2008-2013 by Carnegie Mellon University

# @OPENSOURCE_HEADER_START@
# Use of the Network Situational Awareness Python support library and
# related source code is subject to the terms of the following licenses:
# 
# GNU Public License (GPL) Rights pursuant to Version 2, June 1991
# Government Purpose License Rights (GPLR) pursuant to DFARS 252.227.7013
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

from datetime import datetime, timedelta
from os import path
from copy import copy
import sys, itertools

import netsa.json
from netsa.script      import Flow_params
from netsa.data        import times
from netsa.data.format import datetime_silk_hour, datetime_silk_day, \
                              datetime_iso, timedelta_iso, \
                              DATETIME_DAY, DATETIME_HOUR, DATETIME_MINUTE, \
                              DATETIME_SECOND, DATETIME_MSEC, DATETIME_USEC

from netsa.script       import model
from netsa.script.model import Script
from netsa.script.golem import Nada, GolemScriptError

import netsa.util.compat

GOLEM_VERSION = 1

NULL_DELTA = timedelta(0)

class Golem(Script):
    """
    A :class:`Golem` object represents a golem automation script. It
    encapsulates the logic and meta information necessary to peform
    synchronization with other golem objects. It does not, however,
    interact directly with the OS or perform any system level work.

    The :mod:`netsa.script.golem.script` module has a single instance of
    a :class:`Golem` that represents "the" golem script currently
    running. The module provides various functions that interact with
    this single instance.

    Other than using the functions provided by the :mod:`golem` module,
    a :class:`Golem` object is more commonly encapsulated within a
    :class:`GolemView` derived object which provides the primary
    interface and delegates to :class:`Golem` as necessary.
    """

    __slots__ = ('name', 'suite', 'span', 'interval', 'repository',
                 '_epoch', '_lag', 'realtime',
                 'tags', 'arg_tags', 'flow_maps', 'loops',
                 'golem_inputs', 'output_templates', 'input_templates',
                 'query_templates', '_version')

    default_span     = timedelta(days=1)
    default_interval = timedelta(days=1)
    default_lag      = timedelta(hours=3)
    default_epoch    = times.dow_epoch()

    @classmethod
    def _make_from_meta(cls, **kwargs):
        mdata = kwargs.setdefault('metadata', {})
        version = int(mdata['golem_version'])
        if version > GOLEM_VERSION:
            error = GolemScriptError(
                "Unknown golem version %s" % repr(version))
            raise error
        kwargs['_version'] = version
        if 'golem_span' in mdata:
            kwargs['span'] = \
                times.make_timedelta(mdata.pop('golem_span'))
        if 'golem_interval' in mdata:
            kwargs['interval'] = \
                times.make_timedelta(mdata.pop('golem_interval'))
        if 'golem_lag' in mdata:
            kwargs['lag'] = \
                times.make_timedelta(mdata.pop('golem_lag'))
        if 'golem_epoch' in mdata:
            kwargs['epoch'] = \
                times.make_datetime(mdata.pop('golem_epoch'))
        if 'golem_realtime' in mdata:
            kwargs['realtime'] = bool(mdata.pop('golem_realtime'))
        if 'golem_name' in mdata:
            kwargs['name'] = mdata.pop('golem_name')
        if 'golem_suite_name' in mdata:
            kwargs['suite_name'] = mdata.pop('golem_suite_name')
        if 'golem_inputs' in mdata:
            inputs = []
            for meta, spec in mdata.pop('golem_inputs'):
                inputs.append((cls._make_from_meta(**meta), spec))
            kwargs['golem_inputs'] = inputs
        if 'golem_tags' in mdata:
            kwargs['tags'] = mdata.pop('golem_tags')
        if 'golem_loops' in mdata:
            kwargs['loops'] = mdata.pop('golem_loops')
        if 'golem_flow_maps' in mdata:
            kwargs['flow_maps'] = mdata.pop('golem_flow_maps')
        if 'golem_arg_tags' in mdata:
            kwargs['arg_tags'] = mdata.pop('golem_arg_tags')
        if 'golem_repository' in mdata:
            kwargs['repository'] = mdata.pop('golem_repository')
        if 'golem_output_templates' in mdata:
            kwargs['output_templates'] = mdata.pop('golem_output_templates')
        if 'golem_input_templates' in mdata:
            kwargs['input_templates'] = mdata.pop('golem_input_templates')
        if 'golem_query_templates' in mdata:
            kwargs['query_templates'] = mdata.pop('golem_query_templates')
        return cls(**kwargs)

    def _as_meta(self):
        meta = dict(self._metadata)
        meta['golem_version']  = str(GOLEM_VERSION)
        meta['golem_span']     = timedelta_iso(self.span)
        meta['golem_interval'] = timedelta_iso(self.interval)
        if self.suite:
            meta['golem_suite_name'] = self.suite
        if self.name:
            meta['golem_name'] = self.name
        if self._lag:
            meta['golem_lag'] = timedelta_iso(self._lag)
        if self._epoch:
            meta['golem_epoch'] = datetime_iso(self._epoch, self.precision())
        if self.realtime:
            meta['golem_realtime'] = self.realtime
        if self.repository:
            meta['golem_repository'] = self.repository
        if self.loops:
            meta['golem_loops'] = self.loops
        if self.tags:
            meta['golem_tags'] = self.tags
        if self.arg_tags:
            meta['golem_arg_tags'] = self.arg_tags
        if self.output_templates:
            meta['golem_output_templates'] = self.output_templates
        if self.input_templates:
            meta['golem_input_templates'] = self.input_templates
        if self.query_templates:
            meta['golem_query_templates'] = self.query_templates
        if self.flow_maps:
            meta['golem_flow_maps'] = self.flow_maps
        if self.golem_inputs:
            inputs = []
            for jin, spec in self.golem_inputs:
                jmeta = model._script_to_meta(jin)
                inputs.append([jmeta, spec])
            meta['golem_inputs'] = inputs
        return meta

    def __init__(self, span=None, interval=None,
                       name=None, suite_name=None, epoch=None,
                       lag=None, realtime=False, repository=None,
                       tags=None, arg_tags=None, loops=None,
                       flow_maps=None, golem_inputs=None,
                       output_templates=None, input_templates=None,
                       query_templates=None, _version=None, **kwargs):
        """
        Creates a new :class:`Golem` object from the various data that
        make up a golem script definition. This should never need to be
        used by anything outside of the :mod:`golem.model` module. See
        instead :func:`golem.model.parse_golem_metadata` for a way to
        retrieve golem script information from serialized metadata or
        existing scripts.
        """

        Script.__init__(self, **kwargs)

        self._version = _version

        self.name = name
        """
        The short name of this jool script, if any.
        """

        self.suite = suite_name
        """
        The short name of this jool script's suite, if any.
        """

        self._epoch = None
        """
        The epoch which all time bins are relative to. Defaults to
        midnight of the first Monday after the standard unix epoch.
        """
        if epoch:
                self._epoch = times.make_datetime(epoch)

        self.interval = \
            times.make_timedelta(interval or self.default_interval)
        """
        A :class:`timedelta` representing the process interval
        of this :class:`Golem` instance.
        """

        self.span = times.make_timedelta(span or self.default_span)
        """
        A :class:`timedelta` representing the data window of
        this :class:`Golem` instance.
        """

        self.repository = repository
        """
        The default path, if any, for the output results data
        repository for this :class:`Golem` instance.
        """

        self.realtime = realtime or False
        """
        A boolean value indicating whether results for this
        :class:`Golem` script can be generated in real time
        or not. If true, forces a *lag* of 0.
        """

        self._lag = None
        if lag and not self.realtime:
            self._lag = times.make_timedelta(lag)

        if not isinstance(tags, dict):
            tags = dict(tags or ())
        self.tags = tags
        
        if not isinstance(arg_tags, dict):
            arg_tags = dict(arg_tags or ())
        self.arg_tags = arg_tags

        self.flow_maps = tuple(flow_maps or ())
        for x in self.flow_maps:
            name, params = x
            if isinstance(x, tuple) and isinstance(params, dict):
                continue
            maps = []
            for name, params in self.flow_maps:
                maps.append((name, dict(params)))
            self.flow_maps = tuple(flow_maps)
            break

        self.loops = tuple(loops or ())
        for item in self.loops:
            name, x = item
            vals, groups, group_name, sep = x
            if all(isinstance(y, tuple) for y in (item, x, vals)) and \
                    not isinstance(vals, basestring) and \
                    not (groups and not group_name) and \
                    (groups and isinstance(groups, dict)):
                continue
            loops = []
            for name, (vals, groups, group_name, sep) in self.loops:
                if isinstance(vals, basestring):
                    vals = (vals,)
                if groups:
                    if not group_name:
                        group_name = name + '_group'
                    if not isinstance(groups, dict):
                        groups = dict(groups)
                loops.append((name, (vals, groups, group_name, sep)))
            self.loops = tuple(loops)
            break

        self.input_templates = tuple(input_templates or ())
        for x in self.input_templates:
            name, t, spec = x
            if isinstance(x, tuple) and (isinstance(t, tuple) or callable(t)):
                continue
            templates = []
            for name, t, spec in self.input_templates:
                if not callable(t):
                    t = tuple(t)
                templates.append((name, t, spec))
            self.input_templates = tuple(templates)
            break

        self.output_templates = tuple(output_templates or ())
        for x in self.output_templates:
            if isinstance(x, tuple):
                continue
            templates = []
            for name, t, spec in self.output_templates:
                templates.append((name, t, spec))
            self.output_templates = tuple(templates)
            break

        self.query_templates = tuple(query_templates or ())
        for x in self.query_templates:
            if isinstance(x, tuple):
                continue
            templates = []
            for name, t, spec in self.query_templates:
                templates.append((name, t, spec))
            self.query_templates = tuple(templates)
            break

        self.golem_inputs = tuple(golem_inputs or ())

        self._validate_params()

    def using(self, name=Nada, suite_name=Nada,
                    span=Nada, interval=Nada, epoch=Nada,
                    lag=Nada,  realtime=Nada, repository=Nada,
                    tags=Nada, arg_tags=Nada, loops=Nada,
                    flow_maps=Nada, golem_inputs=Nada,
                    output_templates=Nada, input_templates=Nada,
                    query_templates=Nada):
        """
        Clones the current :class:`Golem` object, possibly replacing
        certain parameters. Available parameters correspond to those
        provided by :func:`Golem.__init__`.
        """
        # copy Script() details first
        kwargs = dict(
            script_path = self._path,
            params   = copy(self._params),
            outputs  = copy(self._outputs),
            metadata = copy(self._metadata),
            flow_params = self._flow_params,
            flow_params_require_pull = self._flow_params_require_pull)

        # primitives
        if name is Nada:
            name = self.name
        if suite_name is Nada:
            suite_name = self.suite
        if realtime is Nada:
            realtime = self.realtime
        if repository is Nada:
            repository = self.repository

        # potentially shared
        if interval is not Nada:
            kwargs['interval'] = interval
        if span is not Nada:
            kwargs['span'] = span
        if epoch is not Nada:
            kwargs['epoch'] = epoch
        if lag is not Nada:
            kwargs['lag'] = lag
        if tags is not Nada:
            kwargs['tags'] = tags
        if arg_tags is not Nada:
            kwargs['arg_tags'] = arg_tags
        if flow_maps is not Nada:
            kwargs['flow_maps'] = flow_maps
        if input_templates is not Nada:
            kwargs['input_templates'] = input_templates
        if output_templates is not Nada:
            kwargs['output_templates'] = output_templates
        if query_templates is not Nada:
            kwargs['query_templates'] = query_templates
        if loops is not Nada:
            kwargs['loops'] = loops
        if golem_inputs is not Nada:
            kwargs['golem_inputs'] = golem_inputs

        golem = self.__class__(name=name, suite_name=suite_name,
                               realtime=realtime, repository=repository,
                               **kwargs)

        if interval is Nada:
            golem.interval = self.interval
        if span is Nada:
            golem.span = self.span
        if epoch is Nada:
            golem._epoch = self._epoch
        if lag is Nada:
            golem._lag = self._lag
        if tags is Nada:
            golem.tags = self.tags
        if arg_tags is Nada:
            golem.arg_tags = self.arg_tags
        if loops is Nada:
            golem.loops = self.loops
        if flow_maps is Nada:
            golem.flow_maps = self.flow_maps
        if input_templates is Nada:
            golem.input_templates = self.input_templates
        if output_templates is Nada:
            golem.output_templates = self.output_templates
        if golem_inputs is Nada:
            golem.golem_inputs = self.golem_inputs
        if query_templates is Nada:
            golem.query_templates = self.query_templates
        if loops is Nada:
            golem.loops = self.loops
        return golem

    def _validate_params(self):
        seen = set()
        def _check(n):
            if n in seen:
                script_error = GolemScriptError(
                    "multiple instances of name '%s'" % n)
                raise script_error
            seen.add(n)
        if self.interval <= NULL_DELTA:
            raise ValueError("interval must be > 0")
        if self.span <= NULL_DELTA:
            raise ValueError("span must be > 0")
        for name in self.tags:
            _check(name)
        for name in self.arg_tags:
            _check(name)
        for name, (vals, _, group_name, _) in self.loops:
            _check(name)
            if group_name:
                _check(group_name)
                if name == group_name:
                    script_error = GolemScriptError(
                        "name and group_name collide '%s'" % name)
                    raise script_error
        for name in (x[0] for x in self.output_templates):
            _check(name)
        for name in (x[0] for x in self.input_templates):
            _check(name)
        for name in (x[0] for x in self.query_templates):
            _check(name)
        for jin, spec in self.golem_inputs:
            for name in (x[0] for x in jin.output_templates):
                _check(name)
            join = spec.get('join', ())
            diff = set(join).difference(x[0] for x in jin.loops)
            if diff:
                script_error = GolemScriptError(
                    "invalid join %s to %s: %s" \
                        % (jin.name, self.name, tuple(sorted(diff))))
                raise script_error
        for name, fmap in self.flow_maps:
            _check(name)
            for v in fmap.values():
                if v not in seen:
                    script_error = GolemScriptError(
                        "invalid flow map label '%s'" % v)
                    raise script_error

    def select(self, loop, vals):
        """
        Clones the current :class:`Golem` object, restricting the
        specified loop to the provided values. An exception is thrown
        if any of the provided values are not present in the loop's
        current values.
        """
        loops = list(self.loops)
        for i, (name, (v, gr, gn, sep)) in enumerate(loops): 
            if name != loops:
                continue
            if set(vals).difference(v):
                rem = ','.join(set(vals).difference(v))
                error = ValueError(
                    "unknown values in loop '%s' : %s" % (loop, rem))
                raise error
            loops[i] = (name, (vals, gr, gn, sep))
            return self.using(loops=loops)
        error = ValueError("unknown loop '%s'" % loop)
        raise error

    @property
    def epoch(self):
        """
        A :class:`datetime <datetime.datetime>` instance representing
        the epoch for aligning various time bins such as intervals and
        spans. This is primarily useful for aligning these bins to a
        particular day of the week. By default, bins align to Monday
        within any given week.
        """
        e = self._epoch or self.default_epoch
        return times.bin_datetime(self.interval, e)

    @property
    def lag(self):
        """
        A :class:`timedelta`
        """
        if self.realtime:
            return NULL_DELTA
        else:
            return self._lag or self.default_lag

    def precision(self):
        """
        Returns a precision value as defined in :mod:`netsa.data.times`
        (e.g. ``netsa.data.times.DATETIME_DAY``) based on the apparent
        precision of the *interval* and *span* of this
        :class:`Golem` instance.
        """
        if self.interval.microseconds or self.span.microseconds:
            if self.interval.microseconds % 1000 \
                    or self.span.microseconds % 1000:
                return DATETIME_USEC
            else:
                return DATETIME_MSEC
        elif self.interval.seconds or self.span.seconds:
            if not (self.interval.seconds % 3600 or self.span.seconds % 3600):
                return DATETIME_HOUR
            elif not (self.interval.seconds % 60 or self.span.seconds % 60):
                return DATETIME_MINUTE
            else:
                return DATETIME_SECOND
        else:
            return DATETIME_DAY

    def _map_outputs(self, label_map):
        lmap = dict(label_map)
        outs = []
        for name, template, spec in self.output_templates:
            if name in lmap:
                spec = dict(spec)
                spec['oname'] = name
                outs.append((lmap.pop(name), template, spec))
            else:
                continue
        if lmap:
            script_error = GolemScriptError(
                "unknown golem outputs for '%s': '%s'" \
                    % (self.name, ','.join(sorted(lmap))))
            raise script_error
        return self.using(output_templates=outs)

    def _date_bin(self, date):
        return times.bin_datetime(self.interval, date, self.epoch)

    def _horizon_bin(self, horizon):
        true_hzn = horizon - self.lag
        hzn = self._date_bin(true_hzn)
        if not self.realtime:
            while hzn + self.interval >= true_hzn:
                hzn -= self.interval
        return hzn
