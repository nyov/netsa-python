# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import netsa, netsa.script

__version__ = netsa.find_version(__file__)

from netsa.script      import *
from netsa.script      import catalog
from netsa.util        import shell
from netsa.data        import times
from netsa             import json
from netsa.data.format import datetime_iso, datetime_iso_basic, \
                              datetime_silk, timedelta_iso
from netsa.files       import get_temp_file_name

import sys, os, re, itertools, tempfile, atexit
from datetime import datetime, timedelta
from glob import glob

import netsa.util.compat

class GolemScriptError(ScriptError):
    pass

class GolemInitError(GolemScriptError):
    pass

class GolemUserError(UserError):
    pass

class GolemException(Exception):
    pass

class GolemInputMissing(GolemException):
    pass

class GolemPartialComplete(GolemException):
    pass

class GolemComplete(GolemException):
    pass

class GolemIgnore(GolemException):
    pass

class Nada(object):
    pass

def _make_timedelta(days=0, minutes=0, hours=0, weeks=0, allow_negative=False):
    delta = timedelta(days=days, minutes=minutes, hours=hours, weeks=weeks)
    if not delta or (not allow_negative and abs(delta) != delta):
        raise ValueError, "positive timedelta required"
    return delta

# model uses some of the above, so import after

import model

###

class GolemView(object):
    """
    A :class:`GolemView` object encapsulates a golem script model and is
    used to view and manipulate it in various ways. These different
    views are primarily accessed through the
    :meth:`loop <GolemView.loop>`, :meth:`outputs <GolemView.outputs>`,
    and :meth:`inputs <GolemView.inputs>` methods.

    Optional keyword arguments:

      *last_date*
        The interval containing this :class:`datetime <datetime.datetime>`
        object is the last to be considered for processing. (default:
        most recent)

      *first_date*
        The interval containing this :class:`datetime <datetime.datetime>`
        object is the first to be considered for processing. (default:
        *last_date*)
    """

    __slots__ = ('golem', '_first_date', '_last_date',
                          '_inputs', '_outputs')

    today = times.make_datetime(datetime.now())

    def __init__(self, golem, first_date=None, last_date=None):
        if golem is Nada:
            raise RuntimeError

        self.golem = golem
        """
        The golem script model which this view manipulates.
        """

        self._first_date, self._last_date = \
            self._normalize_dates(first_date, last_date)
        self._inputs = self._outputs = None

    def using(self, golem=Nada, first_date=Nada, last_date=Nada):
        """
        Return a copy of this :class:`GolemView` object, optionally
        using new values for the following keyword arguments:

        *golem*
          Use a different golem script model.

        *first_date*
          Select a different starting time bin based on the provided
          :class:`datetime <datetime.datetime>` object.

        *last_date*
          Select a different ending time bin based on the provided
          :class:`datetime <datetime.datetime>` object.
        """
        if not golem or golem is Nada:
            golem = self.golem
        if first_date is Nada:
            first_date = self._first_date
        if last_date is Nada:
            last_date = self._last_date
        return self.__class__(golem,
            first_date=first_date, last_date=last_date)

    def using_span(self, days=0, minutes=0, hours=0, weeks=0):
        """
        Return a new :class:`GolemView` object containing a golem object
        with the given span, specified with keywords
        weeks/days/hours/minutes.
        """
        span = _make_timedelta(days=days, minutes=minutes,
                               hours=hours, weeks=weeks)
        return self.using(golem=self.golem.using(span=span))

    def _current_bin(self):
        return self.golem._horizon_bin(self.today)

    def _normalize_dates(self, first_date=None, last_date=None):
        if first_date:
            first_date = times.make_datetime(first_date)
        if last_date:
            last_date = times.make_datetime(last_date)
        now_bin = self._current_bin()
        if not last_date:
            last_date = now_bin
        last_bin = self.golem._date_bin(last_date)
        if last_bin > now_bin:
            last_bin = last_date = now_bin
        if not first_date:
            first_date = last_date
        first_bin = self.golem._date_bin(first_date)
        if first_bin > now_bin:
            first_bin = first_date = now_bin
        if first_bin > last_bin:
            fs = datetime_iso(first_bin, self.golem.precision())
            ls = datetime_iso(last_bin,  self.golem.precision())
            param_error = ParamError('first bin', fs,
                "exceeds last bin '%s'" % ls)
            raise param_error
        return first_date, last_date

    @property
    def first_bin(self):
        """
        A :class:`datetime <datetime.datetime>` object representing
        the first processing interval for this view, as determined by
        the *first_date* and *last_date* parameters during construction.
        Defaults to :attr:`last_bin`.
        """
        return self.golem._date_bin(self._first_date)

    @property
    def last_bin(self):
        """
        A :class:`datetime <datetime.datetime>` object representing the
        last processing interval for this view, as determined by the
        *last_date* and *first_date* parameters during construction.
        Defaults to the 'most recent' interval that does not overlap
        into the future, taking into account :func:`lag <set_lag>`.
        """
        return self.golem._date_bin(self._last_date)

    @property
    def start_date(self):
        """
        A :class:`datetime <datetime.datetime>` object representing the
        beginning of the first data span covered by this view. Spans can
        be larger (or smaller) than the defined interval, so this value
        is not necessarily equal to :attr:`first_bin`.
        """
        return self.first_bin + self.golem.interval - self.golem.span

    @property
    def end_date(self):
        """
        A :class:`datetime <datetime.datetime>` object representing the
        end of the last data span covered by this view. If the span
        is less than or equal to the interval, this is equal to
        ``last_bin + interval - 1 microsecond``, otherwise it is equal
        to ``last_bin + span - 1 microsecond``.
        """
        if self.golem.span >= self.golem.interval:
            return self.last_bin + \
                   self.golem.interval - timedelta(microseconds=1)
        else:
            return self.last_bin + \
                   self.golem.span - timedelta(microseconds=1)

    def bin_dates(self):
        """
        Provide an iterator over :class:`datetime <datetime.datetime>`
        objects representing all processing intervals represented by
        this view.
        """
        step_bin = self.first_bin
        last_bin = self.last_bin
        while step_bin <= last_bin:
            yield step_bin
            step_bin += self.golem.interval

    def bins(self):
        """
        Provide an iterator over :class:`GolemView` objects for each
        interval represented by this view.
        """
        if self.first_bin == self.last_bin:
            yield self
        else:
            for date in self.bin_dates():
                yield self.using(first_date=date, last_date=date)

    def group_by(self, *keys):
        """
        Returns an iterator that yields a tuple with a primary key and
        :class:`GolemView` object grouped by the provided keys. Each
        primary key is a tuple containing the current values of the keys
        provided to :meth:`group_by`. Iterating over the provided
        view objects will resolve any remaining loops if any remain
        that were not used for the provided key.
        """
        diff = set(keys).difference([x[0] for x in self.golem.loops])
        if diff:
            raise KeyError, "unknown keys %s" % str(tuple(diff))
        kloops = []
        vloops = []
        kgroups = {}
        kgnames = {}
        for entry in self.golem.loops:
            if entry[0] in keys:
                k, (v, g, n, s) = entry
                kloops.append(v)
                kgroups[k] = g
                kgnames[k] = n
            else:
                vloops.append(entry)
        vloops = tuple(vloops)
        for pkey in itertools.product(*kloops):
            loops = []
            for pk, pv in zip(keys, pkey):
                loops.append((pk, ((pv,), kgroups[pk], kgnames[pk], s)))
            # break containment on the altar of efficiency
            golem = self.golem.using()
            golem.loops = vloops + tuple(loops)
            yield pkey, self.using(golem=golem)

    def by_key(self, key):
        """
        Similar to :meth:`group_by` but takes only a single key as an
        argument. Returns and iterator that yields view objects for each
        value of the key; iterating over the provided view objects will
        resolve any remaining loops, if present.
        """
        for _, gv in self.group_by(key):
            yield gv

    def product(self):
        """
        Fully resolve the loops defined within this view. The 'outer'
        loop is always over intervals, followed by any other loops in
        the order in which they were defined. Each view thus provided is
        therefore fully resolved, with no loops remaining.
        """
        for gview in self.bins():
            if gview.golem.loops:
                labels = [x[0] for x in gview.golem.loops]
                for _, gv in gview.group_by(*labels):
                    yield gv
            else:
                yield gview

    def bin_count(self):
        """
        Return the number of intervals represented by this view, as
        defined by :attr:`first_bin` and :attr:`last_bin`.
        """
        w = self.last_bin - self.first_bin
        q, r = times.divmod_timedelta(w, self.golem.interval)
        return q + 1

    def loop_count(self):
        """
        Return the number of non-interval iterations represented by this
        view that are produced by resolving any defined loops.
        """
        if self.golem.loops:
            if len(self.golem.loops) == 1:
                return len(self.golem.loops[0][1][0])
            else:
                return reduce(lambda x, y: x*y,
                              (len(x[1][0]) for x in self.golem.loops))
        else:
            return 0

    def __len__(self):
        """
        Return the number of fully-resolved iterations represented by
        this view, over intervals as well as any defined loops.
        """
        return self.bin_count() * self.loop_count()

    def __iter__(self):
        """
        Iterates over the views returned by the :meth:`product` method.
        """
        return self.product()

    def sync_to(self, other, count=None, offset=None,
                cover=False, trail=False):
        """
        Given another :class:`GolemView` object, return a version of
        *self* that has been synchronized to the given view object.

        Optional keyword arguments:

          *count*
            Synchronize to this many intervals of the given object
            (default: 1)

          *offset*
            Synchronize to this many interval offsets behind the given
            object (default: 0)

          *cover*
            Calculate a *count* necessary to cover all intervals
            represented by the given object (overrides *count* and
            *offset*)

          *trail*
            Force the *end_date* of the new view to always be less than
            or equal to the *end_date* of the given view.
        """

        gv = self.using(first_date=other.end_date, last_date=other.end_date)
        golem = gv.golem
        while trail and gv.end_date > other.end_date:
            first_date = gv._first_date - golem.interval
            last_date  = gv._last_date  - golem.interval
            gv = gv.using(first_date=first_date, last_date=last_date)
        if cover:
            gv = gv.using(first_date=other.start_date)
        if offset:
            first_bin = gv.first_bin - abs(offset or 0) * golem.interval
            last_bin  = gv.last_bin  - abs(offset or 0) * golem.interval
            gv = gv.using(first_date=first_bin, last_date=last_bin)
        if count:
            first_bin = gv.first_bin - golem.interval * (abs(count) - 1)
            gv = gv.using(first_date=first_bin)
        return gv

    def loop(self):
        """
        Return a :class:`GolemTags` object representing this view.
        """
        return GolemTags(
            golem      = self.golem,
            first_date = self._first_date,
            last_date  = self._last_date,
        )

    def outputs(self):
        """
        Return a :class:`GolemOutputs` object representing this view.
        """
        return GolemOutputs(
            golem      = self.golem,
            first_date = self._first_date,
            last_date  = self._last_date,
        )

    def inputs(self):
        """
        Return a :class:`GolemInputs` object representing this view.
        """
        return GolemInputs(
            golem      = self.golem,
            first_date = self._first_date,
            last_date  = self._last_date,
        )

    def tags(self):
        """
        Return a dictionary of resolved tags for this view.
        """
        return self.loop().tags()

    def _get_io(self, label):
        if not self._inputs:
            self._inputs = set()
            self._inputs.update(x[0] for x in self.golem.input_templates)
            for gin, spec in self.golem.golem_inputs:
                self._inputs.update(x[0] for x in gin.output_templates)
        if label in self._inputs:
            return self.inputs()
        if not self._outputs:
            self._outputs = set()
            self._outputs.update(x[0] for x in self.golem.output_templates)
        if label in self._outputs:
            return self.outputs()
        error = GolemScriptError("unknown label '%s'" % label)
        raise error

    def by_output(self):
        for x in self.golem.output_templates:
            golem = self.golem.using(output_templates = [x])
            yield self.using(golem=golem)

    def _as_self_query(self, repository=None):
        # self-input
        spec = dict(
            join     = dict((x[0], x[0]) for x in self.golem.loops),
            required = False,
            offset   = 0,
        )
        golem = self.golem.using(
            repository       = repository,
            golem_inputs     = [(self.golem, spec)],
            input_templates  = None,
            output_templates = None,
        )
        return self.using(golem=golem)

class GolemOutputs(GolemView):
    """
    A :class:`GolemOutputs` object is used to examine resolved output
    templates, either for a specific iteration or aggregated across
    multiple iterations.
    """

    def _expand(self, glob_it=True):
        labels = []
        meta   = dict()
        for name, _, spec in self.golem.output_templates:
            labels.append(name)
            meta[name] = dict(spec)
        for group, members in self.golem.output_groups:
            meta[group] = {}
        outs = {}
        for gv in self.loop().product():
            for k, args in gv._output_tags(glob_it=glob_it):
                if k not in outs:
                    outs[k] = [gv, args]
                else:
                    outs[k][-1] += args
        for label, (gv, args) in outs.iteritems():
            if not args:
                error = GolemScriptError(
                    "output mapping failure for '%s' in '%s'" \
                        % (label, self.golem.name))
                raise error
        for x in labels:
            gv, args = outs[x]
            yield gv, x, meta[x], args

    def expand(self):
        """
        Returns a :class:`GolemArgs` object representing all resolved
        output templates for the current view.
        """
        outputs = GolemArgs()
        for args in (x[-1] for x in self._expand()):
            outputs += args
        return outputs

    def __len__(self):
        """
        Return the number of resolved output templates for the
        current view.
        """
        return self.expand().__len__()
    __nonzero__ = __len__
    __bool__ = __len__

    def __iter__(self):
        """
        Iterate over each resolved output template for the current view.
        """
        return self.expand()


