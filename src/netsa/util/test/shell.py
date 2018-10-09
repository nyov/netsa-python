# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

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
