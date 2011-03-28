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

# Legacy version of netsa.dist

from distutils.command.build import build
from distutils.command.build_py import build_py
from distutils.command.build_ext import build_ext
from distutils.command.build_scripts import build_scripts
from distutils.command.install import install
from distutils.command.install_data import install_data
from distutils import log
from distutils.util import convert_path
from distutils.errors import *
from types import IntType, StringType
import os, string
from subprocess import Popen, PIPE

def get_revision():
    """
    Try get_mercurial_revision and get_subversion_revision in that
    order.  Take the first result that isn't UNKNOWN.
    """
    revision = get_mercurial_revision()
    if revision == "UNKNOWN":
        revision = get_subversion_revision()
    return revision

def get_mercurial_revision():
    """
    If subversion is available and this is a subversion-controlled
    directory, fetch the version number.  Otherwise, use the cached
    version number.  We fetch both a descriptor of the branch/tag, and
    the revision number.
    """
    revision = None
    try:
        p = None
        try:
            p = Popen(["hg", "identify", "-i"],
                      stdin=None, stdout=PIPE,
                      stderr=open("/dev/null", "r"))
            for l in p.stdout:
                l = l.strip()
                revision = l
        finally:
            if p: p.wait()
    except:
        pass
    if revision is None:
        try:
            f = None
            try:
                f = open(".hg_archival.txt", "r")
                for l in f:
                    (k, v) = l.strip().split(': ')
                    if k == "node":
                        revision
                revision = v[:12]
            finally:
                if f: f.close()
        except:
            # We know absolutely nothing
            pass
    if revision is not None:
        return revision
    else:
        return "UNKNOWN"

def get_subversion_revision():
    """
    If subversion is available and this is a subversion-controlled
    directory, fetch the version number.  Otherwise, use the cached
    version number.  We fetch both a descriptor of the branch/tag, and
    the revision number.
    """
    revision = None
    branch = ""
    try:
        p = None
        try:
            p = Popen(["svnversion", "-c"], stdin=None, stdout=PIPE)
            for l in p.stdout:
                l = l.strip()
                revision = l.split(":")[-1]
            if revision == "exported":
                revision = None
        finally:
            if p: p.wait()
    except:
        pass
    if revision is not None:
        try:
            p = None
            try:
                p = Popen(["svn", "info"], stdout=PIPE)
                for l in p.stdout:
                    if ":" not in l:
                        continue
                    (k, v) = l.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if k == "Repository Root":
                        repos_root = v
                    elif k == "URL":
                        repos_url = v
                if repos_url.startswith(repos_root):
                    branch = repos_url[len(repos_root)+1:]
                    if branch.startswith("trunk/"):
                        branch = ""
                    elif branch.startswith("branches/"):
                        branch = "-" + branch.split("/")[1]
                    elif branch.startswith("tags/"):
                        # FIXME: Using the whole tag here results in version
                        # numbers like "0.1.0.netsa-python-0.1.0".  It's
                        # probably best to return nothing when this is a tagged
                        # version.
                        #return branch.split("/")[1]
                        return None
                    else:
                        # We use the whole path
                        branch = "-R-" + branch.replace("/", "-")
                else:
                    # Something's going on that's not quite right.
                    branch = "-HUH"
            finally:
                if p: p.wait()
        except:
            pass
    if revision is not None:
        try:
            f = None
            try:
                f = open(".svnrevision", "w")
                print >>f, "%s|%s" % (revision, branch)
            finally:
                if f: f.close()
        except:
            # Couldn't write it, but no big deal.
            pass
    elif revision is None:
        try:
            f = None
            try:
                f = open(".svnrevision", "r")
                l = f.readline().strip()
                revision, branch = l.split("|")
            finally:
                if f: f.close()
        except:
            # We know absolutely nothing
            pass
    if revision is not None:
        if branch is None: branch = ""
        return revision + branch
    else:
        return "UNKNOWN"

class netsa_dist_build (build):

    user_options = build.user_options
    user_options.append(('src-dir=', None, "directory holding the source [default: .]"))

    def initialize_options (self):
        build.initialize_options(self)
        self.src_dir = None

    def finalize_options (self):
        if self.src_dir is None:
            self.src_dir = "."        

        build.finalize_options(self)
    