class GolemInputs(GolemView):
    """
    A :class:`GolemInputs` object is used to examine resolved input
    templates, either for a specific iteration or aggregated across
    multiple iterations.
    """

    __slots__ = ('_joined_inputs',)

    def members(self, *select):
        """
        Iterate over each golem script that provides inputs for
        this golem script, returning each as a synchronized
        :class:`GolemOutputs` object.
        """
        try:
            inputs = self._joined_inputs
        except AttributeError:
            # go ahead and cache the joined loops
            inputs = self._joined_inputs = tuple(self._join_inputs())
            new_gin = list(self.golem.golem_inputs)
            for i, (_, spec) in enumerate(new_gin):
                new_gin[i] = (inputs[i].golem, spec)
            self.golem = self.golem.using(golem_inputs=new_gin)
        if select:
            select = set(select)
            for gv in inputs:
                outs = set(x[0] for x in gv.golem.output_templates)
                if select.intersection(outs):
                    yield gv
                    select.difference_update(outs)
            if select:
                rem = ','.join(select)
                error = ValueError("unknown input selection '%s'" % rem)
                raise error
        else:
            for gv in inputs:
                yield gv.outputs()

    def _join_inputs(self):
        sloops = None
        for gin, spec in self.golem.golem_inputs:
            join   = spec.get('join',   None)
            cover  = spec.get('cover',  None)
            count  = spec.get('count',  None)
            offset = spec.get('offset', None)
            if join:
                if not sloops:
                    sloops = dict(self.golem.loops)
                loops = []
                for entry in gin.loops:
                    ok, ol = entry
                    if ok in join:
                        sk = join[ok]
                        sv, sg = sloops[sk][0:2]
                        ov = ol[0]
                        offer = set(ov)
                        for v in sv:
                            if v in offer:
                                offer.remove(v)
                            elif sg and offer.issuperset(sg[v]):
                                offer.difference_update(sg[v])
                            else:
                                error = GolemScriptError(
                                    "incomplete join '%s.%s' to"
                                    " '%s.%s': %s" \
                                    % (gin.name, ok, self.golem.name, sk, v))
                                raise error
                        nv = tuple(filter(lambda x: x not in offer, ov))
                        entry = (ok, (nv,) + ol[1:])
                    loops.append(entry)
                gin = gin.using(loops=loops)
            gv = self.using(golem=gin)
            gv = gv.sync_to(self, cover=cover, count=count, offset=offset)
            scope = abs(gin.output_templates[0][-1].get('scope', 0))
            if scope > 1:
                scope = gin.interval * scope
                first_date = gv._first_date - (scope - gin.interval)
                gv = gv.using(first_date=first_date)
            yield gv

    def _from_input_templates(self, glob_it=True):
        if self.golem.input_templates:
            for name, t, spec in self.golem.input_templates:
                nspec = dict(spec)
                join = {}
                for loop in (x[0] for x in self.golem.loops):
                    join[loop] = loop
                gout = self.golem.using(output_templates=[(name, t, {})])
                gin = self.golem.using(
                    input_templates=[],
                    golem_inputs=[(gout, nspec)]
                )
                gvnew = self.using(golem=gin)
                for gv, label, meta, args in \
                        gvnew._expand_members(glob_it=glob_it):
                    meta["source_name"] = nspec.get("source_name", "unknown")
                    yield label, meta, args

    def _expand_members(self, glob_it=True):
        for jio in self.members():
            for gv, label, meta, args in jio._expand(glob_it=glob_it):
                if not args:
                    error = GolemScriptError(
                        "input mapping failure for '%s.%s' in '%s'"
                            % (gv.golem.name, label, self.golem.name))
                    raise error
                yield gv, label, meta, args

    def _expand(self, glob_it=True):
        for gv, label, meta, args in self._expand_members(glob_it=glob_it):
            yield gv, label, meta, args
        for label, meta, args in self._from_input_templates(glob_it=glob_it):
            yield self, label, meta, args

    def expand(self):
        """
        Returns a :class:`GolemArgs` object representing all resolved
        input templates for the current view.
        """
        inputs = GolemArgs()
        for args in (x[-1] for x in self._expand()):
            inputs += args
        return inputs

    def __len__(self):
        """
        Return the number of resolved input templates for the
        current view.
        """
        return len(self.expand())
    __nonzero__ = __len__
    __bool__ = __len__

    def __iter__(self):
        """
        Iterate over each resolved input template for the current view.
        """
        return self.expand()


class GolemTags(GolemView):
    """
    A :class:`GolemTags` object is used to examine resolved template
    tags produced by looping over intervals and other defined loops.
    """

    _input_cache = {}

    def _basic_tags(self):
        first_bin  = self.first_bin
        last_bin   = self.last_bin
        interval   = self.golem.interval
        span       = self.golem.span
        start_date = (first_bin + interval) - span
        end_date   = last_bin + (interval - timedelta(microseconds=1))
        next_date  = last_bin + interval
        prec = self.golem.precision()
        tags = {}

        tags['golem_name'] = self.golem.name
        if self.golem.suite:
            tags['golem_suite'] = self.golem.suite
        elif self.golem.name:
            tags['golem_suite'] = self.golem.name
        tags['golem_repository'] = self.golem.repository
        tags['golem_home'] = get_home()

        tags['golem_span']              = span
        tags['golem_interval']          = interval
        tags['golem_span_iso']          = timedelta_iso(span)
        tags['golem_interval_iso']      = timedelta_iso(interval)

        tags['golem_bin_date']          = first_bin
        tags['golem_bin_year']          = first_bin.year
        tags['golem_bin_month']         = first_bin.month
        tags['golem_bin_day']           = first_bin.day
        tags['golem_bin_hour']          = first_bin.hour
        tags['golem_bin_second']        = first_bin.second
        tags['golem_bin_microsecond']   = first_bin.microsecond

        tags['golem_start_date']        = start_date
        tags['golem_start_year']        = start_date.year
        tags['golem_start_month']       = start_date.month
        tags['golem_start_day']         = start_date.day
        tags['golem_start_hour']        = start_date.hour
        tags['golem_start_second']      = start_date.second
        tags['golem_start_microsecond'] = start_date.microsecond

        tags['golem_end_date']          = end_date
        tags['golem_end_year']          = end_date.year
        tags['golem_end_month']         = end_date.month
        tags['golem_end_day']           = end_date.day
        tags['golem_end_hour']          = end_date.hour
        tags['golem_end_second']        = end_date.second
        tags['golem_end_microsecond']   = end_date.microsecond

        tags['golem_next_bin_date']          = next_date
        tags['golem_next_bin_year']          = next_date.year
        tags['golem_next_bin_month']         = next_date.month
        tags['golem_next_bin_day']           = next_date.day
        tags['golem_next_bin_hour']          = next_date.hour
        tags['golem_next_bin_second']        = next_date.second
        tags['golem_next_bin_microsecond']   = next_date.microsecond

        tags['golem_bin_iso']   = datetime_iso(first_bin,  precision=prec)
        tags['golem_start_iso'] = datetime_iso(start_date, precision=prec)
        tags['golem_end_iso']   = datetime_iso(end_date,   precision=prec)
        tags['golem_next_bin_iso'] = datetime_iso(next_date,   precision=prec)

        tags['golem_bin_silk']   = datetime_silk(first_bin, precision=prec)
        tags['golem_start_silk'] = datetime_silk(start_date, precision=prec)
        tags['golem_end_silk']   = datetime_silk(end_date, precision=prec)
        tags['golem_next_bin_silk'] = datetime_silk(next_date, precision=prec)

        tags['golem_bin_basic']   = \
            datetime_iso_basic(first_bin,  precision=prec)
        tags['golem_start_basic'] = \
            datetime_iso_basic(start_date, precision=prec)
        tags['golem_end_basic']   = \
            datetime_iso_basic(end_date,   precision=prec)
        tags['golem_next_bin_basic']   = \
            datetime_iso_basic(next_date,   precision=prec)

        loopers = {}
        for k, (vals, g, n, s) in self.golem.loops:
            kvals = []
            nvals = []
            for v in vals:
                if g and v in g:
                    kvals.extend(g[v])
                    nvals.append(v)
                else:
                    kvals.append(v)
            if k in tags:
                error = GolemScriptError("tag collision '%s'" % k)
                raise error
            tags[k] = GolemArgs(*kvals, sep=s)
            if len(kvals) > 1:
                loopers[k] = kvals
            if nvals:
                if n in tags:
                    error = GolemScriptError("tag collision '%s'" % k)
                    raise error
                tags[n] = GolemArgs(*nvals, sep=s)
                if len(nvals) > 1:
                    loopers[n] = nvals

        order   = []
        resolve = set()
        for k, v in self.golem.tags.iteritems():
            if k in tags:
                error = GolemScriptError("tag collision '%s'" % k)
                raise error
            tags[k] = v
            if '%' in v:
                if k not in resolve:
                    resolve.add(k)
                    order.append(k)
                idx = order.index(k)
                for x in sorted(_analyze_templates(v)):
                    if x not in tags and x not in resolve:
                        resolve.add(x)
                        order.insert(idx, x)
        for k in order:
            tags[k] = tags[k] % tags

        for k, t in self.golem.arg_tags.iteritems():
            if loopers:
                atags = _analyze_templates(t)
                ltags = atags.intersection(loopers)
                if ltags:
                    tt = dict(tags)
                    v = GolemArgs()
                    for vk in itertools.product(*[loopers[x] for x in ltags]):
                        for pk, pv in zip(ltags, vk):
                            tt[pk] = pv
                        v += t % tt
                    tags[k] = v
                else:
                    tags[k] = GolemArgs(t % tags)
            else:
                tags[k] = GolemArgs(t % tags)

        return tags

    def _output_tags(self, tags=None, glob_it=True):
        if not tags:
            tags = self._basic_tags()
        output_group_map = {}
        output_group_args = {}
        for group, members in self.golem.output_groups:
            output_group_args[group] = GolemArgs()
            for member in members:
                output_group_map.setdefault(member, set())
                output_group_map[member].add(group)
        file_resource = GolemFileResource(self)
        for k, template, spec in self.golem.output_templates:
            resolved = template % tags
            if self.golem.repository:
                resolved = file_resource.repository_fmt_full(resolved)
            if glob_it:
                res = glob(resolved)
                if res:
                    resolved = res
                else:
                    resolved = [resolved]
            else:
                resolved = [resolved]
            args = GolemArgs(resolved)
            if k in output_group_map:
                for group in output_group_map[k]:
                    output_group_args[group] += args
            yield k, args
        for k, args in output_group_args.iteritems():
            yield k, args

    def tags(self):
        """
        Return a dictionary of resolved template tags for the current
        view (flattens tags across the loops that would result from
        invoking the :meth:`product <GolemView.product>` method).
        """

        tags = self._basic_tags()

        # add output tags (including a dictionary of all outputs)
        tags['golem_outputs'] = dict(self._output_tags(tags))
        tags.update(tags['golem_outputs'])

        # add input tags (including a dictionary of all inputs)
        tags['golem_inputs'] = {}
        for _, label, _, args in self.inputs()._expand():
            tags[label] = args
            tags['golem_inputs'][label] = args
        for name, members in self.golem.input_groups:
            if name not in tags:
                tags[name] = GolemArgs()
            for m in members:
                tags[name] += tags[m]

        # bind flow maps
        for name, flow_map in self.golem.flow_maps:
            kwargs = {}
            for fk, pk in flow_map.iteritems():
                v = tags.get(pk, pk)
                if fk == 'sensors':
                    if isinstance(v, basestring):
                        v = v.split(',')
                kwargs[fk] = v
                if 'start_date' not in kwargs:
                    kwargs['start_date'] = tags['golem_start_date']
                if 'end_date' not in kwargs:
                    kwargs['end_date'] = tags['golem_end_date']
            tags[name] = Flow_params(**kwargs)

        # include the view
        tags['golem_view'] = self

        return tags

    def __iter__(self):
        """
        Iterate over each view returned by the :meth:`product
        <GolemView.product` method, yielding a dictionary of fully
        resolved template tags.
        """
        for gv in self.product():
            yield gv.tags()


class GolemArgs(object):
    """
    A :class:`GolemArgs` object encapsulates a list of resolved input
    or output templates destined to be used as a parameter in a tags
    dictionary. The constructor takes any number of strings, or string
    iterators, and flattens them into a unique sorted tuple. Individual
    items can be accessed and iterated over like a tuple. One keyword
    argument is accepted, *sep*, which will be used to join the
    items when rendered as a string. It defaults to a single space.

    If a space is the separator, the object will resolve to a string of
    space-separated values and will properly resolve when passed to the
    :mod:`netsa.util.shell` module for command and pipeline execution.

    Note that some file-related python functions (such as :func:`open`)
    will complain if passed a single-value :class:`GolemArgs` object
    (representing a single file name) without having first explicitly
    converted it to a string via :func:`str` or index 0.

    The length of a :class:`GolemArgs` object represents the number
    of items it contains. These can be accessed via an index like a
    list. Two objects can be added and subtracted from one another,
    as with sets.
    """

    __slots__ = ['items', 'members', 'sep']

    def __init__(self, *items, **kwargs):
        self.items = []
        self.members = set()
        if 'sep' in kwargs:
            self.sep = kwargs.pop('sep') or ''
        else:
            self.sep = ' '
        if kwargs:
            raise TypeError("invalid keyword args: %s" % ', '.join(kwargs))
        for item in items:
            try:
                if isinstance(item, basestring):
                    item = [item]
                for x in item:
                    if x not in self.members:
                        self.members.add(x)
                        self.items.append(x)
            except TypeError:
                if item not in self.members:
                    self.members.add(item)
                    self.items.append(item)

    def __str__(self):
        return self.sep.join("%s" % x for x in self)

    def __unicode__(self):
        return unicode(str(self))

    def __hash__(self):
        return str(self).__hash__()

    def __len__(self):
        return len(self.items)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        # loop tags are GolemArgs and get compared to strings
        return str(self) == str(other)

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        # loop tags are GolemArgs and get compared to strings
        return str(self) != str(other)

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__class__(self.items + other.items)

    def __iadd__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        for item in other.items:
            if item not in self.members:
                self.members.add(item)
                self.items.append(item)
        return self

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__class__(
            filter(lambda x: x not in other.members, self.items))

    def __isub__(self, other):
        other = self - other
        self.items = other.items
        self.members = other.members
        return self

    def __getitem__(self, idx):
        return self.items[idx]

    def __contains__(self, item):
        return item in self.members

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        return "netsa.script.golem.GolemArgs(%s)" \
            % ', '.join(repr(x) for x in self)

    def get_argument_list(self):
        # Bridge method for compatibility with the netsa.util.shell
        # Without this method, When there are multiple items, it would
        # by default put quotes around the items. For a single item, a
        # space would be inserted, i.e. "--items= item"
        if len(self.items) <= 1:
            raise AttributeError, "single argument, stringify"
        return self


