#!/usr/bin/env python

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
# Contract F19628-00-C-0003. Carnegie Mellon University retains 
# copyrights in all material produced under this contract. The U.S. 
# Government retains a non-exclusive, royalty-free license to publish or 
# reproduce these documents, or allow others to do so, for U.S. 
# Government purposes only pursuant to the copyright license under the 
# contract clause at 252.227.7013.
# @OPENSOURCE_HEADER_END@

import os, sys
sys.path.insert(0, 'python')
del os.link    # Prevent hard linking in case of AFS
from distutils.cmd import Command
from distutils.core import setup
from distutils.command.build import build
from distutils.command.install import install
from distutils.command.install_data import install_data
from distutils.command.clean import clean
from distutils.version import LooseVersion
from distutils.dir_util import mkpath
from distutils.file_util import copy_file

import netsa
from netsa.dist import netsa_dist_build, netsa_dist_build_py, \
    netsa_dist_build_scripts, netsa_dist_build_scripts, \
    netsa_dist_install, netsa_dist_install_data, \
    get_revision

# This version number will be grabbed by autotools.
BASE_VERSION = netsa.__version__

# If this is is a svn dev build, we'll get some extra version info back.
full_version = BASE_VERSION
repo_version = get_revision()
if repo_version:
    full_version = "%s.%s" %(BASE_VERSION, repo_version)

def should_install(versionfile):
    my_ver = LooseVersion(full_version)
    if os.path.exists(versionfile):
        verfile = open(versionfile, 'r')
        installed_ver = LooseVersion(verfile.read().strip())
        verfile.close()
        if my_ver > installed_ver:
            return True
        else:
            print "will not install: version to be installed (%s)is not newer than existing version (%s)" %(my_ver, installed_ver)
            return False
    else:
        return True
    

class netsa_python_install(netsa_dist_install):
    def run(self):
        install_data_cmd = self.get_finalized_command('install_data')
        install_dir_root = getattr(install_data_cmd, 'install_dir')
        versionpath = os.path.join(install_dir_root, 'share', 'netsa-python')
        versionfile = os.path.join(versionpath, 'version.txt')
        if self.force or should_install(versionfile):
            netsa_dist_install.run(self)

class netsa_python_install_data(netsa_dist_install_data):
    def run(self):
        install_data_cmd = self.get_finalized_command('install_data')
        install_dir_root = getattr(install_data_cmd, 'install_dir')
        versionpath = os.path.join(install_dir_root, 'share', 'netsa-python')
        versionfile = os.path.join(versionpath, 'version.txt')
        if self.force or should_install(versionfile):
            netsa_dist_install_data.run(self)

class netsa_python_build(netsa_dist_build):
    sub_commands = build.sub_commands[:]
    sub_commands.append(('build_version', None))
    
class netsa_python_build_version(Command):
    def initialize_options (self):
        self.build_base = None

    def finalize_options (self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'))

    def run(self):
        #build_cmd = self.get_finalized_command('build')
        #versionpath = getattr(build_cmd, 'build_base')
        versionpath = self.build_base
        versionfile = os.path.join(versionpath, 'version.txt')
        print "writing version info to %s" %(versionfile)
        verfile = open(versionfile, 'w')
        verfile.write(full_version + "\n")
        verfile.close()

class netsa_python_install(netsa_dist_install):
    sub_commands = install.sub_commands[:]
    sub_commands.append(('install_version', None))
    
class netsa_python_install_version(Command):
    user_options = [
        ('root=', None,
         "install everything relative to this alternate root directory")
    ]
    def initialize_options (self):
        self.root = None
        self.outfiles = []

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('root', 'root'))
        if self.root is None:
            self.root = "/"

    def run(self):
        build_cmd = self.get_finalized_command('build')
        srcpath = getattr(build_cmd, 'build_base')
        srcfile = os.path.join(srcpath, 'version.txt')
        install_cmd = self.get_finalized_command('install')
        install_dir_base = getattr(install_cmd, 'install_base')
        dstpath = os.path.join(self.root + install_dir_base, 'share', 'netsa-python')
        print "dstpath: %s" %(dstpath)
        mkpath(dstpath)
        dstfile = os.path.join(dstpath, 'version.txt')
        copy_file(srcfile, dstfile)
        self.outfiles.append(dstfile)

    def get_inputs (self):
        return []

    def get_outputs (self):
        return self.outfiles


class netsa_python_clean(clean):

    user_options = clean.user_options

    def initialize_options (self):
        clean.initialize_options(self)
        self.build_base = None

    def finalize_options (self):
        clean.finalize_options(self)
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'))
                                   
    def run(self):
        versionfile = os.path.join(self.build_base, 'version.txt')
        if os.path.isfile(versionfile): os.remove(versionfile)
        clean.run(self)
    
distutils_spec = {
    "name": "netsa-python",
    "version": full_version,
    "description": "Python Components for NetSA",
    "maintainer": "CERT Network Situational Awareness Team",
    "maintainer_email": "flocontact@cert.org",
    "url": "http://tools.netsa.cert.org/",
    "package_dir": {"": "python"},
    "packages": [
        "netsa",
        "netsa.data",
        "netsa.files",
        "netsa.json",
        "netsa.json.simplejson",
        "netsa.logging",
        "netsa.script",
        "netsa.sql",
        "netsa.tools",
        "netsa.util",
        "netsa.util.sentinel",
        "netsa.util.sentinel.audit",
        "netsa.util.sentinel.ledger",
        "netsa.util.sentinel.sig",
    ],
    "options": {
        "install":{"optimize":1}
    },
    "data_files": [("share/netsa-python", ["sql/create-sa_meta-0.9.sql"] )],
    "cmdclass": {"build": netsa_python_build,
                 "build_py": netsa_dist_build_py,
                 "build_scripts": netsa_dist_build_scripts,
                 "build_version": netsa_python_build_version,
                 "install": netsa_python_install,
                 "install_data": netsa_dist_install_data,
                 "install_version": netsa_python_install_version,
                 "clean": netsa_python_clean
                 },
    "license": "GNU General Public License (GPL)",
    "platforms": "Unix",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: Unix",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Monitoring",
    ],
}

setup(**distutils_spec)
