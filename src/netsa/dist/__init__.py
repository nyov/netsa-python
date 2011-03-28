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

import codecs
import distutils.core
import distutils.util
import distutils.filelist
import os
import os.path
import re
import sys

from netsa.files import relpath
from netsa.util.shell import run_parallel, command, pipeline
from distutils import dir_util, log
from distutils.dir_util import remove_tree

from glob import glob

### Overridden Distribution Class

source_dir_option = [('source-dir=', None,
                      "source directory for out-of-source builds")]

source_dir_default = os.path.dirname(sys.argv[0])

from distutils.dist import Distribution
class netsa_distribution(Distribution):
    global_options = Distribution.global_options + source_dir_option
    def __init__(self, attrs=None):
        self.source_dir = source_dir_default
        self.netsa_version_files = []
        self.netsa_doc_dir = None
        self.netsa_unit_test_modules = []
        self.netsa_other_test_modules = []
        self.netsa_extra_globs = []
        self.netsa_unit_tests = []
        self.netsa_other_tests = []
        self.netsa_copyright = ""
        self.netsa_dist_funcs = []
        Distribution.__init__(self, attrs=attrs)
    def finalize_options(self):
        self.source_dir = distutils.util.convert_path(self.source_dir)
        Distribution.finalize_options(self)

### Overridden Distutils Commands

# bdist
# bdist_dumb
# -- bdist_msi - added in 2.5.1
# bdist_rpm
# bdist_wininst

# build
from distutils.command.build import build
class netsa_build(build):
    def run(self):
        self.run_command('gen_version')
        build.run(self)

# build_clib - what the heck is this?  We don't use it

# build_ext
from distutils.command.build_ext import build_ext
from distutils.extension import Extension
class netsa_build_ext(build_ext):
    def get_package_dir(self):
        build_py = self.get_finalized_command("build_py")
        return relpath(build_py.get_package_dir(""),
                       self.distribution.source_dir)
    def get_source_files(self):
        build_py = self.get_finalized_command("build_py")
        self.check_extensions_list(self.extensions)
        filenames = []
        for ext in self.extensions:
            filenames.extend(os.path.join(self.distribution.source_dir,
                                          self.get_package_dir(),
                                          fn) for fn in ext.sources)
        return filenames
    def build_extension(self, ext):
        params = dict((k, getattr(ext, k, None)) for k in 
                      ['name', 'sources', 'include_dirs', 'define_macros',
                       'undef_macros', 'library_dirs', 'libraries',
                       'runtime_library_dirs', 'extra_objects',
                       'extra_compile_args', 'extra_link_args',
                       'export_symbols', 'swig_opts', 'depends', 'language']
                      if getattr(ext, k, None) != None)
        sources = params['sources']
        if self.distribution.source_dir:
            for fn in sources:
                fn = os.path.join(self.get_package_dir(), fn)
                self.mkpath(os.path.dirname(os.path.join(self.build_lib, fn)))
                self.copy_file(os.path.join(self.distribution.source_dir, fn),
                               os.path.join(self.build_lib, fn))
            params['sources'] = [
                os.path.join(self.build_lib, self.get_package_dir(), fn)
                for fn in sources]
        else:
            params['sources'] = [
                os.path.join(self.get_package_dir(), fn)
                for fn in sources]
        RESULT = build_ext.build_extension(self, Extension(**params))
    
# build_py
from distutils.command.build_py import build_py
class netsa_build_py(build_py):
    def get_package_dir(self, package):
        return os.path.join(self.distribution.source_dir,
                            build_py.get_package_dir(self, package))
    def find_data_files(self, package, src_dir):
        result = []
        for fn in build_py.find_data_files(self, package, src_dir):
            if os.path.isdir(fn):
                result.extend(distutils.filelist.findall(fn))
            else:
                result.append(fn)
        return result
    def run(self):
        self.run_command("gen_version")
        build_py.run(self)

