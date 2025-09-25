#  Copyright 2025 T-Systems International GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#
#
#
# This file includes code from:  pre-commit/pre-commit-hooks
# Repository: https://github.com/pre-commit/pre-commit-hooks/
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#
from __future__ import annotations

import unittest
from unittest.mock import patch

import pre_commit_hooks.util as lib


class UtilTests(unittest.TestCase):
    @patch('pre_commit_hooks.util.cmd_output', return_value='a.py\nb.txt\nc.md\n')
    def test_added_files_parses_lines_into_set(self, cmd):
        files = lib.added_files()
        self.assertEqual(files, {'a.py', 'b.txt', 'c.md'})

    @patch('pre_commit_hooks.util.cmd_output', return_value='')
    def test_added_files_empty_output_returns_empty_set(self, cmd):
        files = lib.added_files()
        self.assertEqual(files, set())

    @patch('pre_commit_hooks.util.cmd_output', return_value='a.py\na.py\nb.txt\n')
    def test_added_files_deduplicates(self, cmd):
        files = lib.added_files()
        self.assertEqual(files, {'a.py', 'b.txt'})

    @patch('pre_commit_hooks.util.cmd_output', return_value='single\n')
    def test_added_files_invokes_git_diff_with_expected_args(self, cmd):
        files = lib.added_files()
        self.assertEqual(files, {'single'})
        cmd.assert_called_once_with(
            'git', 'diff', '--staged', '--name-only', '--diff-filter=A'
        )

    def test_cmd_output_raises_on_error(self):
        with self.assertRaises(lib.CalledProcessError):
            lib.cmd_output('sh', '-c', 'exit 1')

    def test_cmd_output_returns_stdout(self):
        ret = lib.cmd_output('sh', '-c', 'echo hi')
        self.assertEqual(ret, 'hi\n')

    def test_zsplit_splits_str_correctly(self):
        for out in ('\0f1\0f2\0', '\0f1\0f2', 'f1\0f2\0'):
            with self.subTest(out=out):
                self.assertEqual(lib.zsplit(out), ['f1', 'f2'])

    def test_zsplit_returns_empty(self):
        for out in ('\0\0', '\0', ''):
            with self.subTest(out=out):
                self.assertEqual(lib.zsplit(out), [])
