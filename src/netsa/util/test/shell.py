# Copyright 2011 by Carnegie Mellon University

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

import unittest

from netsa.files import get_temp_file_name, get_temp_pipe_name
from netsa.util.shell import *

class ShellTest(unittest.TestCase):

    def test_run_parallel_1(self):
        f1 = get_temp_file_name()
        run_parallel(["echo foo", ">%(f1)s"],
                     vars={"f1": f1})
        content = open(f1, "r").read()
        self.assertEqual(content, "foo\n")

    def test_run_parallel_2(self):
        f1 = get_temp_file_name()
        f2 = get_temp_file_name()
        run_parallel(["echo foo", ">%(f1)s"],
                     ["echo bar", ">%(f2)s"],
                     vars={"f1": f1, "f2": f2})
        content1 = open(f1, "r").read()
        content2 = open(f2, "r").read()
        self.assertEqual(content1, "foo\n")
        self.assertEqual(content2, "bar\n")

    def test_run_parallel_3(self):
        p1 = get_temp_pipe_name()
        f1 = get_temp_file_name()
        run_parallel(["echo foo", ">%(p1)s"],
                     ["<%(p1)s", "cat", ">%(f1)s"],
                     vars={"f1": f1, "p1": p1})
        content1 = open(f1, "r").read()
        self.assertEqual(content1, "foo\n")

    def test_run_parallel_4(self):
        p1 = get_temp_pipe_name()
        self.assertRaises(
            PipelineException,
            run_parallel,
            ["echo foo", ">%(p1)s"], # should block forever
            ["false"],               # should fail immediately
            vars={"p1": p1})

    def test_run_parallel_5(self):
        f1 = get_temp_file_name()
        run_parallel(pipeline("echo foo", stdout=f1),
                     [command("false", ignore_exit_status=True)])
        content1 = open(f1, "r").read()
        self.assertEqual(content1, "foo\n")

    def test_run_parallel_6(self):
        f1 = get_temp_file_name()
        self.assertRaises(
            PipelineException,
            run_parallel,
            pipeline(command("echo", "foo"), stdout=f1),
            [command("false", ignore_exit_statuses=[2])])

    def test_run_collect_1(self):
        f1 = get_temp_file_name()
        f = open(f1, 'w')
        f.write("foo\nbar\n")
        f.close()
        f = open(f1, 'r')
        (stdout, stderr) = run_collect(
            command("cat"), command("sort"), command("cat"),
            stdin=f)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, "bar\nfoo\n")

    def test_run_collect_files_1(self):
        f1 = get_temp_file_name()
        f = open(f1, 'w')
        f.write("foo\nbar\n")
        f.close()
        f = open(f1, 'r')
        (stdout, stderr) = run_collect_files(
            command("cat"), command("sort"), command("cat"),
            stdin=f)
        self.assertEqual(stderr.read(), "")
        self.assertEqual(stdout.read(), "bar\nfoo\n")
        stdout.close()
        stderr.close()
