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

import os, sys, re, time
from optparse   import OptionParser, OptionGroup, SUPPRESS_HELP
from tempfile   import NamedTemporaryFile
from subprocess import Popen, PIPE

###

def page_pod2man(pod, **kwargs):
    """
    Generate options, given as a POD encoded string, as a man page and
    send through a paging program as specified by the environment
    variables PERLPOD_PAGER, MANPAGER, or PAGER. If no pager is
    specified by those variables, 'less -isr' is attempted.
    """
    fh = NamedTemporaryFile()
    fh.write(pod)
    fh.flush()
    p2m_cmd = _pod2man_cmd(file=fh.name, **kwargs)
    fmt_cmd = ['nroff', '-man']
    pag_cmd = 'less -isr' 
    for env in ('PERLPOD_PAGER', 'MANPAGER', 'PAGER'):
        try:
            v = os.environ[env]
            if not v:
                continue
            pag_cmd = v
            break
        except KeyError:
            continue
    pag_cmd = re.split('\s+', pag_cmd)
    p2m_p = Popen(p2m_cmd, stdin=PIPE,         stdout=PIPE, shell=False)
    fmt_p = Popen(fmt_cmd, stdin=p2m_p.stdout, stdout=PIPE, shell=False)
    pag_p = Popen(pag_cmd, stdin=fmt_p.stdout, stdout=None, shell=False)
    pag_p.communicate()
    fh.close()

def pod2man(pod, **kwargs):
    """
    Return options, given as a POD encoded string, formatted as nroff.
    """
    fh = NamedTemporaryFile()
    fh.write(pod)
    fh.flush()
    p2m_cmd = _pod2man_cmd(file=fh.name, **kwargs)
    p_p2m = Popen(p2m_cmd, stdin=PIPE, stdout=PIPE, shell=False)
    man = p_p2m.communicate()[0]
    fh.close()
    return man

def _pod2man_cmd(file=None, **kwargs):
    p2m_opts = _pod2man_opts(**kwargs)
    p2m_cmd = ['pod2man']
    for k,v in p2m_opts.iteritems():
        p2m_cmd.extend(["--%s" % k,str(v)])
    if file:
        p2m_cmd.append(file)
    return p2m_cmd

def _pod2man_opts(name=None, section=1, release='', center='', date=None):
    if not name:
        name = os.path.basename(sys.argv[0]).upper()
    if not date:
        date = time.ctime(os.path.getctime(sys.argv[0])).split(' ')
        date = ' '.join([date[1], date[2], date[4]])
    if not release:
        import __main__
        for va in ('version', '__version__'):
            try:
                release = getattr(__main__, va)
            except AttributeError:
                continue
    return dict(name=name, section=section,
                release=release, center=center, date=date)

def flense(item):
    """
    Reformat strings by stripping each line and normalizing newlines.
    """
    if item == None:
        return
    paras = [x.strip() for x in re.split('\n{2,}', item.strip())]
    for i, p in enumerate(paras):
        paras[i] = '\n'.join([x.strip() for x in re.split('\n+', p.strip())])
    return '\n\n'.join(paras)

def all_groups(parser, level=0):
    """
    Iterator that provides all option groups.
    """
    yield(parser, level)
    try:
        for group in parser.option_groups:
            for (g, l) in all_groups(group, level+1):
                yield(g, l)
    except AttributeError:
        pass

def all_options(parser, level=0):
    """
    Iterator that provides all options from all option groups.
    """
    for (group, level) in all_groups(parser, level):
        if group.option_list:
            for option in group.option_list:
                yield(option, group, level)