# build_scripts
from distutils.command.build_scripts import build_scripts
class netsa_build_scripts(build_scripts):
    def copy_scripts(self):
        old_scripts = self.scripts
        self.scripts = [os.path.join(self.distribution.source_dir, script)
                        for script in self.scripts]
        build_scripts.copy_scripts(self)
        self.scripts = old_scripts

# clean
from distutils.command.clean import clean
class netsa_clean(clean):
    def run(self):
        if self.all:
            for (filename, template) in self.distribution.netsa_version_files:
                log.info("removing %r", filename)
                if not self.dry_run:
                    try:
                        os.unlink(filename)
                    except:
                        log.debug("%r doesn't exist -- can't clean it",
                                  filename)
            html_dir = self.get_finalized_command('gen_doc_html').gen_doc_html
            if os.path.exists(html_dir):
                remove_tree(html_dir, dry_run=self.dry_run)
            pdf_file = self.get_finalized_command('gen_doc_pdf').gen_doc_pdf
            log.info("removing %r", pdf_file)
            if not self.dry_run:
                try:
                    os.unlink(pdf_file)
                except:
                    log.debug("%r doesn't exist -- can't clean it",
                              pdf_file)
        latex_dir = self.get_finalized_command('gen_doc_pdf').gen_doc_latex
        extra_dir = self.get_finalized_command('gen_doc_pdf').gen_doc_extra
        if os.path.exists(latex_dir):
            remove_tree(latex_dir, dry_run=self.dry_run)
        if os.path.exists(extra_dir):
            remove_tree(extra_dir, dry_run=self.dry_run)
        clean.run(self)


# config
# install

# install_data
from distutils.command.install_data import install_data
class netsa_install_data(install_data):
    def run(self):
        old_data_files = self.data_files
        self.data_files = []
        for f in old_data_files:
            if isinstance(f, basestring):
                self.data_files.append(os.path.join(
                        self.distribution.source_dir, f))
            else:
                self.data_files.append(
                    (f[0], [os.path.join(self.distribution.source_dir, fn)
                            for fn in f[1]]))
        install_data.run(self)
        self.data_files = old_data_files

# -- install_egg_info - added in 2.5?
# install_headers
# install_lib
# install_scripts
# register