### script config

_golem_view = None

def _view_using(golem=Nada, first_date=Nada, last_date=Nada, repository=Nada):
    if _golem_view is None:
        raise GolemInitError("view invoked outside of main()")
    return _golem_view.using(golem=golem,
                             first_date=first_date, last_date=last_date)

def _set_golem_view(golem=Nada, first_date=Nada, last_date=Nada):
    global _golem_view
    if golem is not Nada:
        if golem.interval != _golem_view.golem.interval and \
                first_date is Nada and last_date is Nada:
            # avoid horizon overruns when changing intervals
            first_date = last_date = None
        netsa.script._script = golem
    _golem_view = _view_using(golem=golem, first_date=first_date,
                              last_date=last_date)
    return _golem_view

def _set_golem(**kwargs):
    if _golem_view is None:
        raise GolemInitError("view invoked outside of main()")
    golem = _golem_view.golem.using(**kwargs)
    return _set_golem_view(golem=golem)

def _initialize_golem_view():
    global _golem_view
    _golem_view = GolemView(golem=model.Golem(script_path=get_script_path()))
    _set_golem_view(golem=_golem_view.golem)

### repository

def set_default_home(*paths):
    """
    Sets the default base path for this golem script in
    cases where the :envvar:`GOLEM_HOME` environment variable is not
    set.  Multiple arguments will be joined together as with
    :func:`os.path.join`.  If the provided path is relative, it is
    assumed to be relative to the directory in which script resides.

    The actual home path will be decided by the first available source
    in the following order:

      1) The :envvar:`GOLEM_HOME` environment variable
      2) The default home if set by this function
      3) The directory in which the script resides

    Subsequent path settings (e.g. :func:`set_repository`) will be
    relative to the script home if they are not absolute paths.
    """
    _cfg.home = os.path.join(*paths)
    return _cfg.home

def set_repository(*paths):
    """
    Sets the default path for the output results data repository.
    Multiple arguments will be joined together as with
    :func:`os.path.join`. Output results will be stored in this
    directory or in a subdirectory beneath, depending on how each output
    template is specified. Relative paths are considered to be relative
    to the ``home`` path.
    """
    _cfg.repository = os.path.join(*paths)
    return _cfg.repository

def get_script_path():
    """
    Returns the normalized absolute path to this script.
    """
    return os.path.normpath(os.path.abspath(sys.argv[0]))

def get_script_dir():
    """
    Returns the normalized absolute path to the directory in which this
    script resides.
    """
    return os.path.dirname(get_script_path())

def get_home():
    """
    Returns the current value of this script's home path if it has been
    set. Otherwise, defaults to the contents of the :envvar:`GOLEM_HOME`
    environment variable (if set), or finally, the directory in which
    this script resides.
    """
    return _cfg.get_home()

def get_repository():
    """
    Returns the current path for this script's data output repository,
    or ``None`` if not set.
    """
    return _cfg.get_repository()

### repository subsystem

class GolemResource(object):

    __slots__ = ('gview',)

    resource_cache = {}
    audit_cache = {}
    proc_cache = {}

    def __init__(self, gview, name=None):
        if not isinstance(gview, GolemView):
            raise TypeError("GolemView object required")
        if name:
            gview = gview.using(golem=gview.golem.using(name=name))
        self.gview = gview

    @property
    def descriptor(self):
        return self.gview.golem.repository

    @property
    def name(self):
        return self.gview.golem.name

    def _get_audit_cache(self, label):
        gcache = self.audit_cache.setdefault(self.name, {})
        return gcache.setdefault(label, {})

    def clear_audit_cache(self, label):
        gcache = self.audit_cache.setdefault(self.name, {})
        if label not in gcache:
            raise KeyError("unknown label %s" % repr(label))
        gcache[label] = {}

    def _get_proc_cache(self, label, default=None):
        pcache = self.proc_cache.setdefault(self.name, {})
        if default is None:
            default = {}
        return pcache.setdefault(label, default)

    def clear_proc_cache(self, label):
        pcache = self.proc_cache.setdefault(self.name, {})
        if label not in pcache:
            raise KeyError("unknown label %s" % repr(label))
        pcache[label] = {}

    def audit_expand(self, labels=None, glob_it=False):
        if labels and isinstance(labels, basestring):
            labels = set([labels])
        for gv, label, meta, args in self.gview._expand(glob_it=glob_it):
            if labels and label not in labels:
                continue
            r = GolemFileResource(gv, name=meta.get("source_name", None))
            lc = r._get_audit_cache(label)
            new_args = []
            for item in args:
                if item not in lc:
                    new_args.append(item)
            yield r, label, r.audit, args, new_args

    def audit_all(self):
        tags = self.gview.loop()._basic_tags()
        for r, label, audit, args, new_args in self.audit_expand():
            lc = r._get_audit_cache(label)
            if args:
                if new_args:
                    lc.update(audit(label, new_args, tags))
                for item in args:
                    yield r, label, lc[item], item, tags
            else:
                yield r, label, None, None, tags

    def audit_all_by_label(self):
        tags = self.gview.loop()._basic_tags()
        for r, label, audit, raw_args, new_args in self.audit_expand():
            lc = r._get_audit_cache(label)
            args = GolemArgs()
            miss = GolemArgs()
            if raw_args:
                if new_args:
                    lc.update(audit(label, new_args, tags))
                for item in raw_args:
                    if item in lc and lc[item]:
                        args += item
                    else:
                        miss += item
            yield r, label, args, miss, tags

    def audit_by_bin(self):
        for rbin in (self.__class__(x) for x in self.gview.bins()):
            tags = rbin.gview.loop()._basic_tags()
            for r, label, audit, args, new_args in self.audit_expand():
                lc = r._get_audit_cache(label)
                if args:
                    if new_args:
                        lc.update(audit(label, new_args, tags))
                    for item in args:
                        yield r, label, lc[item], item, tags
                else:
                    yield r, label, None, None, tags

    def audit_by_label(self, labels):
        tags = self.gview.loop()._basic_tags()
        labels = labels or set()
        if isinstance(labels, basestring):
            labels = [labels]
        labels = set(labels)
        found  = set()
        for r, label, audit, raw_args, new_args in self.audit_expand():
            found.add(label)
            if labels and label not in labels:
                continue
            lc = r._get_audit_cache(label)
            if raw_args:
                if new_args:
                    lc.update(audit(label, new_args, tags))
                for item in raw_args:
                    yield r, label, lc[item], item, tags
            else:
                yield r, label, None, None, tags
        if labels.difference(found):
            diff = labels.difference(found)
            diff = ', '.join(sorted(diff))
            error = GolemScriptError("unknown label %s" % diff)
            raise error

    def purge_output(self):
        rsrc = self.__class__(self.gview.outputs())
        tags = self.gview.loop()._basic_tags()
        hits = GolemArgs()
        misses = GolemArgs()
        dirs = set()
        for r, label, audit, args, new_args in \
                self.audit_expand(glob_it=True):
            lc = r._get_audit_cache(label)
            items = []
            if args and new_args:
                lc.update(audit(label, new_args, tags))
            for item in args:
                items.append((item, lc[item]))
            r.purge_output_items(items)
            for item, _ in items:
                lc[item] = None

    def prepare_output(self, overwrite=False, zap_empty=True, create=True):
        rsrc = self.__class__(self.gview.outputs())
        tags = self.gview.loop()._basic_tags()
        hits = GolemArgs()
        misses = GolemArgs()
        for r, label, audit, args, new_args in \
                self.audit_expand(glob_it=True):
            lc = r._get_audit_cache(label)
            items = []
            if args and new_args:
                lc.update(audit(label, new_args, tags))
            for item in args:
                items.append((item, lc[item]))
            h, m = r.prepare_output_items(label, items, overwrite=overwrite,
                                          zap_empty=zap_empty, create=create)
            hits += h
            misses += m
        return hits, misses

    def finalize_output(self, zap_empty=True):
        rsrc = self.__class__(self.gview.outputs())
        tags = self.gview.loop()._basic_tags()
        for r, label, audit, args, new_args in self.audit_expand():
            pc = r._get_proc_cache(label)
            for item in args:
                if item in pc:
                    del pc[item]
            lc = r._get_audit_cache(label)
            for item in args:
                if item in lc:
                    del lc[item]
        for r, label, audit, args, new_args in self.audit_expand():
            pc = r._get_proc_cache(label)
            args = filter(lambda x: x not in pc, args)
            if not args:
                continue
            items = []
            if args and new_args:
                lc.update(audit(label, new_args, tags))
            for item in args:
                if item in pc:
                    continue
                items.append((item, lc[item]))
            cc = 0
            for item, status in items:
                if status or (status == 0 and not zap_empty):
                    pc.add(item)
                cc += 1
            r.finalize_output_items(label, items, zap_empty=zap_empty)

    def is_complete(self):
        o = self.gview.outputs()
        if o:
            r = self.__class__(o)
            return all(x[2] for x in r.audit_all())
        else:
            return False

    def contains(self, item):
        return False

    def repository_fmt_rel(self, item, other=None):
        return item

    def repository_fmt_full(self, item):
        return item

    def repository_fmt(self, item, verbose=False, prefix=None):
        if prefix and not verbose:
            if item.startswith(prefix) and item != prefix:
                item = item.split(prefix, 1)[1]
        return item

    def repository_exists(self):
        return NotImplemented

    def audit(self, label, args, tags):
        return NotImplemented

    def copy_query_result(self, src_tag, tgt_tag, tags):
        return NotImplemented

    def prepare_output_items(self, label, items, overwrite=False,
                             zap_empty=True, create=True):
        return NotImplemented

    def purge_output_items(self, items):
        return NotImplemented

    def finalize_output_items(self, label, items, zap_empty=True):
        return NotImplemented


# file-specific operations

class GolemFileResource(GolemResource):

    def audit(self, label, args, tags):
        for f in args:
            f = self.repository_fmt_full(f)
            files = glob(f)
            if files:
                status = 0
                for fg in files:
                    status += os.path.getsize(fg)
            else:
                status = None
            if files and not status:
                status = True
            yield f, status

    def repository_exists(self):
        if self.gview.golem.repository:
            return os.path.isdir(self.gview.golem.repository)
        else:
            return False

    def repository_contains(self, path, base=None):
        if base is None:
            base = self.gview.golem.repository
        abs_p = os.path.normpath(base)
        abs_o = os.path.normpath(os.path.abspath(path))
        cp = os.path.commonprefix([abs_p, abs_o])
        return abs_o.startswith(cp)

    def repository_fmt_rel(self, item, base=None):
        if base is None:
            base = os.path.abspath(self.gview.golem.repository)
        if not os.path.isabs(item):
            item = os.path.normpath(os.path.join(base, item))
        rp = os.path.relpath(os.path.normpath(item), base)
        if len(rp) > len(item):
            return item
        else:
            return rp

    def repository_fmt_full(self, item):
        base = self.gview.golem.repository
        if base and not os.path.isabs(item):
            item = os.path.join(base, item)
            item = os.path.abspath(os.path.normpath(item))
        return item

    def repository_fmt(self, item, verbose=False):
        if not self.gview.golem.repository:
            return item
        if verbose > 1:
            item = self.repository_fmt_full(item)
        elif verbose == 1:
            item = self.repository_fmt_rel(item)
        else:
            item = os.path.basename(item)
        return item

    def prepare_output_items(self, label, items, overwrite=False,
                             zap_empty=True, create=True):
        cache = self._get_proc_cache(label, set())
        hits = GolemArgs()
        misses = GolemArgs()
        for f, size in items:
            p = os.path.dirname(f)
            if p not in cache:
                if not os.path.isdir(p) and create and '*' not in p:
                    os.makedirs(p)
                cache.add(p)
            if size is None:
                misses += f
                continue
            if overwrite or (zap_empty and not size):
                if os.path.exists(f):
                    os.remove(f)
                    misses += f
            else:
                hits += f
        return hits, misses

    def finalize_output_items(self, label, items, zap_empty=True):
        for f, size in items:
            if size is None:
                continue
            if size == 0 and zap_empty and os.path.exists(f):
                os.remove(f)
                continue

    def purge_output_items(self, items):
        dirs = set()
        for f, size in items:
            if os.path.isdir(f):
                dirs.add(f)
                continue
            if size is not None:
                os.remove(f)
                dirs.add(os.path.dirname(f))
        for d in dirs:
            try:
                os.removedirs(d)
            except OSError:
                continue

    def copy_query_result(self, src_tag, tgt_tag, tags):
        tags['_golem_copy_src'] = tags[src_tag]
        tags['_golem_copy_tgt'] = tags[tgt_tag]
        cmd = "cp %(_golem_copy_src)s %(_golem_copy_tgt)s"
        shell.run_parallel(cmd, vars=tags)


###

# bootstrap initial script

_initialize_golem_view()

### golem proto config