class netsa_dist_build_py (build_py):

    user_options = build_py.user_options
    user_options.append(('src-dir=', None, "directory holding the source [default: .]"))
        
    def initialize_options (self):
        build_py.initialize_options(self)
        self.src_dir = None
        
    def finalize_options (self):
    
        self.set_undefined_options('build',
                                   ('src_dir', 'src_dir'))
        if self.src_dir is None:
            self.src_dir = "."

        build_py.finalize_options(self)


    def get_package_dir (self, package):
        """Return the directory, relative to the top of the source
           distribution, where package 'package' should be found
           (at least according to the 'package_dir' option, if any)."""

        path = string.split(package, '.')
        if not self.package_dir:
            if path:
                return os.path.join(self.src_dir,apply(os.path.join, path))
            else:
                return self.src_dir
        else:
            tail = []
            while path:
                try:
                    pdir = self.package_dir[string.join(path, '.')]
                except KeyError:
                    tail.insert(0, path[-1])
                    del path[-1]
                else:
                    tail.insert(0, pdir)
                    return os.path.join(self.src_dir,apply(os.path.join, tail))

            else:
                # Oops, got all the way through 'path' without finding a
                # match in package_dir.  If package_dir defines a directory
                # for the root (nameless) package, then fallback on it;
                # otherwise, we might as well have not consulted
                # package_dir at all, as we just use the directory implied
                # by 'tail' (which should be the same as the original value
                # of 'path' at this point).
                pdir = self.package_dir.get('')
                if pdir is not None:
                    tail.insert(0, pdir)

                if tail:
                    return os.path.join(self.src_dir,apply(os.path.join, tail))
                else:
                    return self.src_dir

    def check_package (self, package, package_dir):

        # Empty dir name means current directory, which we can probably
        # assume exists.  Also, os.path.exists and isdir don't know about
        # my "empty string means current dir" convention, so we have to
        # circumvent them.
        if package_dir != "":
            if not os.path.exists(package_dir):
                if self.src_dir != ".":
                    raise DistutilsFileError, \
                      "package directory '%s' does not exist" % package_dir
                else:
                    os.makedirs(package_dir)                      
            if not os.path.isdir(package_dir):
                raise DistutilsFileError, \
                      ("supposed package directory '%s' exists, " +
                       "but is not a directory") % package_dir

        # Require __init__.py for all but the "root package"
        if package:
            #init_py = os.path.join(package_dir, "__init__.py")
            init_py = os.path.join(self.src_dir, package_dir, "__init__.py")
            if os.path.isfile(init_py):
                return init_py
            else:
                log.warn(("package init file '%s' not found " +
                          "(or not a regular file)"), init_py)

        # Either not in a package at all (__init__.py not expected), or
        # __init__.py doesn't exist -- so don't return the filename.
        return None


class netsa_dist_build_scripts (build_scripts):

    user_options = build_scripts.user_options
    user_options.append(('src-dir=', None, "directory holding the source [default: .]"))

    def initialize_options (self):
        build_scripts.initialize_options(self)
        self.src_dir = None
        
    def finalize_options (self):
        build_scripts.finalize_options(self)
    
        self.set_undefined_options('build',
                                   ('src_dir', 'src_dir'))

        if self.src_dir is None:
            self.src_dir = "."

class netsa_dist_install (install):
    user_options = install.user_options
    user_options.append(('src-dir=', None, "directory holding the source [default: .]"))

    def initialize_options (self):
        install.initialize_options(self)
        self.src_dir = None

    def finalize_options (self):
        if self.src_dir is None:
            self.src_dir = "."        
        install.finalize_options(self)

class netsa_dist_install_data (install_data):
    user_options = install_data.user_options
    user_options.append(('src-dir=', None, "directory holding the source [default: .]"))

    def initialize_options (self):
        install_data.initialize_options(self)
        self.src_dir = None

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('src_dir', 'src_dir'))
        if self.src_dir is None:
            self.src_dir = "."        

        install_data.finalize_options(self)

    def run (self):
        self.mkpath(self.install_dir)
        for f in self.data_files:
            if type(f) is StringType:
                # it's a simple file, so copy it
                f = convert_path(f)
                if self.warn_dir:
                    self.warn("setup script did not provide a directory for "
                              "'%s' -- installing right in '%s'" %
                              (f, self.install_dir))
                (out, _) = self.copy_file(os.path.join(self.src_dir, f), self.install_dir)
                self.outfiles.append(out)
            else:
                # it's a tuple with path to install to and a list of files
                dir = convert_path(f[0])
                if not os.path.isabs(dir):
                    dir = os.path.join(self.install_dir, dir)
                elif self.root:
                    dir = change_root(self.root, dir)
                self.mkpath(dir)

                if f[1] == []:
                    # If there are no files listed, the user must be
                    # trying to create an empty directory, so add the
                    # directory to the list of output files.
                    self.outfiles.append(dir)
                else:
                    # Copy files, adding them to the list of output files.
                    for data in f[1]:
                        data = convert_path(data)
                        (out, _) = self.copy_file(os.path.join(self.src_dir, data), dir)
                        self.outfiles.append(out)

__all__ = """
    get_revision
    get_mercurial_revision
    get_subversion_revision
    netsa_dist_build
    netsa_dist_build_py
    netsa_dist_build_scripts
    netsa_dist_install
    netsa_dist_install_data
""".split()