# sdist
from distutils.command.sdist import sdist
class netsa_sdist(sdist):
    def get_file_list(self, no_pdf=False):
        # Our own version, based on the 2.7 version plus special sauce
        self.filelist.findall()
        source_dir = self.distribution.source_dir
        if os.path.exists(os.path.join(source_dir, "README")):
            self.filelist.append(os.path.join(source_dir, "README"))
        elif os.path.exists(os.path.join(source_dir, "README.txt")):
            self.filelist.append(os.path.join(source_dir, "README.txt"))
        else:
            self.warn("standard file not found: should have one of "
                      "'README', 'README.txt'")
        if os.path.exists(os.path.join(source_dir, "GPL.txt")):
            self.filelist.append(os.path.join(source_dir, "GPL.txt"))
        else:
            self.warn("standard file 'GPL.txt' not found")
        if os.path.exists(os.path.join(source_dir, "LICENSE-OPENSOURCE.txt")):
            self.filelist.append(os.path.join(source_dir,
                                              "LICENSE-OPENSOURCE.txt"))
        else:
            self.warn("standard file 'LICENSE-OPENSOURCE.txt' not found")
        if os.path.exists(os.path.join(source_dir, "setup.py")):
            self.filelist.append(os.path.join(source_dir, "setup.py"))
        else:
            self.warn("standard file 'setup.py' not found")
        if os.path.exists(os.path.join(source_dir, "setup.cfg")):
            self.filelist.append(os.path.join(source_dir, "setup.cfg"))
        build_py = self.get_finalized_command('build_py')
        if self.distribution.has_pure_modules():
            self.filelist.extend(build_py.get_source_files())
        for pkg, src_dir, build_dir, filenames in build_py.data_files:
            for filename in filenames:
                self.filelist.append(os.path.join(src_dir, filename))
        if self.distribution.has_data_files():
            for item in self.distribution.data_files:
                if isinstance(item, str):
                    item = distutils.util.convert_path(item)
                    if os.path.isfile(item):
                        self.filelist.append(item)
                else:
                    dirname, filenames = item
                    for f in filenames:
                        f = distutils.util.convert_path(f)
                        if os.path.isfile(f):
                            self.filelist.append(f)
        if self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            self.filelist.extend(build_ext.get_source_files())
        if self.distribution.has_scripts():
            build_scripts = self.get_finalized_command('build_scripts')
            for sc in build_scripts.get_source_files():
                self.filelist.append(os.path.join(source_dir, sc))
        for g in self.distribution.netsa_extra_globs:
            g = distutils.util.convert_path(g)
            g = os.path.join(source_dir, g)
            for f in glob(g):
                if os.path.isfile(f):
                    self.filelist.append(f)
                elif os.path.isdir(f):
                    self.filelist.extend(distutils.filelist.findall(f))
        for (f, _) in self.distribution.netsa_version_files:
            self.filelist.append(f)
        if not no_pdf:
            gen_doc_pdf_cmd = self.get_finalized_command('gen_doc_pdf')
            self.run_command('gen_doc_pdf')
            self.filelist.extend(gen_doc_pdf_cmd.get_source_files())
            self.filelist.extend(gen_doc_pdf_cmd.get_generated_files())
        
        self.prune_file_list()
        self.filelist.sort()
        self.filelist.remove_duplicates()
    def make_release_tree (self, base_dir, files):
        # Taken from 2.7 version -- but also removes source_dir from dests
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames in
        'files' are created under 'base_dir', and then we hard link or copy
        (if hard linking is unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but in a
        directory named after the distribution, containing only the files
        to be distributed.
        """
        self.run_command('gen_version')

        source_dir = self.distribution.source_dir

        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' is just so we don't die
        # if the manifest happens to be empty.
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, [relpath(f, source_dir) for f in files],
                             dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist in its
        # corresponding location under 'base_dir', or copying each file
        # that's out-of-date in 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        link = None
        msg = "copying files to %s..." % base_dir

        if not files:
            log.warn("no files to distribute -- empty manifest?")
        else:
            log.info(msg)
        for file in files:
            if not os.path.isfile(file):
                log.warn("'%s' not a regular file -- skipping" % file)
            else:
                dest = destpath(file, [source_dir])
                dest = os.path.join(base_dir, dest)
                self.copy_file(file, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)

def destpath(filename, paths):
    for p in paths:
        if filename.startswith(p):
            return relpath(filename, p)
    return filename

# -- upload

### New Distutils Commands

from distutils.cmd import Command

class netsa_gen_version(Command):
    description = "Create generated 'version' files for project"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        self.already_run = False
        pass
    def run(self):
        if self.already_run:
            return
        self.already_run = True
        for (filename, template) in self.distribution.netsa_version_files:
            filename = os.path.join(self.distribution.source_dir, filename)
            self.mkpath(os.path.dirname(filename))
            verfile = None
            try:
                verfile = open(filename, 'w')
                verfile.write(template % self.distribution.get_version())
                verfile.close()
            except:
                verfile.close()
                raise

def get_theme_path():
    return __path__[0]

def gen_doc_config(distribution, target_dir):
    conf_py_in = open(os.path.join(__path__[0],
                                   'netsa_sphinx_config.py.in'), 'r')
    conf_py_out = open(os.path.join(target_dir, 'netsa_sphinx_config.py'), 'w')
    conf_py_out.write(conf_py_in.read() % {
            'project_name': distribution.get_name(),
            'project_title': distribution.get_description(),
            'project_copyright': distribution.netsa_copyright,
            'project_version': distribution.get_version(),
            })
    conf_py_in.close()
    conf_py_out.close()

class netsa_gen_doc_html(Command):
    description = "Create generated HTML documentation files for project"
    user_options = []
    def initialize_options(self):
        self.gen_doc_html = None
        self.gen_doc_extra = None
    def finalize_options(self):
        build_base = self.get_finalized_command('build').build_base
        if self.gen_doc_html is None:
            self.gen_doc_html = os.path.join(self.distribution.netsa_doc_dir,
                                             'html')
        if self.gen_doc_extra is None:
            self.gen_doc_extra = os.path.join(build_base, 'gen.doc.extra')
    def run(self):
        self.run_command('build')
        build_lib = self.get_finalized_command('build').build_lib
        if self.distribution.netsa_doc_dir:
            self.mkpath(self.gen_doc_extra)
            gen_doc_config(self.distribution, self.gen_doc_extra)
            old_pythonpath = None
            try:
                if 'PYTHONPATH' in os.environ:
                    old_pythonpath = os.environ['PYTHONPATH']
                    os.environ['PYTHONPATH'] = (
                        self.gen_doc_extra + ':' + build_lib +
                        ':' + old_pythonpath)
                else:
                    os.environ['PYTHONPATH'] = (
                        self.gen_doc_extra + ":" + build_lib)
                cmd = command("sphinx-build",
                              "-b", "html",
                              "-d", self.gen_doc_extra,
                              os.path.join(self.distribution.source_dir,
                                           self.distribution.netsa_doc_dir),
                              self.gen_doc_html)
                log.info("generating HTML documentation with Sphinx")
                log.debug("PYTHONPATH=%s %s", os.environ['PYTHONPATH'], cmd)
                run_parallel([cmd], stdout=sys.stdout, stderr=sys.stderr)
            finally:
                if old_pythonpath:
                    os.environ['PYTHONPATH'] = old_pythonpath
                else:
                    del os.environ['PYTHONPATH']
    def get_source_files(self):
        return distutils.filelist.findall(
            os.path.join(self.distribution.source_dir,
                         self.distribution.netsa_doc_dir))
    def get_generated_files(self):
        # Only after running!
        return distutils.filelist.findall(self.gen_doc_html)

def convert_file_to_8859_1(filename):
    out_filename = filename + ".fixed"
    sys.stdout.write(filename +": ")
    f = codecs.open(filename, 'r', 'utf-8')
    s = f.read()
    f.close()
    out = codecs.open(out_filename, 'w', 'iso-8859-1')
    for c in s:
        if ord(c) < 128:
            out.write(c)
        else:
            sys.stdout.write("*")
            out.write("&#%d;" % ord(c))
    out.close()
    sys.stdout.write(" ok\n")
    os.rename(out_filename, filename)

def convert_html_to_8859_1(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(".html"):
                convert_file_to_8859_1(os.path.join(dirpath, filename))

class netsa_gen_doc_tools_web(Command):
    description = "Create generated HTML documentation files for project"
    user_options = []
    def initialize_options(self):
        self.gen_doc_web = None
        self.gen_doc_extra = None
    def finalize_options(self):
        build_base = self.get_finalized_command('build').build_base
        self.base_name = ('%s-%s-doc-web' % (self.distribution.get_name(),
                                             self.distribution.get_version()))
        if self.gen_doc_web is None:
            self.gen_doc_web = os.path.join(build_base, 'gen.doc.web')
        if self.gen_doc_extra is None:
            self.gen_doc_extra = os.path.join(build_base, 'gen.doc.extra')
    def run(self):
        self.run_command('build')
        build_lib = self.get_finalized_command('build').build_lib
        if self.distribution.netsa_doc_dir:
            self.mkpath(self.gen_doc_extra)
            gen_doc_config(self.distribution, self.gen_doc_extra)
            old_pythonpath = None
            try:
                if 'PYTHONPATH' in os.environ:
                    old_pythonpath = os.environ['PYTHONPATH']
                    os.environ['PYTHONPATH'] = (
                        self.gen_doc_extra + ':' + build_lib +
                        ':' + old_pythonpath)
                else:
                    os.environ['PYTHONPATH'] = (
                        self.gen_doc_extra + ":" + build_lib)
                cmd = command("sphinx-build",
                              "-b", "html",
                              "-D", "html_theme=tools_web",
                              "-D", "html_style=tools.css",
                              "-d", self.gen_doc_extra,
                              os.path.join(self.distribution.source_dir,
                                           self.distribution.netsa_doc_dir),
                              os.path.join(self.gen_doc_web, self.base_name))
                log.info("generating tools site HTML documentation with Sphinx")
                log.debug("PYTHONPATH=%s %s", os.environ['PYTHONPATH'], cmd)
                run_parallel([cmd], stdout=sys.stdout, stderr=sys.stderr)
            finally:
                if old_pythonpath:
                    os.environ['PYTHONPATH'] = old_pythonpath
                else:
                    del os.environ['PYTHONPATH']
            log.info("converting UTF-8 to ISO-8859-1")
            convert_html_to_8859_1(os.path.join(self.gen_doc_web,
                                                self.base_name))
            self.make_archive(os.path.join('dist', self.base_name),
                              'gztar', self.gen_doc_web, self.base_name)
                              

class netsa_gen_doc_pdf(Command):
    description = "Create generated PDF documentation files for project"
    user_options = []
    def initialize_options(self):
        self.gen_doc_latex = None
        self.gen_doc_pdf = None
        self.gen_doc_extra = None
    def finalize_options(self):
        build_base = self.get_finalized_command('build').build_base
        if self.gen_doc_latex is None:
            self.gen_doc_latex = os.path.join(build_base, 'gen.doc.latex')
        if self.gen_doc_pdf is None:
            self.gen_doc_pdf = \
                ("%s-%s.pdf" % (self.distribution.get_name(),
                                self.distribution.get_version()))
        if self.gen_doc_extra is None:
            self.gen_doc_extra = os.path.join(build_base, 'gen.doc.extra')
    def run(self):
        self.run_command('build')
        build_lib = self.get_finalized_command('build').build_lib
        if self.distribution.netsa_doc_dir:
            self.mkpath(self.gen_doc_extra)
            gen_doc_config(self.distribution, self.gen_doc_extra)
            old_pythonpath = None
            try:
                if 'PYTHONPATH' in os.environ:
                    old_pythonpath = os.environ['PYTHONPATH']
                    os.environ['PYTHONPATH'] = (
                        self.gen_doc_extra + ':' + build_lib +
                        ':' + old_pythonpath)
                else:
                    os.environ['PYTHONPATH'] = (
                        self.gen_doc_extra + ":" + build_lib)
                cmd = command("sphinx-build",
                              "-b", "latex",
                              "-d", self.gen_doc_extra,
                              os.path.join(self.distribution.source_dir,
                                           self.distribution.netsa_doc_dir),
                              self.gen_doc_latex)
                log.info("generating PDF documentation with Sphinx")
                log.debug("PYTHONPATH=%s %s", os.environ['PYTHONPATH'], cmd)
                try:
                    run_parallel([cmd], stdout=sys.stdout, stderr=sys.stderr)
                except Exception, ex:
                    log.error(str(ex))
                    sys.exit(-1)
            finally:
                if old_pythonpath:
                    os.environ['PYTHONPATH'] = old_pythonpath
                else:
                    del os.environ['PYTHONPATH']
            latex_name = ("%s.tex" % self.distribution.get_name())
            pdf_name = ("%s.pdf" % self.distribution.get_name())
            curdir = os.getcwd()
            try:
                os.chdir(self.gen_doc_latex)
                try:
                    run_parallel(["pdflatex %(latex_name)s"],
                                 vars={'latex_name': latex_name})
                    run_parallel(["pdflatex %(latex_name)s"],
                                 vars={'latex_name': latex_name})
                    run_parallel(["pdflatex %(latex_name)s"],
                                 vars={'latex_name': latex_name})
                except Exception, ex:
                    log.error(str(ex))
                    sys.exit(-1)
            finally:
                os.chdir(curdir)
            self.copy_file(os.path.join(self.gen_doc_latex, pdf_name),
                           self.gen_doc_pdf)
    def get_source_files(self):
        return distutils.filelist.findall(
            os.path.join(self.distribution.source_dir,
                         self.distribution.netsa_doc_dir))
    def get_generated_files(self):
        # Only after running!
        return [self.gen_doc_pdf]

class netsa_check(Command):
    description = "Run automated tests for project"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.run_command('check_unit')
        self.run_command('check_other')

class netsa_check_unit(Command):
    description = "Run automated unit tests for project"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.run_command('build')
        build_lib = self.get_finalized_command('build').build_lib
        old_pythonpath = None
        try:
            if 'PYTHONPATH' in os.environ:
                old_pythonpath = os.environ['PYTHONPATH']
                os.environ['PYTHONPATH'] = build_lib + ':' + old_pythonpath
            else:
                os.environ['PYTHONPATH'] = build_lib
            python_exec = os.path.normpath(sys.executable)
            log.info("running unit tests...")
            try:
                cmd = command(python_exec, "-m", "netsa.dist.run_unit_tests",
                              "-v", *self.distribution.netsa_unit_test_modules)
                log.debug("PYTHONPATH=%s %s", os.environ['PYTHONPATH'], cmd)
                run_parallel([cmd], stdout=sys.stdout, stderr=sys.stderr)
            except:
                log.info("running unit tests... failed")
                sys.exit(-1)
            log.info("running unit tests... success")
        finally:
            if old_pythonpath:
                os.environ['PYTHONPATH'] = old_pythonpath
            else:
                del os.environ['PYTHONPATH']

class netsa_check_other(Command):
    description = "Run other automated tests for project"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.run_command('build')
        build_lib = self.get_finalized_command('build').build_lib
        old_pythonpath = None
        try:
            if 'PYTHONPATH' in os.environ:
                old_pythonpath = os.environ['PYTHONPATH']
                os.environ['PYTHONPATH'] = build_lib + ':' + old_pythonpath
            else:
                os.environ['PYTHONPATH'] = build_lib
            python_exec = os.path.normpath(sys.executable)
            log.info("running other tests...")
            errors = False
            for test_mod in self.distribution.netsa_other_test_modules:
                try:
                    cmd = command(python_exec, "-m", test_mod,
                                  self.distribution.source_dir)
                    log.debug("PYTHONPATH=%s %s",
                              os.environ['PYTHONPATH'], cmd)
                    run_parallel([cmd], stdout=sys.stdout, stderr=sys.stderr)
                except:
                    errors = True
            if errors:
                log.info("running other tests... failed")
                sys.exit(-1)
            log.info("running other tests... success")
        finally:
            if old_pythonpath:
                os.environ['PYTHONPATH'] = old_pythonpath
            else:
                del os.environ['PYTHONPATH']

class netsa_dist(Command):
    description = "Generate standard items for a NetSA release"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.run_command('sdist')
        self.run_command('gen_doc_tools_web')
        for func in self.distribution.netsa_dist_funcs:
            func(self)

class netsa_src_license(Command):
    description = "(CAREFUL) Modify source files in place to update license"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        sdist = self.get_finalized_command('sdist')
        sdist.filelist = distutils.filelist.FileList()
        sdist.check_metadata()
        sdist.get_file_list(no_pdf=True)
        source_files = sdist.filelist.files
        license_dir = self.distribution.source_dir
        if not license_dir: license_dir = '.'
        license_text = {}
        log.info("reading licenses from %r:", license_dir)
        for license_file in os.listdir(license_dir):
            license_path = os.path.join(license_dir, license_file)
            if (license_file.startswith("LICENSE-") and
                license_file.endswith(".txt") and
                os.path.isfile(license_path)):
                license_text[license_file[8:-4]] = \
                    open(license_path, 'r').readlines();
                log.info("    %r", license_file)
        def printheader(out, license, prefix):
            for l in license_text[license]:
                out.write(prefix)
                out.write(l)
        re_start = re.compile(
            r"^(?P<prefix>.*)\@(?P<license>[^@]+)_HEADER_START\@")
        re_end = re.compile(r"\@(?P<license>[^@]+)_HEADER_END\@")
        log.info("updating licenses in files:")
        for f in source_files:
            if not os.path.isfile(f):
                continue
            in_header = False
            matched = False
            in_file = open(f, 'r')
            out_file = open(f + ".fixed-license", 'w')
            for l in in_file:
                m = re_start.search(l)
                if m and m.group('license') in license_text:
                    # Matched start of hreader section for a license we know
                    in_header = True
                    matched = True
                    out_file.write(l)
                    printheader(out_file, m.group('license'),
                                m.group('prefix'))
                    continue
                m = re_end.search(l)
                if m:
                    # Matched end of header section
                    in_header = False
                    out_file.write(l)
                    continue
                if in_header:
                    # Throw away old header
                    continue
                out_file.write(l)
            in_file.close()
            out_file.close()
            if matched:
                # We replaced some stuff
                os.rename(f, f + ".bak")
                os.rename(f + ".fixed-license", f)
                log.info("    %r - updated", f)
            else:
                os.unlink(f + ".fixed-license")
                log.info("    %r - unchanged", f)

        

### Storage for the config info

dist_info = {'package_dir': {'': 'src'},
             'license': 'GPL'}
dist_package = []
dist_package_data = {}
dist_module_py = []
dist_module_ext = []
dist_scripts = []
dist_data_files = []
dist_doc_dir = 'doc'
dist_version_files = []
dist_test_functions = []
dist_unit_test_modules = []
dist_other_test_modules = []
dist_extra_globs = []
dist_funcs = []

re_email_1 = re.compile(r"""
    ^
    (?P<name_1>[^<]*)
    < (?P<email_1>[^>]*) >
    (?P<name_2>.*)
    $
""", re.VERBOSE)

re_email_2 = re.compile(r"""
    ^
    (?P<email_1>[^"]+)
    (?: " (?P<name_1> (?: [^"\\]+ | \\. )* ) " )?
    (?P<email_2>.*)
    $
""", re.VERBOSE)

def split_email(s):
    m = re_email_1.match(s)
    if m:
        return (' '.join((m.group('name_1') + " " +
                          m.group('name_2')).strip().split()),
                m.group('email_1').strip())
    m = re_email_2.match(s)
    if m:
        return (' '.join((m.group('name_1') or "").strip().split()),
                (m.group('email_1') + m.group('email_2')).strip())

### Standard Metadata and Config

def set_name(project_name):
    dist_info['name'] = project_name

def set_title(project_title):
    dist_info['description'] = project_title

def set_description(project_description):
    dist_info['long_description'] = project_description

def set_version(project_version):
    dist_info['version'] = project_version

def set_copyright(project_copyright):
    dist_info['netsa_copyright'] = project_copyright

def set_license(project_license):
    dist_info['license'] = project_license

def set_maintainer(project_maintainer):
    (maint_name, maint_email) = split_email(project_maintainer)
    dist_info['maintainer'] = maint_name
    dist_info['maintainer_email'] = maint_email

def set_author(project_author):
    (author_name, author_email) = split_email(project_author)
    dist_info['author'] = author_name
    dist_info['author_email'] = author_email

def set_url(project_url):
    dist_info['url'] = project_url

def set_download_url(project_download_url):
    dist_info['download_url'] = project_download_url

def _deprecated_set_package_dir(project_python_dir):
    dist_info['package_dir'] = {'': project_python_dir}

def add_package(package_name):
    dist_package.append(package_name)

def add_package_data(package_name, data_file_glob):
    dist_package_data[package_name] = \
        dist_package_data.get(package_name, []) + [data_file_glob]

def add_module_py(module_name):
    dist_module_py.append(module_name)

def add_module_ext(module_name, module_sources, **kwargs):
    dist_module_ext.append(
        distutils.extension.Extension(module_name, module_sources, **kwargs))

def add_script(script_name):
    dist_scripts.append(os.path.join("bin", script_name))

def add_install_data(install_path, data_file_name):
    dist_data_files.append((install_path, [data_file_name]))

def add_extra_files(extra_glob):
    dist_extra_globs.append(extra_glob)

### Version File Generation

default_template = "%s\n"

def add_version_file(version_file_name,
                     version_file_template=default_template):
    dist_version_files.append((version_file_name, version_file_template))
    if version_file_name.startswith("src/"):
        if not version_file_name.endswith(".py"):
            version_package = os.path.dirname(version_file_name[4:])
            version_package = re.sub('/', '.', version_package)
            add_package_data(version_package,
                             os.path.basename(version_file_name))

### Documentation Generation

def deprecated_set_doc_dir(project_doc_dir):
    global dist_doc_dir
    dist_doc_dir = project_doc_dir

### Tests and Unit Tests

def add_unit_test_module(script_unit_test_module):
    dist_unit_test_modules.append(script_unit_test_module)

def add_other_test_module(script_other_test_module):
    dist_other_test_modules.append(script_other_test_module)

### Extra distribution generation steps

def add_dist_func(script_dist_func):
    dist_funcs.append(script_dist_func)

###

def execute():
    # Make sure to use sane umask to install
    old_umask = None
    try:
        old_umask = os.umask(0022)
    except:
        pass
    setup_args = dict(dist_info)
    setup_args['cmdclass'] = {'clean': netsa_clean,
                              'build': netsa_build,
                              'build_ext': netsa_build_ext,
                              'build_py': netsa_build_py,
                              'build_scripts': netsa_build_scripts,
                              'gen_version': netsa_gen_version,
                              'gen_doc_html': netsa_gen_doc_html,
                              'gen_doc_tools_web': netsa_gen_doc_tools_web,
                              'gen_doc_pdf': netsa_gen_doc_pdf,
                              'install_data': netsa_install_data,
                              'sdist': netsa_sdist,
                              'check': netsa_check,
                              'check_unit': netsa_check_unit,
                              'check_other': netsa_check_other,
                              'netsa_src_license': netsa_src_license,
                              'netsa_dist': netsa_dist}
    setup_args['distclass'] = netsa_distribution
    setup_args['packages'] = dist_package
    setup_args['package_data'] = dist_package_data
    setup_args['py_modules'] = dist_module_py
    setup_args['ext_modules'] = dist_module_ext
    setup_args['scripts'] = dist_scripts
    setup_args['data_files'] = dist_data_files
    setup_args['netsa_version_files'] = dist_version_files
    setup_args['netsa_doc_dir'] = dist_doc_dir
    setup_args['netsa_unit_test_modules'] = dist_unit_test_modules
    setup_args['netsa_other_test_modules'] = dist_other_test_modules
    setup_args['netsa_extra_globs'] = dist_extra_globs
    setup_args['netsa_dist_funcs'] = dist_funcs
    setup_args['options'] = {'install': {'optimize': 1}}
    distutils.core.setup(**setup_args)
    try:
        os.umask(old_umask)
    except:
        pass

from legacy import *

__all__ = """

    set_name
    set_title
    set_description
    set_version
    set_copyright
    set_license
    set_maintainer
    set_author
    set_url
    set_download_url

    add_package
    add_package_data
    add_module_py
    add_module_ext
    add_script
    add_install_data
    add_extra_files

    add_version_file

    add_unit_test_module
    add_other_test_module

    add_dist_func

""".split() + legacy.__all__