class _cfg(object):
    # Convenience depot for keeping track of configuration details as
    # defined by script authors.

    tags = []
    loops = []
    arg_tags = []
    flow_params = []
    golem_inputs = []
    input_templates = []
    output_templates = []
    input_groups = []
    output_groups = []
    query_templates = []
    sensor_loops = []

    query_handlers = {}
    tags_seen = set()

    main = None
    home = None
    repository = None
    tty_safe = False
    passive_mode = False
    golem_sources = []
    golem_scripts = {}

    @classmethod
    def get_home(cls):
        p = cls.home or os.getenv('GOLEM_HOME') or get_script_dir()
        if not os.path.isabs(p):
            p = os.path.join(get_script_dir(), p)
        return os.path.normpath(p)

    @classmethod
    def get_repository(cls):
        if cls.repository:
            p = cls.repository
            if not os.path.isabs(p):
                p = os.path.join(cls.get_home(), p)
            return os.path.normpath(p)

    @classmethod
    def get_sources(cls):
        sd = get_script_dir()
        hd = cls.get_home()
        if os.getenv('GOLEM_SOURCES'):
            for p in os.getenv('GOLEM_SOURCES').split(':'):
                yield p
        for p in cls.golem_sources:
            if not os.path.isabs(p):
                p = os.path.join(hd, p)
            yield p
        yield sd
        if sd != hd:
            yield hd

    @classmethod
    def register_tag(cls, n):
        if n in cls.tags_seen:
            error = GolemScriptError("duplicate name '%s'" % n)
            raise error
        cls.tags_seen.add(n)

    @classmethod
    def find_script(cls, gscript):
        if hasattr(gscript, '__package__') \
                   and gscript.__package__ == __package__:
            return get_script_path()
        elif isinstance(gscript, model.Golem):
            return gscript.script_path
        if os.path.isabs(gscript):
            spaths = [gscript]
        else:
            spaths = (os.path.join(p, gscript) for p in cls.get_sources())
        for s in spaths:
            s = os.path.normpath(s)
            if os.path.exists(s):
                return s

    @classmethod
    def fetch_golem_script_details(cls, gscript):
        s = cls.find_script(gscript)
        if not s:
            error = GolemScriptError(
                "could not locate golem input %s" % repr(gscript))
            raise error
        if s not in cls.golem_scripts:
            cls.golem_scripts[s] = catalog.fetch_script_details(s)
        return cls.golem_scripts[s]


### golem command line params

class _ctx_param(object):
    # convenience object for tracking parameter states
    __slots__ = ('name', 'alias', 'enabled', 'bound',
                 'help', 'default', 'kwargs')
    def __init__(self, name):
        self.name = name
        self.alias = None
        self.enabled = False
        self.bound = False
        self.help = None
        self.kwargs = {}
    def __str__(self):
        from pprint import pformat
        fmt = "--%s %s\n" % (self.name, (self.help or '').strip())
        fmt += "alias:   %s\n" % self.alias
        fmt += "enabled: %s\n" % self.enabled
        fmt += "bound:   %s\n" % self.bound
        fmt += "kwargs:  %s\n" % pformat(self.kwargs)
        return fmt

class _ctx(object):
    # convenience depot for tracking command-line parameter configuration
    # and runtime values

    reserved = set(['golem-query-mode', 'golem-query-path'])

    valid    = set()
    params   = {}
    aliases  = {}

    ###

    @classmethod
    def register_params(cls, *args):
        for arg in args:
            if arg in cls.reserved or arg.startswith("golem-"):
                error = GolemScriptError(
                    "attempt to register reserved param '%s'" % arg)
                raise error
        cls.valid.update(args)

    @classmethod
    def get_param(cls, name):
        name = cls.aliases.get(name, name)
        if name not in cls.valid and name not in cls.reserved:
            error = GolemScriptError("unknown golem param %s" % repr(name))
            raise error
        return cls.make_param(name)

    @classmethod
    def make_param(cls, name):
        name = cls.aliases.get(name, name)
        p = cls.params.get(name, None)
        if not p:
            p = cls.params[name] = _ctx_param(name)
        return p

    @classmethod
    def bind_golem_param(cls, name, func, help, **kwargs):
        p = cls.get_param(name)
        kwargs.update(p.kwargs)
        p.help = help
        p.kwargs = kwargs
        if p.enabled and not p.bound:
            pn = cls.get_pname(name)
            try:
                func(pn, p.help, **kwargs)
            except TypeError, e:
                raise TypeError("failed to bind param '%s' : %s" % (name, e))
        p.bound = True
        return p

    @classmethod
    def modify_golem_param(cls, name, enabled=Nada, alias=Nada, help=Nada,
                           **kwargs):
        p = cls.get_param(name)
        if p.name in cls.reserved:
            error = GolemScriptError("cannot modify reserved param")
            raise error
        if enabled is not Nada:
            p.enabled = enabled
        if alias is not Nada:
            for k, v in cls.params.items():
                if v.alias == alias or (not v.alias and alias == k):
                    error = GolemScriptError(
                        'golem param alias collision %s' % repr(alias))
                    raise error
            if alias in cls.reserved or alias.startswith("golem-"):
                error = GolemScriptError(
                    'alias is reserved param %s' % alias)
                raise error
            p.alias = alias
            cls.aliases[alias] = name
        if help is not Nada:
            p.help = help
        p.kwargs.update(kwargs)
        return p

    @classmethod
    def _golem_loop_param_default(cls, name, groups, group_name):
        if groups:
            if group_name:
                group_name = '-'.join(group_name.split('_'))
            name = group_name or "%s-group" % name
        return name

    @classmethod
    def get_pname(cls, name):
        p = cls.get_param(name)
        return p.alias or p.name

    @classmethod
    def get_script_param(cls, name):
        p = cls.get_param(name)
        if not p.bound:
            error = GolemScriptError("unbound golem param %s" % repr(name))
            raise error
        v = None
        if p.enabled:
            v = netsa.script.get_param(p.alias or p.name)
        elif 'default' in p.kwargs:
            v = p.kwargs['default']
        return v

    @classmethod
    def get_date_range(cls):
        first_date_p    = cls.get_param('first-date')
        last_date_p     = cls.get_param('last-date')
        intervals_p     = cls.get_param('intervals')
        last_interval_p = cls.get_param('last-interval')
        first_date    = cls.get_script_param('first-date')
        last_date     = cls.get_script_param('last-date')
        intervals     = cls.get_script_param('intervals')
        last_interval = cls.get_script_param('last-interval')
        if first_date_p.enabled ^ last_date_p.enabled:
            first_date = last_date = first_date or last_date
        gv = current_view()
        if not last_date:
            # latest bin
            last_date = gv.last_bin
        if not first_date:
            first_date = last_date
        if last_interval_p.enabled and last_interval:
            last_date = last_date - last_interval * gv.golem.interval
            if first_date > last_date:
                first_date = last_date
        if intervals_p.enabled and intervals:
            first_date = last_date - (intervals - 1) * gv.golem.interval
        return first_date, last_date

    @classmethod
    def skip_missing_inputs(cls):
        return cls.get_script_param('skip-incomplete')

    @classmethod
    def overwrite_outputs(cls):
        return cls.get_script_param('overwrite')

    @classmethod
    def skip_partial_outputs(cls):
        return cls.get_script_param('skip-partial')

    @classmethod
    def data_purge(cls):
        return cls.get_script_param('data-purge')

    @classmethod
    def load_state(cls, gv):
        state = {}
        for pn in cls.valid:
            state[pn] = cls.get_script_param(pn)
        if state['output-select']:
            selects = []
            for o in state['output-select'].split(','):
                if o != '' and o not in selects:
                    selects.append(o)
            state['output-select'] = selects
        else:
            state['output-select'] = []
        for name, (vals, groups, group_name, sep) in gv.golem.loops:
            pname = _ctx._golem_loop_param_default(name, groups, group_name)
            given = state[pname]
            if given:
                selects = []
                for o in state[pname].split(sep):
                    if o != '' and o not in selects:
                        selects.append(o)
                state[pname] = selects
            else:
                state[pname] = []
        state['first-date'], state['last-date'] = _ctx.get_date_range()
        return state


### golem metadata

def set_suite_name(name):
    """
    Set the short suite name for this script, if it belongs to a suite
    of related scripts. This should be a simple label suitable for use
    as a component in paths or filenames. Defaults to ``None``.
    """
    _set_golem(suite_name=name)

def set_name(name):
    """
    Set the short name for this script. The name should be a simple
    label suitable for use as a component in paths or filenames. This
    defaults to the basename of the script file itself, minus the '.py'
    extension, if present.
    """
    _set_golem(name=name)

def set_interval(days=0, minutes=0, hours=0, weeks=0):
    """
    Set how often this golem script is expected to generate results.

    The interval roughly corresponds to how often the script should be
    run (such as from a cron job). Golem scripts will only process data
    for incomplete intervals over a provided date range, unless told
    otherwise via the :option:`--overwrite` option.
    """
    t = _make_timedelta(days=days, minutes=minutes, hours=hours, weeks=weeks)
    _set_golem(interval=t)

def set_span(days=0, minutes=0, hours=0, weeks=0):
    """
    Set the span over which this golem script will expect input data for
    each processing interval. Defaults to the processing interval.

    The span will manifest as how much data is being pulled from a SiLK
    repository or possibly how many outputs from another golem script
    are being consumed. For example, a script having a 4 week span might
    run once a week, pulling 4 weeks worth of data each time it runs.

    See :ref:`golem-interval-span-explained` for more details.
    """
    t = _make_timedelta(days=days, minutes=minutes, hours=hours, weeks=weeks)
    _set_golem(span=t)

def set_skew(days=0, minutes=0, hours=0, weeks=0):
    """
    Shift the epoch from which all time bins and spans are anchored. For
    example, given a golem script with an interval of one week, skew can
    control which day of the week processing occurs.
    """
    t = _make_timedelta(days=days, minutes=minutes, hours=hours, weeks=weeks,
                        allow_negative=True)
    _set_golem(epoch=times.dow_epoch() + t)

def set_lag(days=0, minutes=0, hours=0, weeks=0):
    """
    Set the lag for this golem script relative to the current date and
    time. Defaults to 0.

    As an example, 3 hours is a typical value for data to finish
    accumulating in a given hour within a SiLK repository. Setting lag
    to 3 hours effectively shifts the script's concept of the current
    time that far into the past.
    """
    t = _make_timedelta(days=days, minutes=minutes, hours=hours, weeks=weeks)
    _set_golem(lag=t)

def set_realtime(enable=True):
    """
    Set whether or not this golem script will report output results in
    real time or not. Defaults to ``False``.

    Normally a golem script will wait until a processing interval has
    completely passed before performing any processing or reporting any
    output results. With :func:`set_realtime` enabled, the golem script
    will consider the current processing bin to be the most recent, even
    if it extends to a future date.

    Enabling realtime has a side effect of setting *lag* to zero.
    """
    _set_golem(realtime=bool(enable))

def set_tty_safe(enable=True):
    """
    Set whether or not query results are safe to send to the terminal.
    Defaults to ``False``.
    """
    _cfg.tty_safe = enable

def set_passive_mode(enable=True):
    """
    Controls whether or not an output option is required before running
    the main loop of the script. Defaults to ``False``. Normally at
    least one repository-related or query-related option must be present
    or the script aborts. This is useful for scripts that require query
    behavior by default or are maintaining the repository in a custom
    fashion. If enabled, script authors should explicitely check whether
    or not repository updates were requested via the command line prior
    to updating the repository.
    """
    _cfg.passive_mode = enable

### golem tags, templates, loops

def add_tag(name, value):
    """
    Set a command template tag with key *name*. The provided value can
    be callable, in which case it is resolved once the :func:`main`
    function is invoked. Tags can reference other tags. See
    :ref:`template and tag usage <golem-templates>` for more
    information.
    """
    _cfg.register_tag(name)
    _cfg.tags.append((name, value))

def add_arg(name, value):
    """
    Set a command template argument with key *name*. The value for the
    argument will be a :class:`GolemArgs` object, which shares the same
    behavior as input or output template value (i.e. can have multiple
    values which will render as a space-separated string in the resolved
    template).
    """
    _cfg.register_tag(name)
    _cfg.arg_tags.append((name, value))

def add_output_template(name, template, scope=None,
                        mime_type=None, description=None):
    """
    Define an output template tag key *name* with the provided
    *template*. The provided template can use any of the tags available
    for each processing iteration. Wildcards are acceptable in the
    template specification. Absolute paths are not allowed since outputs
    must reside in the data repository.

    The following optional keyword arguments are available. Pass any of
    them a value of ``None`` to disable entirely:

      *scope*
        Defines how many intervals of this output are required to
        represent a complete analysis result in cases where the output
        from a single interval represents a partial result. For example,
        a golem script might have an interval of 1 day whereas a
        "complete" set of results is 7 days worth relative to any
        particular day.

      *mime_type*
        The expected MIME Content-Type of the output file, if any.

      *description*
        A long-form text description, if any, of the contents of this
        output file.

    See :ref:`template and tag usage <golem-templates>` for more
    information on templates.

    Templates are not required to reference all distinguishing tags and
    can therefore be 'lossy' across loop iterations if such a thing is
    desired.
    """
    _cfg.register_tag(name)
    spec = {}
    if abs(scope or 0) > 1:
        spec['scope'] = abs(scope)
    if mime_type:
        spec['mime_type'] = mime_type
    if description:
        spec['description'] = description
    _cfg.output_templates.append((name, template, spec))