def opt2pod(parser, level=0, expansions={}, groups_first=True, autofmt=False):
    """
    Given a parser object (OptionParser or Opt2Pod, for example), return
    options formatted as a POD encoded string.
    """
    def parser_and_formatter(parser):
        formatter = None
        p = parser
        while p:
            try:
                return (p, p.formatter)
            except AttributeError:
                try:
                    p = p.parser
                except AttributeError:
                    return (p, optparse.IndentedHelpFormatter())
    (p, f) = parser_and_formatter(parser)
    option_strings = set(p._short_opt.keys())
    option_strings.update(p._long_opt.keys())
    opat = sorted(option_strings)
    opat = '|'.join(map(lambda x: re.escape(x), opat))
    opat = re.compile("\s+(%s)" % opat)
    expansions.setdefault('prog', p.get_prog_name())
    def defaults2pod(option, formatter):
        expanded = formatter.expand_default(option)
        if option.help == expanded:
            return option.help
        parts = option.help.rsplit(formatter.default_tag)
        new = []
        while parts:
            part = parts.pop(0)
            (item, expanded) = expanded.split(part, 1)
            if item != '':
                new.append("I<%s>" % item)
            new.append(part)
        return ''.join(new)
    def option2pod(option, formatter):
        opt_str = formatter.format_option_strings(option)
        opts = re.split('\s*,\s*', opt_str)
        opts = map(lambda x: re.sub('^\s*([^=\s]+)', 'B<\g<1>>', x), opts)
        help = defaults2pod(option, formatter)
        if option.metavar:
            chunks = re.split('\s*\|\s*', option.metavar)
            if len(chunks) > 1:
                chunks.append(option.metavar)
            for str in chunks:
                str_pat = re.compile(re.escape(str))
                new_str = "I<%s>" % str.lower()
                opts = map(lambda x: str_pat.sub(new_str, x), opts)
                if help:
                    help = str_pat.sub(new_str, help)
                    help = opat.sub(' C<\g<1>>', help)
        pod = "=item %s" % ', '.join(opts)
        if help:
            if autofmt:
                help = flense(help)
            pod += "\n\n%s" % help
        return pod
    def options2pod(group):
        chunks = []
        if not group.option_list:
            return chunks
        (p, formatter) = parser_and_formatter(group)
        chunks.append('=over 4')
        for option in group.option_list:
            if option.help == SUPPRESS_HELP:
                continue
            chunks.append(option2pod(option, formatter))
            option_strings.update(option._short_opts)
            option_strings.update(option._long_opts)
        chunks.append('=back')
        return chunks
    doc = []
    for (group, level) in all_groups(parser, level):
        try:
            title = group.title
        except AttributeError:
            title = 'OPTIONS'
        doc.append("=head%d %s" % (level+1, title))
        if group.description:
            doc.append(group.description)
        if groups_first and group == parser:
            continue
        doc.extend(options2pod(group))
    if groups_first:
        doc.extend(options2pod(parser))
    return "\n\n".join(doc) % expansions

###

class Opt2Pod(OptionParser):
    """
    OptionParser subclass that adds additional options for returning
    options formatted as POD or nroff/man pages. Otherwise the class
    behaves just like OptionParser, including the traditional behavior
    of -h/--help. The extra options provided are::

        --opt2pod_brief : returns only option descriptions as POD
        --opt2pod       : returns option POD embedded in template
        --opt2man       : returns option POD embedded in template as nroff
        --man/-?        : returns option POD embedded in template as man page

    With the exception of --opt2pod_brief, the resulting pod string
    will be embedded in either the provided template attribute or
    the contents of __main__.POD (if present) with %(opt2pod)s in
    the contents.
    """
    def __init__(self, level=0, expansions={}, template=None,
                  groups_first=True, autofmt=False, suite=None, **kwargs):
        if autofmt and 'description' in kwargs:
            kwargs['description'] = flense(kwargs['description'])
        OptionParser.__init__(self, **kwargs)
        self.suite        = suite
        self.level        = level
        self.groups_first = groups_first
        self.autofmt      = autofmt
        self.template     = template
        self.expansions   = expansions
        self.expansions.setdefault('prog', self.get_prog_name())
        def handle_opt2pod_brief(option, opt, value, parser):
            print self.pod_opts()
            parser.exit()
        def handle_opt2pod(option, opt, value, parser):
            print self.pod()
            parser.exit()
        def handle_opt2man(option, opt, value, parser):
            print self.man()
            parser.exit()
        def handle_opt2page(option, opt, value, parser):
            self.page_man()
            parser.exit()
        self.add_option("--opt2pod_brief",
                        action="callback", callback=handle_opt2pod_brief,
                        help=SUPPRESS_HELP)
        self.add_option("--opt2pod",
                        action="callback", callback=handle_opt2pod,
                        help=SUPPRESS_HELP)
        self.add_option("--opt2man",
                        action="callback", callback=handle_opt2man,
                        help=SUPPRESS_HELP)
        self.add_option('-?', "--man",
                        action="callback", callback=handle_opt2page,
                        help="show full documentation as man page")

    def expand(self, item):
        item_map = self.expansions.copy()
        item_map['opt2pod'] = self.pod_opts()
        return item % item_map

    def pod_opts(self):
        return opt2pod(self, self.level, self.expansions,
                       self.groups_first, self.autofmt)

    def pod(self):
        if self.template:
            fh = open(self.template, 'r')
            pod = fh.read()
            fh.close()
            return self.expand(pod)
        else:
            import __main__
            try:
                return self.expand(__main__.POD)
            except AttributeError:
                return self.pod_opts()

    def man(self):
        return pod2man(self.pod(), center=self.suite)

    def page_man(self):
        page_pod2man(self.pod(), center=self.suite)

    def format_help(self, **kwargs):
        seen = set()
        if self.autofmt:
            for (option, group, level) in all_options(self):
                if group not in seen:
                    try:
                        group.description = flense(group.description)
                    except AttributeError:
                        pass
                try:
                    option.help = flense(option.help)
                except AttributeError:
                    pass
        return self.expand(OptionParser.format_help(self, **kwargs))

    def format_description(self, formatter):
        desc = self.get_description()
        if desc:
            desc = flense(desc)
            new_desc = []
            for p in re.split('\n{2,}', desc.strip()):
                new_desc.append(formatter.format_description(p.strip()).strip())
            return '\n\n'.join(new_desc) + '\n'
        else:
            return ''

###

__all__ = ['opt2pod', 'Opt2Pod']