def add_input_template(name, template, required=True,
                             count=None, offset=None, cover=False,
                             source_name=None, mime_type=None,
                             description=None):
    """
    Define an input template tag under key *name*. This is useful for
    defining inputs not produced by other golem scripts. Wildcards
    are allowed in the template specification.

    The provided template can use the any of the set of tags available
    on each processing iteration. The resolved string is available to
    command templates under key *name*.

    Optional keyword arguments:

      *required*
        When ``False`` will ignore missing inputs once the template is
        resolved. Defaults to ``True``.

      *count*
        Specifies how many intervals (as defined by this script)
        over which to resolve the input template. For example, if
        this script has an *interval* of one week, a *count* of 4
        will resolve to the last 4 days of the week in question.

      *offset*
        Specify how far backwards (in intervals) to anchor this input.
        If a *count* has been specified, the offset shifts the entire
        count of intervals.

      *cover*
        If ``True``, a *count* will be calculated such that the template
        will be resolved over all *intervals* covered by the *span* of
        this script. For example, a script with an interval of one day
        and span of seven, the input template will be resolved for all
        seven days in the span.

      *source_name*
        Specify what produced this input For informational purposes when
        listing script inputs.

      *mime_type*
        The expected MIME Content-Type of the input.

      *description*
        A long-form text description of the expected contents of
        this input.

    See :ref:`template and tag usage <golem-templates>` for more
    information on templates.
    """
    _cfg.register_tag(name)
    spec = {}
    if mime_type:
        spec['mime_type'] = mime_type
    if description:
        spec['description'] = description
    if source_name:
        spec['source_name'] = source_name
    if count:
        spec['count'] = count
    if offset:
        spec['offset'] = offset
    if cover:
        spec['cover'] = cover
    spec['required'] = int(required)
    _cfg.input_templates.append((name, template, spec))

def add_input_group(name, inputs):
    """
    Group the given inputs under the provided tag as a single
    :class:`GolemArgs` object. The result can be used the same
    as the regular inputs.
    """
    _cfg.register_tag(name)
    spec = {}
    _cfg.input_groups.append((name, inputs))

def add_output_group(name, inputs):
    """
    Group the given outputs under the provided tag as a single
    :class:`GolemArgs` object. The result can be used the same
    as the regular outputs, including as inputs to other golem
    scripts.
    """
    _cfg.register_tag(name)
    spec = {}
    _cfg.output_groups.append((name, inputs))

def add_query_handler(name, query_handler):
    """
    Define a query handler under tag key *name* to be processed by the
    callable *query_handler*. The output will only be generated
    dynamically when specifically requested via :ref:`query-related
    parameters <golem-query-cli>`.

    The provided callable will be passed the name of this query and
    a 'tags' dictionary for use with templates. And additonal tag
    ``%(golem_query_tgt)s`` will be provided in the standard dictionary
    that contains the output path for this query. The function is
    responsible for creating this output.
    """
    _cfg.register_tag(name)
    if not callable(query_handler):
        error = GolemScriptError(
            "query_only param for '%s' must be callable") % name
        raise error
    _cfg.query_handlers[name] = query_handler
    _cfg.query_templates.append((name, None, {}))

def add_loop(name, values, group_by=None, group_name=None, sep=','):
    """
    Add a template tag under key *name* whose values cycle through
    those provided by *values*, either as an iterable or callable. In
    the latter case, the values are not resolved until the
    :func:`main` function is invoked.

    Optional keyword arguments:

      *group_by*
        Specifies how to group entries from *values* into a single loop
        entry. If the provided value is callable, the function should
        accept a single entry from *values* and return the group label
        for that entry or the original string, e.g. 'LAB2' might return
        'LAB'. If the value is a dictionary, it will resolve to the
        mapped value if present. If it is an iterable of prefix matches,
        they will be converted into a regular expression to be applied
        to the beginning of each entry. In all cases, if there is no
        match or result, the original entry becomes its own group label.

      *group_name*
        This is the name of the template tag under which the group label
        appears, defaulting to the value of *name* appended with
        '_group'. In the above example, if *name* is 'sensor', then
        ``%(sensor)s`` might resolve to 'LAB1,LAB2,LAB3' whereas
        ``%(sensor_group)s`` would merely resolve to 'LAB'.

      *sep*
        Depending on how these loops are visited, the template value
        under *name* might contain multiple values from *values*. Under
        these circumstances, the resulting string is joined by the value
        of 'sep' (default: ',')

    Note that adding a loop will automatically add an additional
    query command line parameter named after the *name* for limiting
    which values to process within the loop. If grouping was requested,
    an additional parameter named after the *group_name* is also added.
    If these parameters are not desired or need to be modified, use the
    :func:`modify_golem_param` function.

    See :ref:`template usage <golem-templates>` for more information on
    templates and loop values.
    """
    _cfg.register_tag(name)
    _cfg.loops.append((name, (values, group_by, group_name, sep)))

def add_sensor_loop(name='sensor', sensors=None,
                    group_by=None, group_name=None, auto_group=False):
    """
    This is a convenience function for adding a template loop tag under
    key *name* whose values are based on sensors defined in a SiLK
    repository. Special note is taken that these loop values represent
    SiLK sensors, so any :class:`netsa.script.Flow_params` tags that are
    defined (see :func:`add_flow_tag`) will have their *sensors*
    parameter automatically bound (if not explicitly bound to something
    else) to the last sensor loop defined by this function.

    Optional keyword arguments:

      *name*
        The tag name within the template. Defaults to 'sensor',
        accessible from within templates as the tag ``%(sensor)s``

      *sensors*
        The source of sensor names, specified either as an iterable or
        callable. Defaults to the :func:`get_sensors` function, which
        will interrogate the local SiLK repository once the :func:`main`
        function is invoked.

      *group_by*
        Same as with :func:`add_loop`

      *group_name*
        Same as with :func:`add_loop`

      *auto_group*
        Causes *group_by* to be set to the :func:`get_sensor_group`
        function, a convenience function that strips numbers, possibly
        preceded by an underscore, from the end of sensor names. This
        can provide serviceable sensor grouping for descriptive sensor
        names (e.g. 'LAB0', 'LAB1', 'LAB2') but will not be of much use
        if they are generically named (e.g. 'S0', 'S1', etc).
    """
    if auto_group:
        group_by = get_sensor_group
    _cfg.sensor_loops.append(name)
    def _get_sensors():
        if sensors:
            s = sensors
        else:
            s = get_sensors
        if callable(s):
            s = s()
        return tuple(s)
    add_loop(name, _get_sensors,
             group_by=group_by, group_name=group_name, sep=',')

def add_golem_input(golem_script, name, output_name=None,
                    count=None, cover=False, offset=None, span=None,
                    join=None, required=True, join_on=None):
    """
    Specify a tag, under key *name*, that represents the path (or paths)
    to an output of an external *golem script*. Only a single output can
    be assosciated at at time -- if the external script has multiple
    outputs defined, then additional calls to this function are
    necessary for each output of interest.

    For each output template, efforts are made to synchronize across
    time intervals and loop tags as appropriate. By default, this is the
    output of the most recent interval of the other golem script that
    corresponds to the interval currently under consideration within the
    local script. Covering multiple intervals of the input is controlled by
    *cover*, *count*, or *span*. If, for example, you're pulling inputs
    with an hourly interval into a script with a daily interval, the
    *cover* parameter should probably be used, otherwise only a single
    hour would be pulled in.

    Matching loop tags are automatically joined unless the *join*
    parameter is provided, in which case the only joins that happen
    are the ones provided.

    Optional keyword arguments:

      *output_name*
        The tag name used for this output in the external script if it
        differs from the value of *name* used locally for this input. By
        default the names are assumed to be identical.

      *count*
        Specifies how many intervals (as defined by the external script)
        of output data are to be used as input. By default, the most
        recent interval of the other golem script that corresponds to
        the local interval currently under consideration is provided.

        For example, if the other golem script has an *interval* of one
        week, a *count* of 4 will provide the last 4 weeks of output
        from that script.

      *offset*
        Specify how far back (in units of the other script's interval)
        to reference for this input. Defaults to the most recent
        corresponding interval. If a *count* has been specified, the
        offset shifts the entire count of intervals.

        For example, if the other script's interval is one week, an
        offset of -1 will reference the output from the week prior to
        the most recent week. Negative and positive offsets are
        equivalent for these purposes, they always reach backwards
        through time.

      *cover*
        If ``True``, a *count* is calculated that will fully cover the
        local interval under consideration. This option cannot be used
        with the *count* or *offset* options. Defaults to ``False``.

        For example, if the local interval is one week, and the other
        interval is one day, then this is equivalent to specifying a
        *count* of 7 (days).

      *span*
        A :class:`datetime <datetime.timedelta>` object that represents
        a span of time that covers the intervals of interest. Based on
        the other script's interval, a *count* is calculated that will
        cover the provided span. Cannot be used simultaneously with
        *count*, *offset*, or *cover*.

      *join*
        A dictionary or iterable of tuples that provides an equivalence
        mapping between template loops defined in the other golem script
        and locally defined loops. If no join mapping is provided, an
        attempt is made to join on loops sharing the same name. If the
        join parameter is provided, no auto-join is performed.

        For example, if the other script defines a template loop on the
        ``%(my_sensor)s`` tag, and the local script defines a loop on
        ``%(sensor)s``, a mapping from 'my_sensor' to 'sensor' will
        ensure that for each iteration over the values of ``%(sensor)s``
        the input tag value is also sensor-specific based on its
        ``%(my_sensor)s`` loop. Without this association, the input tag
        would resolve to all outputs across all sensors, regardless of
        which sensor or sensor group was currently under local
        consideration. Iterations with no valid mapping are ignored, as
        opposed to when a valid association exists but the other output
        is missing.

      *required*
        If ``False`` or ``0`` and the expected output from the other
        golem script is missing, continue processing rather than raising
        an exception. If specified as a positive integer, it means *at
        least* that many of the other inputs should exist, otherwise an
        exception is thrown. By default, at least one input is required.
        It is up to the developer to handle missing inputs (i.e. empty
        template tags) appropriately in these cases.
    """
    if not output_name:
        output_name = name
    # note: None signals auto-join, {} means no joins
    if join:
        join = dict(join)
    # note: join_on is deprecated
    _cfg.golem_inputs.append((golem_script, name, output_name, join, \
                              count, cover, offset, span, required))

def add_self_input(name, output_name, count=None, offset=None, span=None):
    """
    Specify an input template tag, under key *name*, associated with
    this script's own output from prior intervals. Since output tag
    names will necessarily collide, *name* is the new tag name for the
    input and *output_name* is the name of the output template.

    Optional keyword arguments:

      *count*
        Same as with :func:`add_golem_input`

      *offset*
        Same as with :func:`add_golem_input`, except defaults to -1. If
        self-referencing for purposes of delta-encoding, 0 should
        probably be specified.

      *span*
        Same as with :func:`add_golem_input`

    Assuming a local loop over the template tag ``%(sensor)s``, the
    following example:

      >>> script.add_self_input('result', 'prior_result')

    ...is equivalent to this:

      >>> script.add_golem_input(script.get_script_path(), 'prior_result',
      >>>     output_name='result',
      >>>     offset=-1,
      >>>     join_on=['sensor'],
      >>>     required=False)

    .. note::

        If this output happens to have a *scope* the developer should
        ensure that this self-reference means what is intended for 'most
        recent' output.

        For example, if this golem script has an *interval* of 1
        day, but the output has a *scope* of 28 (days), the example
        above would capture the prior 28 days of output due to the
        offset of -1.

        If the script is delta-encoding its current result with its own
        prior results, however, probably what is desired would be the
        prior 27 days, in which case offset should be specified as 0.
        The 28th day in this scope scenario is the very result currently
        being generated, which does not exist yet, and therefore will
        not appear in the template as a 'prior' result. After processing
        is complete, however, it *will* appear in the collected outputs
        if a different golem script references this interval as input.
    """
    add_golem_input(get_script_path(), name, output_name=output_name,
                    count=count, cover=False, offset=offset, span=span,
                    join_on=None, join=None, required=False)

def add_flow_tag(name, flow_class=None, flow_type=None, flowtypes=None,
                       sensors=None, start_date=None, end_date=None,
                       input_pipe=None, xargs=None, filenames=None):
    """
    Add a :class:`netsa.script.Flow_params` object as a template tag
    under key *name*. The rest of the keyword arguments correspond to
    the same parameters accepted by the
    :class:`netsa.script.Flow_params` constructor and serve to map
    these fields to *either* specific template tags in the golem script
    or to the literal string if it is not present in the template
    tags.. If not otherwise specified, the *start_date* and *end_date*
    attributes are bound to the values of ``%(golem_start_date)s`` and
    ``%(golem_end_date)s``, respectively, for each loop iteration.
    Additionally, if any sensor-specific loops were specified via
    :func:`add_sensor_loop`, the *sensors* parameter defaults to the
    tag associated with the last defined sensor loop (typically
    ``%(sensor)s``). The resulting :class:`netsa.script.Flow_params`
    object is associated with a tag entry specified by *name*. The
    values of tags associated with :class:`netsa.script.Flow_params`
    attributes in this way are still accessible under their original
    tag names.

    The following optional keyword arguments are available to map
    template tag values to their corresponding attributes in the flow
    params object: *flow_class*, *flow_type*, *flowtypes*, *sensors*,
    *start_date*, *end_date*, *input_pipe*, *xargs*, and *filenames*.

    See :ref:`template and tag usage <golem-templates>` for more
    information on templates.
    """
    _cfg.register_tag(name)
    params = {}
    if flow_class:
        params['flow_class'] = flow_class
    if flow_type:
        params['flow_type'] = flow_type
    if flowtypes:
        params['flowtypes'] = flowtypes
    if sensors:
        params['sensors'] = sensors
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    if input_pipe:
        params['input_pipe'] = input_pipe
    if xargs:
        params['xargs'] = xargs
    if filenames:
        params['filenames'] = filenames
    _cfg.flow_params.append((name, params))

###

def modify_golem_param(name, enabled=Nada, alias=Nada, help=Nada, **kwargs):
    """
    Modifies the settings for the given golem script parameter. Accepts
    new values for the golem-specific keywords *enabled* and *alias*,
    along with the usual :mod:`netsa.script` parameter keywords (e.g.
    *help*, *required*, *default*, *default_help*, *description*,
    *mime_type*)
    """
    _ctx.make_param(name)
    _ctx.modify_golem_param(name, enabled=enabled, alias=alias, **kwargs)

def add_golem_source(repo_path):
    """
    Adds a directory within which to search for other golem scripts.
    Directories are searched in the following order: 1) paths within the
    colon-separated list of directories in the :envvar:`GOLEM_SOURCES`
    environment variable; 2) any paths added by this function (multiple
    invocations allowed); 3) this script's own directory as reported by
    the :func:`get_script_dir` function, and finally 4) this script's
    home directory as reported by the :func:`get_home` function, if
    different than the script directory. These directories are only
    searched if the external script is specified as a relative path.
    """
    if repo_path not in _cfg.golem_sources:
        _cfg.golem_sources.append(repo_path)

###

def add_golem_params(without_params=None):
    """
    Enables all golem command line parameters. Equivalent to
    individually invoking each of :func:`add_golem_basic_params`,
    :func:`add_golem_repository_params`, and
    :func:`add_golem_query_params`. Optionally accepts a list of
    parameters to exclude.
    """
    add_golem_basic_params(without_params)
    add_golem_query_params(without_params)
    add_golem_repository_params(without_params)

def add_golem_param(name, alias=Nada, help=Nada, **kwargs):
    """
    Enables a particular golem command line parameter. Accepts the
    same optional keyword parameters as the
    :func:`modify_golem_param` function with the exception of
    ``enable``, which is implied. An example is the ``alias``
    parameter, which which can be provided to change the default
    parameter string (for example, aliasing ``--last-date`` to
    ``--date`` in cases where date ranges are not desired).
    """
    _ctx.get_param(name)
    _ctx.modify_golem_param(name, enabled=True,
                            alias=alias, help=help, **kwargs)

_golem_basic_params = ['last-date', 'first-date', 'last-interval',
                       'intervals', 'skip-incomplete', 'skip-partial',
                       'overwrite']
_golem_basic_params_disabled = set()
_ctx.register_params(*_golem_basic_params)

def add_golem_basic_params(without_params=None):
    """
    Enables :ref:`basic <golem-basic-cli>` golem command line
    parameters. Optionally accepts a list of parameters to exclude.
    """
    without_params = without_params or ()
    for name in _golem_basic_params:
        _ctx.modify_golem_param(name, enabled=True)
        if name in without_params:
            _ctx.modify_golem_param(name, enabled=False)
    _golem_basic_params_disabled.update(without_params)

def _bind_golem_basic_params():

    _ctx.bind_golem_param(
        'last-date', netsa.script.add_date_param,
        "Date within the last time bin of interest.",
        required=False, default_help="most recent")

    _ctx.bind_golem_param(
        'first-date', netsa.script.add_date_param,
        "Date within the first time bin of interest.",
        required=False, default_help="value of last-date")

    interval_str = timedelta_iso(current_view().golem.interval)

    _ctx.bind_golem_param(
        'last-interval', netsa.script.add_int_param,
        """
        Set the last processing date N intervals (%s) prior to the
        provided last date, which defaults to the most recent date. This
        can be useful when purging old results when used in conjunction
        with --intervals.
        """ % interval_str, required=False)

    _ctx.bind_golem_param(
        'intervals', netsa.script.add_int_param,
        """
        Optionally process or query the last N intervals (%s) of data
        from the last date, which defaults to the most recent date. This
        will override the first interval date if it was provided. This
        can be useful when purging old results when used in conjunction
        with --last-interval.
        """ % interval_str, required=False)

    _ctx.bind_golem_param(
        'skip-incomplete', netsa.script.add_flag_param,
        """
        Skip processing bins that have incomplete input requirements,
        as opposed to aborting.
        """)

    _ctx.bind_golem_param(
        'skip-partial', netsa.script.add_flag_param,
        """
        Skip processing bins that have partial output results,
        as opposed to aborting.
        """)

    _ctx.bind_golem_param(
        'overwrite', netsa.script.add_flag_param,
        "Overwrite output results if they already exist.")

_golem_query_params = ['output-select', 'output-path']
_ctx.register_params(*_golem_query_params)

def add_golem_query_params(without_params=None):
    """
    Enables :ref:`query-related <golem-query-cli>` golem command line
    parameters. Optionally accepts a list of parameters to exclude.
    """
    without_params = without_params or ()
    for name in _golem_query_params:
        _ctx.modify_golem_param(name, enabled=True)
        if name in without_params:
            _ctx.modify_golem_param(name, enabled=False)

def _bind_golem_query_params():

    help_text = """
        Optionally limit output results to the comma-separated
        names provided.
    """
    if len(_cfg.output_templates) + len(_cfg.query_templates) <= 1:
        _ctx.modify_golem_param('output-select', enabled=False)
    else:
        avail  = [x[0] for x in _cfg.output_templates]
        avail += [x[0] for x in _cfg.query_templates]
        avail = ','.join(avail)
        help_text += "Available choices: %s" % avail
    _ctx.bind_golem_param(
        'output-select', netsa.script.add_text_param,
        help_text, required=False)

    _ctx.bind_golem_param(
        'output-path', netsa.script.add_output_file_param,
        """
        Optionally specify an output file in which to generate a
        single query result for the given parameters. Also accepts
        '-', and 'stdout'.
        """, required=False)

_golem_repository_params = ['data-process', 'data-purge', 'data-status',
                            'data-queue', 'data-complete', 'data-inputs',
                            'data-outputs', 'data-load']
_ctx.register_params(*_golem_repository_params)

def add_golem_repository_params(without_params=None):
    """
    Adds :ref:`repository-related <golem-repository-cli>` golem command
    line parameters. Optionally accepts a list of parameters to exclude.
    """
    without_params = without_params or ()
    for name in _golem_repository_params:
        _ctx.modify_golem_param(name, enabled=True)
        if name in without_params:
            _ctx.modify_golem_param(name, enabled=False)

def _bind_golem_repository_params():
    # default golem-related data-generation command line parameters

    _ctx.bind_golem_param(
        'data-process', netsa.script.add_flag_param,
        """
        Generate incomplete or missing repository results,
        skipping those that are complete.
        """)

    _ctx.bind_golem_param(
        'data-load', netsa.script.add_flag_param,
        """
        Alias for --data-process.
        """, expert=True)

    _ctx.bind_golem_param(
        'data-purge', netsa.script.add_flag_param,
        """
        Purge any repository results present for the given processing
        intervals. This negates --data-process if present.
        """)

    _ctx.bind_golem_param(
        'data-status', netsa.script.add_flag_param,
        """
        Show the status of repository date-bin results given the
        options provided. No processing is performed.
        """)

    _ctx.bind_golem_param(
        'data-queue', netsa.script.add_flag_param,
        """
        List the dates of all pending repository results given
        the options provided. No processing is performed.
        """)

    _ctx.bind_golem_param(
        'data-complete', netsa.script.add_flag_param,
        """
        List the dates of all repository results currently
        completed, given the options provided. No processing is
        performed.
        """)

    if not _cfg.input_templates and not _cfg.golem_inputs:
        _ctx.modify_golem_param('data-inputs', enabled=False)
    _ctx.bind_golem_param(
        'data-inputs', netsa.script.add_flag_param,
        """
        Show the status of input dependencies from other golem scripts
        or defined templates, given the options provided. No processing
        is performed.
        """)

    _ctx.bind_golem_param(
        'data-outputs', netsa.script.add_flag_param,
        """
        Show the status of repository output results given the
        options provided. No processing is performed.
        """)

    if not _cfg.get_repository():
        for name in _golem_repository_params:
            p = _ctx.get_param(name)
            if p.enabled:
                error = GolemScriptError("Repository params enabled with"
                                            " no repository defined")
                raise error

### various golem views

def inputs(gview=None):
    """
    Returns a :class:`GolemInputs` view of the given golem view, which
    defaults to the main script view. No system level processing happens
    while iterating over or interacting with this view.
    """
    if not gview:
        try:
            gview = script_view()
        except GolemInitError:
            error = GolemScriptError(
                "inputs() invoked outside of main()")
            raise error
    return gview.inputs()

def outputs(gview=None):
    """
    Returns a :class:`GolemOutputs` view of the given golem view, which
    defaults to the main script view.. No system level processing
    happens while iterating over or interacting with this view.
    """
    if not gview:
        try:
            gview = script_view()
        except GolemInitError:
            error = GolemScriptError(
                "outputs() invoked outside of main()")
            raise error
    return gview.outputs()

def loop(gview=None):
    """
    Returns a :class:`GolemTags` view of the given golem view, which
    defaults to the main script view. No system level processing happens
    while iterating over or interacting with this view.
    """
    if not gview:
        try:
            gview = script_view()
        except GolemInitError:
            error = GolemScriptError(
                "loop() invoked outside of main()")
            raise error
    return gview.loop()

def _status_pfx(gview, tags=None):
    if not tags:
        tags = gview.tags()
    loops = []
    for l in (x[0] for x in gview.golem.loops):
        loops.append("%%(%s)s" % l)
    pfx = "%(golem_bin_basic)s"
    if loops:
        pfx = ' '.join([pfx, "(%s)" % ','.join(loops)])
    return pfx % tags

def process(gview=None, exception_handler=None):
    """
    Returns a :class:`GolemProcess` wrapper around the given golem view,
    which defaults to the main script view. The result behaves much like
    a :class:`GolemTags` object. Iterating over it returns a dictionary
    of resolved template tags while performing system level interactions
    (such as checking for input existence and creating output
    directories and/or files) in preparation for whatever processing the
    developer specifies in the processing loop. Views that have already
    completed processing are ignored.

    Also takes an optional 'exception_handler' keyword argument
    which must be a function that accepts an exception and a
    golem view object (advanced use only).
    """
    if not gview:
        try:
            gview = script_view()
        except GolemInitError:
            error = GolemScriptError(
                "process() invoked outside of main()")
            raise error
    overwrite_outputs    = _ctx.overwrite_outputs()
    skip_missing_inputs  = _ctx.skip_missing_inputs()
    skip_partial_outputs = _ctx.skip_partial_outputs()
    data_purge           = _ctx.data_purge()

    verbose = netsa.script.get_verbosity()

    def handler(e, gv):
        try:
            raise e
        except GolemInputMissing:
            if skip_missing_inputs:
                if verbose > 1:
                    msg = _status_pfx(gv) + ": inputs missing (skipping)"
                    print >> sys.stderr, msg
                raise GolemIgnore
            else:
                pn = _ctx.get_pname('skip-incomplete')
                msg = _status_pfx(gv) + \
                      ": %s (use --%s to skip bins missing inputs)" % (e, pn)
                raise GolemUserError, msg
        except GolemPartialComplete:
            if skip_partial_outputs:
                if verbose > 1:
                    msg = _status_pfx(gv) + \
                          ": partially complete (skipping)"
                    print >> sys.stderr, msg
                raise GolemIgnore
            else:
                pn1 = _ctx.get_pname('overwrite')
                pn2 = _ctx.get_pname('skip-partial')
                msg = _status_pfx(gv) + \
                      ": partial result present: use --%s to overwrite " \
                      "or --%s to skip" % (pn1, pn2)
                raise GolemUserError, msg
        except GolemComplete:
            if verbose > 1:
                msg = _status_pfx(gv) + ": already complete (skipping)"
                print >> sys.stderr, msg
            raise GolemIgnore
        except GolemIgnore:
            pass

    return GolemProcess(gview,
        exception_handler = exception_handler or handler,
        overwrite_outputs = overwrite_outputs,
    )

def generate_query_result(tgt_file, gproc=None):
    if not gproc:
        gproc = process()
    if not isinstance(gproc, GolemProcess):
        gproc = process(gproc)

    golem = gproc.gview.golem
    if golem.query_templates:
        if len(golem.query_templates) > 1:
            raise RuntimeError("too many query templates")
        gproc = gproc.using(gproc.gview._as_self_query())
        golem = gproc.gview.golem

    outs = gproc.outputs()
    if len(outs) > 1:
        error = GolemScriptError("too many outputs for single query")
        raise error
    if os.path.exists(tgt_file):
        if gproc.overwrite_outputs:
            os.remove(tgt_file)
        else:
            error = GolemComplete("output exists %s" % repr(tgt_file))
            raise error
    tags  = gproc.tags()
    tags['golem_query_tgt'] = tgt_file
    if golem.output_templates:
        label = golem.output_templates[0][0]
        cmd = "cp %%(%s)s %%(golem_query_tgt)s" % label
        shell.run_parallel(cmd, vars=tags)
    elif golem.query_templates:
        tag  = golem.query_templates[0][0]
        func = _cfg.query_handlers[tag]
        func(tags)
    else:
        error = GolemScriptError("no output or query templates")
        raise error

def _resolve_loops_and_params():
    # normalize loops, add loop selection command line params
    golem_loops = []
    for name, (vals, group_by, group_name, sep) in _cfg.loops:
        if callable(vals):
            vals = tuple(vals())
        if isinstance(vals, basestring):
            vals = (vals,)
        groups = None
        if group_by:
            if not callable(group_by):
                try:
                    gb = dict(group_by)
                    group_by = lambda x: gb.get(x)
                except TypeError:
                    if isinstance(groups, basestring):
                        groups = (groups,)
                    pat = '(' + '|'.join(sorted(set(groups))) + ')'
                    def _sgroup(name):
                        match = re.search(pat, name)
                        if match:
                            return match.group(0)
                        else:
                            return name
                    group_by = _sgroup
            new_vals = ()
            groups = {}
            for v in vals:
                g = group_by(v) or v
                if g not in groups:
                    groups[g] = ()
                    new_vals += (g,)
                groups[g] += (v,)
            vals = new_vals
        golem_loops.append((name, (vals, groups, group_name, sep)))
        pname = _ctx._golem_loop_param_default(name, groups, group_name)
        avail = ','.join((str(x) for x in sorted(groups or vals)))
        pdesc = """
            Optional list of %s values (separated by %s) on which to
            limit processing or querying (if any). Available values: %s
        """ % (pname, repr(sep), avail)
        _golem_basic_params.append(pname)
        p = _ctx.register_params(pname)
        if pname not in _golem_basic_params_disabled:
            if any(_ctx.get_param(x).enabled for x in _golem_basic_params):
                _ctx.modify_golem_param(pname, enabled=True)
        _ctx.bind_golem_param(pname, netsa.script.add_text_param,
            pdesc, required=False)
    return golem_loops

def execute(func):
    """
    Executes the ``main`` function of a golem script. This should be
    called as the last line of any golem script, with the script's
    ``main`` function (whatever it might be named) as its only argument.

    .. warning::

        It is important that most, if not all, actual work the script
        does is done within this function. Golem scripts (as with all
        :ref:`NetSA Scripting Framework <netsa-script>` scripts) may
        be loaded in such a way that they are not executed, but merely
        queried for metadata instead. If the golem script performs
        significant work outside of the :func:`main` function,
        metadata queries will no longer be efficient. Golem scripts
        must use this :func:`execute` function rather than
        :func:`netsa.script.execute`.
    """

    # bind basic params
    _bind_golem_basic_params()

    # resolve plain tags
    golem_tags = []
    for name, val in _cfg.tags:
        if callable(val):
            val = val()
        golem_tags.append((name, val))
    _cfg.tags = golem_tags

    # resolve arg tags
    golem_arg_tags = []
    for name, val in _cfg.arg_tags:
        if callable(val):
            val = val()
        golem_arg_tags.append((name, val))
    _cfg.arg_tags = tuple(golem_arg_tags)

    # default bind to sensor loops
    golem_flow_params = []
    for name, params in _cfg.flow_params:
        if _cfg.sensor_loops and 'sensors' not in params:
            params['sensors'] = _cfg.sensor_loops[-1]
        golem_flow_params.append((name, params))

    # commit output templates
    golem_output_templates = []
    for name, template, spec in _cfg.output_templates:
        golem_output_templates.append((name, template, dict(spec)))

    # commit query-only templates
    golem_query_templates = []
    for name, template, spec in _cfg.query_templates:
        golem_query_templates.append((name, template, dict(spec)))

    # normalize loops, add loop selection command line params,
    # update _cfg with resolved callables
    golem_loops = _resolve_loops_and_params()
    _cfg.loops = tuple(golem_loops)

    # bind remaining golem params
    _bind_golem_query_params()
    _bind_golem_repository_params()

    # inform golem
    gview = _set_golem(
        repository       = _cfg.get_repository(),
        tags             = golem_tags,
        loops            = golem_loops,
        arg_tags         = golem_arg_tags,
        flow_maps        = golem_flow_params,
        output_templates = golem_output_templates,
        query_templates  = golem_query_templates,
        input_groups     = list(_cfg.input_groups),
        output_groups    = list(_cfg.output_groups)
    )

    # process command line parameters, possibly dump metadata
    netsa.script.execute(lambda: True)
    ctx = _ctx.load_state(gview)

    # adjust output and query-only templates if output-select was
    # specified
    selects = set(ctx['output-select'])
    outs = gview.golem.output_templates
    outs = []
    queries = []
    if selects:
        for x in gview.golem.output_templates:
            if x[0] in selects:
                outs.append(x)
                selects.remove(x[0])
        for x in gview.golem.query_templates:
            if x[0] in selects:
                queries.append(x)
                selects.remove(x[0])
        if selects:
            pname = _ctx.get_pname('output-select')
            outs = ','.join(selects)
            error = ParamError(pname, outs, "invalid output select")
            _print_failure(sys.stderr, error)
    if not outs:
        outs = gview.golem.output_templates
    gview = _set_golem(output_templates=outs, query_templates=queries)

    # commit input templates
    golem_input_templates = []
    for name, t, spec in _cfg.input_templates:
        golem_input_templates.append((name, t, dict(spec)))

    # adjust loop values if any loop-select params were specified,
    # then commit loops
    for i, (name, (vals, groups, group_name, sep)) in enumerate(golem_loops):
        pname = _ctx._golem_loop_param_default(name, groups, group_name)
        given = list(ctx[pname])
        if not given:
            continue
        if groups:
            gmap = {}
            for g, names in groups.iteritems():
                gmap.update((x, g) for x in names)
            for j, g in enumerate(given):
                if g in gmap:
                    given[j] = gmap[g]
        for g in given:
            if g not in vals:
                pn = _ctx.get_pname(pname)
                error = ParamError(pn, g, "unknown loop select")
                _print_failure(sys.stderr, error)
        golem_loops[i] = (name, (tuple(given), groups, group_name, sep))

    # now add golem inputs
    golem_inputs = []
    for (gscript, name, output_name, join,
            count, cover, offset, span, required) in _cfg.golem_inputs:
        gpath = _cfg.find_script(gscript)
        ap1 = None
        if gpath:
            ap1 = os.path.normpath(gpath)
        ap2 = os.path.normpath(get_script_path())
        if ap1 == ap2:
            # self-input
            gin = gview.golem.using()
            if offset is None:
                offset = -1
        elif isinstance(gscript, model.Golem):
            gin = gscript
        else:
            gin = _cfg.fetch_golem_script_details(gscript)
        if not gin.output_templates:
            error = GolemScriptError(
                "input script has no outputs %s" % repr(gscript))
            raise error
        # auto-join on matching loop names
        if join is None:
            join = {}
            for loop in set(x[0] for x in gview.golem.loops).intersection(
                            x[0] for x in gin.loops):
                join[loop] = loop
        if span:
            if cover or count:
                error = GolemScriptError(
                    "span cannot be used with cover or count")
                raise error
            count, r = times.divmod_timedelta(span, gin.interval)
            if count <= 1:
                error = GolemScriptError(
                    "input span must cover more than one interval")
                raise error
        spec = {}
        spec['output_name'] = output_name
        if join:
            spec['join'] = join
        if cover:
            spec['cover'] = cover
        if count:
            spec['count'] = count
        if offset or offset is not None:
            spec['offset'] = offset
        spec['required'] = int(required)
        gin = gin._map_outputs({output_name: name}, filter=True)
        golem_inputs.append((gin, spec))

    # check loop alignment
    loops_defined = set(x[0] for x in golem_loops)
    for gin, spec in golem_inputs:
        join = spec.get('join', None)
        k, template, _ = gin.output_templates[0]
        tags = _analyze_templates(template)
        if join:
            loops_left = loops_defined.difference(join.values())
        else:
            loops_left = loops_defined
        cross = loops_left.intersection(tags)
        if cross:
            error = GolemScriptError(
                "unbound loops in golem input template %s : %s" \
                    % (repr(gin.name), repr(sorted(cross))))
            raise error

    # finalize inputs and loops
    gview = _set_golem(
        loops            = golem_loops,
        golem_inputs     = golem_inputs,
        input_templates  = golem_input_templates)

    # finalize date window and repository
    first_date, last_date = ctx['first-date'], ctx['last-date']
    gview = _set_golem_view(first_date=first_date, last_date=last_date)

    has_out = {}
    for o in ('data-process', 'data-load', 'output-path'):
        p = ctx[o]
        p = _ctx.get_param(o)
        if _ctx.get_param(o).enabled:
            has_out[o] = ctx[o]

    if _ctx.get_param('data-process').enabled or \
           _ctx.get_param('data-load').enabled:
        data_load = ctx['data-process'] or ctx['data-load']
    elif _cfg.passive_mode and not has_out:
        data_load = True
    else:
        tmp_dir = tempfile.mkdtemp()
        atexit.register(os.system, ("rm -rf %s" % tmp_dir))
        gview = _set_golem(repository=tmp_dir)
        data_load = True

    verbose = netsa.script.get_verbosity()

    if ctx['data-status']:
        _print_status(sys.stdout, gview)
        sys.exit(0)

    if ctx['data-queue']:
        _print_queue(sys.stdout, gview)
        sys.exit(0)

    if ctx['data-complete']:
        _print_complete(sys.stdout, gview)
        sys.exit(0)

    if ctx['data-inputs']:
        _print_io(sys.stdout, gview.inputs(), verbose=verbose)
        sys.exit(0)

    if ctx['data-outputs']:
        _print_io(sys.stdout, gview.outputs(), verbose=verbose)
        sys.exit(0)

    if ctx['data-purge']:
        verbose = netsa.script.get_verbosity()
        for gv in gview:
            if verbose > 1:
                print >> sys.stderr, _status_pfx(gv) + ": purging"
            GolemResource(gv.outputs()).purge_output()
        sys.exit(0)

    # process

    try:

        out_path = ctx['output-path']
        out_fh = None
        if out_path:
            pname = 'output-select'
            error = None
            otc = len(gview.golem.output_templates)
            qtc = len(gview.golem.query_templates)
            if (otc > 1 and not qtc) or (qtc and qtc > 1):
                error = GolemUserError(
                    "no output selected with --%s" % _ctx.get_pname(name))
                raise error
            bc = gview.bin_count()
            lc = len(golem_loops)
            if lc == 1:
                lc = len(golem_loops[0][1][0])
            if bc > 1 or lc > 1:
                p = _ctx.get_pname('output-path')
                if bc > 1:
                    msg = "Select single date"
                elif lc > 1:
                    msg = "Select single loop value"
                else:
                    msg = "Select single date and single loop value"
                msg += " when using --%s" % p
                error = GolemUserError(msg)
                raise error
            if out_path == '_' or out_path == 'stdout':
                out_path = 'stdout'
                out_fh = sys.stdout
                if out_fh.isatty() and not _cfg.tty_safe:
                    error = GolemUserError(
                        "%s selected on tty" % out_path)
                    raise error
                out_path = get_temp_file_name()

        rsrc = GolemFileResource(gview)
        if gview.golem.repository and not rsrc.repository_exists():
            error = GolemScriptError(
                "missing repository %s (create it, set $GOLEM_HOME"
                    " environment variable or use"
                    " set_default_home())" % repr(gview.golem.repository))
            raise error
        if has_out and not _cfg.passive_mode:
            if not any((ctx[x] for x in has_out)):
                error = GolemUserError("no output actions specified")
                raise error

        # load repository
        if data_load or (_cfg.passive_mode and not out_path):
            func()

        # load query
        if out_path:
            generate_query_result(out_path)
            if out_fh:
                import subprocess
                subprocess.call(['cat', out_path])

    except UserError:
        netsa.script._print_failure(sys.stderr, str(sys.exc_info()[1]))
    except ParamError:
        netsa.script._print_failure(sys.stderr, str(sys.exc_info()[1]))

###

def _dump_params(bind=False):
    # debug for params
    if bind:
        _bind_golem_basic_params()
        _bind_golem_query_params()
        _bind_golem_repository_params()
    _resolve_loops_and_params()
    print "BASIC PARAMS\n"
    for name in _golem_basic_params:
        print _ctx.get_param(name)
    print "\nQUERY PARAMS\n"
    for name in _golem_query_params:
        print _ctx.get_param(name)
    print "\nREPOSITORY PARAMS\n"
    for name in _golem_repository_params:
        print _ctx.get_param(name)
    sys.exit()

def _dump_env():
    print "name:", script_view().golem.name
    print "loc: ", get_script_dir()
    print "home:", get_home()
    print "repo:", get_repository()
    for (gscript, name, output_name, _, _, _, _, _) in _cfg.golem_inputs:
        if hasattr(gscript, '__package__') \
                   and gscript.__package__ == __package__:
            gscript = get_script_path()
        gscript = _cfg.find_script(gscript)
        print "input %s (%s):\n    %s" % (name, output_name, gscript)
    sys.exit()

###

class GolemProcess(object):
    """
    A utility class for performing system-level interactions (such as
    checking for required inputs, pre-existing outputs, creating
    output paths, etc) while iterating over the provided view.

      *exception_handler*
        Function for processing GolemException events. Takes
        the exception and the current GolemView as arguments.

      *overwrite_outputs*
        Delete existing outputs prior to processing. (default:
        ``False``)

      *keep_empty_outputs*
        Consider zero-byte output results to be valid, otherwise
        they will be ignored or deleted when encountered, regardless of
        the value of *overwrite_results*. (default: ``False``)
    """

    __slots__ = ('gview', 'exception_handler', 'overwrite_outputs',
                 'keep_empty_outputs')

    def __init__(self, gview, exception_handler=None,
                 overwrite_outputs=False, keep_empty_outputs=False):
        self.gview               = gview.loop()
        self.exception_handler   = exception_handler
        self.overwrite_outputs   = overwrite_outputs
        self.keep_empty_outputs  = keep_empty_outputs

    def using(self, gview=Nada, exception_handler=Nada,
              overwrite_outputs=Nada, keep_empty_outputs=Nada):
        """
        Return a copy of this :class:`GolemProcess` object, possibly
        replacing certain attributes corresponding to the keyword
        arguments in the constructor.
        """
        if gview is Nada:
            gview = self.gview
        if exception_handler is Nada:
            exception_handler = self.exception_handler
        if overwrite_outputs is Nada:
            overwrite_outputs = self.overwrite_outputs
        if keep_empty_outputs is Nada:
            keep_empty_outputs = self.keep_empty_outputs
        return self.__class__(gview,
                exception_handler=exception_handler,
                overwrite_outputs=overwrite_outputs,
                keep_empty_outputs=keep_empty_outputs)

    def _check_inputs(self):
        required = {}
        for k, _, spec in self.golem.input_templates:
            required[k] = int(spec.get('required', 0) or 0)
        for gin, spec in self.golem.golem_inputs:
            for k in [x[0] for x in gin.output_templates]:
                required[k] = int(spec.get('required', 0) or 0)
        input_groups = set(x[0] for x in self.golem.input_groups)
        rsrc = GolemFileResource(self.inputs())
        hits = GolemArgs()
        misses = GolemArgs()
        for r, label, args, miss, tags in rsrc.audit_all_by_label():
            if label in input_groups:
                continue
            if not args and not miss:
                if required[label]:
                    error = GolemInputMissing(
                        "required input missing '%s'" % label)
                    raise error
            if miss:
                v = abs(required[label])
                if required[label] == 1:
                    f = sorted(miss)[0]
                    error = GolemInputMissing(
                        "required input missing '%s': %s" % (label, f))
                    raise error
                elif required[label] > 1:
                    v = required[label]
                    if len(args) < v:
                        error = GolemInputMissing(
                            "at least %d items required for input '%s'" \
                                    % (v, label))
                        raise error
            hits +=args
            misses += miss
        return hits, misses

    def _initialize(self):
        self._check_inputs()
        hits, misses = GolemResource(self.outputs()).prepare_output(
            overwrite = self.overwrite_outputs,
            zap_empty = not self.keep_empty_outputs)
        if not hits and not misses:
            pass
        elif not misses:
            raise GolemComplete
        elif hits:
            raise GolemPartialComplete

    def _finalize(self):
        zap_empty = not self.keep_empty_outputs
        GolemResource(self.outputs()).finalize_output(zap_empty=zap_empty)

    def product(self):
        """
        Return a :class:`GolemProcess` object for each iteration over
        the processing intervals and loops defined for this process
        view, possibly performing system level tasks along the way (such
        as creating output paths and performing input checks).
        Iterations where processing is complete will be skipped, unless
        :class:`overwrite_outputs <GolemProcess>` has been enabled for
        this object.
        """
        for gv in self.gview.product():
            gp = self.using(gv)
            try:
                gp._initialize()
                yield gp
                gp._finalize()
            except GolemException, e:
                if self.exception_handler:
                    try:
                        self.exception_handler(e, gv)
                        yield gv
                    except GolemIgnore:
                        pass
                else:
                    raise e

    def bins(self):
        """
        Provide an iterator over :class:`GolemProcess` objects for each
        processing interval represented by this view Iterations for
        which processing is complete will be skipped, unless
        :class:`overwrite_outputs <GolemProcess>` has been enabled for
        this object.
        """
        for gv in self.gview.bins():
            yield self.using(gv)

    def group_by(self, *keys):
        """
        Returns an iterator that yields a tuple with a primary key and
        a :class:`GolemProcess` object, grouped by the provided keys.
        Each primary key is a tuple containing the current values of the keys
        provided. Iterating over the resulting process objects process
        objects will resolve any remaining loops remaining in that view,
        if any. Views for which processing is complete will be skipped,
        unless :class:`overwrite_outputs <GolemProcess>` has been
        enabled for this object.
        """
        for pkey, gv in self.gview.group_by(*keys):
            yield pkey, self.using(gv)

    def by_key(self, key):
        """
        Similar to :meth:`group_by` but takes a single key as an
        argument. Returns and iterator that yields :class:`GolemProcess`
        objects for each value of the key. Views for which processing is
        complete will be skipped, unless :class:`overwrite_outputs
        <GolemProcess>` has been enabled for this object.
        """
        for gv in self.gview.by_key(key):
            yield self.using(gv)

    def is_complete(self):
        """
        Returns a boolean value indicating whether processing has been
        completed for the intervals represented by this view.
        """
        return GolemResource(self.outputs()).is_complete()

    def status(self, label):
        """
        Iterate over items within the given tag, returning a tuple
        containing the item string and its current status. Status is
        typically the size in bytes of each input or output, or ``None``
        if it does not exist.
        """
        r = GolemResource(self.gview._get_io(label))
        for _, _, status, item, _ in r.audit_by_label(label):
            yield item, status

    def __iter__(self):
        """
        Iterate over the views produced by the :meth:`product`
        method, yielding a dictionary of fully resolved template
        tags. Iterations for which processing is complete will be
        skipped, unless :class:`overwrite_outputs <GolemProcess>` has
        been enabled for this object.
        """
        for gp in self.product():
            yield gp.tags()

    ### delegate to GolemTags

    first_bin  = property(lambda x: x.gview.first_bin,
                          doc=GolemTags.first_bin.__doc__)
    last_bin   = property(lambda x: x.gview.last_bin,
                          doc=GolemTags.last_bin.__doc__)
    start_date = property(lambda x: x.gview.start_date,
                          doc=GolemTags.start_date.__doc__)
    end_date   = property(lambda x: x.gview.end_date,
                          doc=GolemTags.end_date.__doc__)
    golem      = property(lambda x: x.gview.golem)

    def bin_dates(self):
        return self.gview.bin_dates()
    bin_dates.__doc__ = GolemTags.bin_dates.__doc__

    def bin_count(self):
        return self.gview.bin_count()
    bin_count.__doc__ = GolemTags.bin_count.__doc__

    def loop_count(self):
        return self.gview.loop_count()
    loop_count.__doc__ = GolemTags.loop_count.__doc__

    def __len__(self):
        return self.gview.__len__()
    __len__.__doc__ = GolemTags.__len__.__doc__

    def tags(self):
        return self.gview.tags()
    tags.__doc__ = GolemTags.tags.__doc__

    def loop(self):
        return self.gview.loop()
    loop.__doc__ = GolemTags.loop.__doc__

    def outputs(self):
        return self.gview.outputs()
    outputs.__doc__ = GolemTags.outputs.__doc__

    def inputs(self):
        return self.gview.inputs()
    inputs.__doc__ = GolemTags.inputs.__doc__

###

_template_tags = {}

def _analyze_templates(*templates):
    labels = set()
    for g in templates:
        if isinstance(g, basestring):
            g = [g]
        for t in g:
            if t not in _template_tags:
                hits = {}
                while True:
                    try:
                        t % hits
                        break
                    except KeyError, e:
                        hits.update([(x, True) for x in e.args])
                _template_tags[t] = frozenset(hits)
            labels.update(_template_tags[t])
    return labels

###

def script_view():
    """
    Returns the currently defined global :class:`GolemView` object.
    """
    global _golem_view
    if _golem_view is None:
        raise GolemInitError("script_view invoked outside of main()")
    return _golem_view

def current_view(gv=None):
    """
    Returns a version of the given :class:`GolemView` object, which
    defaults to the main script view, for the most recent interval
    available.
    """
    if gv is None:
        gv = script_view()
    cb = gv._current_bin()
    return gv.using(first_date=cb, last_date=cb)

def is_complete(gv=None):
    """
    Examines the outputs of the optionally provided :class:`GolemView`
    object, which defaults to the main script view, and examines the
    status of the outputs for each processing interval. If all appear to
    be complete, returns ``True``, otherwise ``False``.
    """
    if gv is None:
        gv = script_view()
    return GolemResource(gv).is_complete()


###

def get_sensors():
    """
    Retrieves a list of sensors as defined in the local SiLK repository
    configuration.
    """
    return netsa.script._get_sensors()

def get_sensor_group(s):
    """
    Convenience function, such as can be passed as a value for the
    *group_by* parameter in :func:`add_sensor_loop`, for extracting a
    sensor 'group' out of a sensor name. Groups are determined by
    extracting prefixes made of 'word' characters excluding '_'. For
    example, two sensors called 'LAB0' and 'LAB1' would be grouped
    under 'LAB'.
    """
    return re.sub('(\W|_)*\d+\w?$', '', s)

def get_sensors_by_group(grouper=None, sensors=None):
    """
    Convenience function that uses the callable *grouper* to construct a
    tuple of named pairs of the form (group_name, members) suitable for
    use in constructing a dictionary. Defaults to the
    :func:`get_sensor_group` function.
    """
    if not grouper:
        grouper = get_sensor_group
    groups = {}
    order = []
    for s in sensors or get_sensors():
        g = grouper(s)
        if g not in groups:
            groups[g] = []
            order.append(g)
        groups[g].append(s)
    for i, g in enumerate(order):
        order[i] = (g, tuple(groups[g]))
    return tuple(order)

def get_args():
    """
    Returns a :class:`GolemArgs` object containing any non-parameter
    arguments that were provided to the script on the command line.
    """
    from optparse import OptionParser
    from netsa.script import params
    parser = OptionParser()
    for p in netsa.script._script._params:
        n, k = p['name'], p['kind']
        s = '--' + n
        if k is params.KIND_FLAG:
            parser.add_option(s, dest=n, default=True, action='store_true')
        else:
            parser.add_option(s, dest=n)
    return GolemArgs(parser.parse_args()[1])

###

from netsa.script import _print_failure, _print_warning

def _print_queue(out, gv):
    for date_str in _incomplete_bins_as_iso(gv):
        out.write(date_str + "\n")

def _print_complete(out, gv):
    for date_str in _complete_bins_as_iso(gv):
        out.write(date_str + "\n")

def _print_basic_outputs(out, gview, verbose=False, base=None):
    rsrc = GolemResource(gview.outputs())
    verbose = verbose or 1
    for r, _, _, args in rsrc.audit_expand():
        for f in args:
            out.write(r.repository_fmt(f, verbose=verbose) + "\n")

def _print_status(out, gview):
    def _status_row(gv, count=None):
        if not count:
            count = 0
        # fix later
        sstr = None
        hit = miss = 0
        tags = gv.loop()._basic_tags()
        first_iso = start_iso = None
        for _, _, exists, _, _ in GolemResource(gv).audit_all():
            if exists:
                hit += 1
            else:
                miss += 1
        if miss == 0:
            cstr = str(hit)
        else:
            cstr = "%d/%d" % (hit, hit + miss)
        row = [gv.golem.name, count]
        if sstr:
            row.append(sstr)
        row += [cstr,
                tags['golem_interval_iso'],
                tags['golem_span_iso'],
                gv.bin_count(),
                tags['golem_bin_iso'],
                tags['golem_start_iso'],
                tags['golem_end_iso']]
        return tuple(row)
    hrow = ['app', 'dep']
    # fix
    hrow += ['done', 'int', 'spn', 'bins',
             'first_bin', 'start_date', 'end_date']
    order = []
    seen = {}
    def _cascade(gview):
        key = (gview.golem.name, gview.first_bin, gview.last_bin)
        if key not in seen:
            order.append(key)
            seen[key] = gview
        else:
            gv = seen[key]
            go = gv.golem.output_templates
            for ot in gview.golem.output_templates:
                if ot not in go:
                    go += (ot,)
            seen[key] = gv.using(golem=gv.golem.using(output_templates=go))
        for gv in gview.members():
            _cascade(gv.inputs())
    _cascade(gview.inputs())
    stats = []
    for key in order:
        stats.append(_status_row(seen[key].outputs()))
    widths = [len(x) for x in hrow]
    for row in stats:
        for i, v in enumerate(row):
            w = len(str(v))
            if w > widths[i]:
                widths[i] = w
    tot = sum(widths)
    hfmt = ["%%%ds" % x for x in widths]
    hformat = ' '.join(hfmt) + "\n"
    fmt = list(hfmt)
    format = ' '.join(fmt) + "\n"
    div = '-' * (tot + len(hrow) - 1) + "\n"
    out.write(hformat % tuple(hrow))
    out.write(div)
    for row in stats:
        out.write(format % row)

def _incomplete_bins_as_iso(gv):
    group_by = lambda x: x[-1]['golem_bin_iso']
    auditor  = GolemResource(gv.outputs()).audit_by_bin()
    for bin_date, res in itertools.groupby(auditor, group_by):
        if all(x[2] for x in res):
            continue
        yield bin_date

def _complete_bins_as_iso(gv):
    group_by = lambda x: x[-1]['golem_bin_iso']
    auditor  = GolemResource(gv.outputs()).audit_by_bin()
    for bin_date, res in itertools.groupby(auditor, group_by):
        if all((x[2] for x in res)):
            yield bin_date

def _print_io(out, gview, verbose=False):
    hrow = ('bin', 'name', 'label', 'exist', 'item')
    widths = [len(x) for x in hrow]
    rows = []
    count  = 0

    items = set()
    for gv in gview.bins():
        for r, label, exists, f, tags in GolemResource(gv).audit_all():
            if f in items:
                continue
            items.add(f)
            bin_date = tags['golem_bin_iso']
            if not f:
                f = 'unavailable'
            if exists:
                exists = 'yes'
            else:
                exists = 'no'
            row = [bin_date, r.name, label, exists,
                   r.repository_fmt(f, verbose=verbose)]
            for i, v in enumerate(row):
                w = len(str(v))
                if w > widths[i]:
                    widths[i] = w
            rows.append(row)
    res_str = ''
    if rows:
        tot = sum(widths)
        fmt = ["%%%ds" % x for x in widths]
        fmt = ' '.join(fmt) + "\n"
        div = '-' * (tot + len(hrow) - 1) + "\n"
        out.write(fmt % hrow)
        out.write(div)
        for row in rows:
            out.write(fmt % tuple(row))

###

__all__ = netsa.script.__all__ + """

    set_default_home
    set_repository
    set_suite_name
    set_name
    set_interval
    set_span
    set_skew
    set_lag
    set_realtime
    set_tty_safe
    set_passive_mode

    get_script_path
    get_script_dir
    get_home
    get_repository

    add_golem_params
    add_golem_param
    add_golem_basic_params
    add_golem_query_params
    add_golem_repository_params
    modify_golem_param

    add_tag
    add_arg
    add_output_template
    add_input_template
    add_input_group
    add_output_group
    add_query_handler
    add_loop
    add_sensor_loop
    add_golem_input
    add_self_input
    add_flow_tag
    add_golem_source

    execute
    process
    loop
    inputs
    outputs

    is_complete
    script_view
    current_view

    get_sensors
    get_sensor_group
    get_sensors_by_group
    get_args

""".split()
