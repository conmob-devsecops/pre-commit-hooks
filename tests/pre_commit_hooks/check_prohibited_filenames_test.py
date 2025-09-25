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

import argparse
import io
import os
import runpy
import sys
import unittest
from contextlib import redirect_stdout

import pre_commit_hooks.check_prohibited_filenames as lib


class ProhibitedFilenamesUnitTests(unittest.TestCase):
    def test_match_filename_basename(self):
        # Exact basename match
        self.assertTrue(lib._match_filename('dir/sub/README.md', ['README.md']))
        self.assertTrue(lib._match_filename('README.md', ['dir/README.md']))
        # POSIX path: case-sensitive
        if os.name != 'nt':
            self.assertFalse(lib._match_filename('dir/sub/readme.md', ['README.md']))

    def test_matches_patterns_basename_and_components(self):
        # No separator pattern checks basename
        self.assertTrue(lib._matches_patterns('a/b/file.txt', ['*.txt']))
        self.assertFalse(lib._matches_patterns('a/b/file.txt', ['*.md']))
        # Component scan for patterns without separators (has glob meta)
        self.assertTrue(lib._matches_patterns('x/whoopie/z.txt', ['*whoop*']))
        self.assertFalse(lib._matches_patterns('x/y/z.txt', ['*whoop*']))

    def test_matches_patterns_with_separators_and_recursive(self):
        self.assertTrue(lib._matches_patterns('a/secrets/cred.pem', ['**/secrets/*']))
        self.assertFalse(lib._matches_patterns('secrets.pem', ['**/secrets/*']))
        # Mixed: one matches, one not
        self.assertTrue(
            lib._matches_patterns('keys/id_rsa.pem', ['**/secrets/*', '*.pem'])
        )

    def test_find_prohibited_reports_and_returns_1(self):
        prohibited_filenames = ['README.md']
        prohibited_patterns = ['*.pem', '**/secrets/*']
        filenames = [
            'docs/README.md',
            'keys/id_rsa.pem',
            'src/secrets/api_key.txt',
            'src/ok.txt',
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lib.find_prohibited(
                prohibited_filenames, prohibited_patterns, filenames
            )
        out = buf.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn('Prohibited filename(s) found:', out)
        self.assertIn('docs/README.md', out)
        self.assertIn('keys/id_rsa.pem', out)
        self.assertIn('src/secrets/api_key.txt', out)
        self.assertNotIn('src/ok.txt', out)

    def test_find_prohibited_clean_returns_0_and_no_output(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lib.find_prohibited(
                prohibited_filenames=['LICENSE'],
                prohibited_patterns=['*.pem'],
                filenames=['src/main.py', 'README.md'],
            )
        self.assertEqual(rc, 0)
        self.assertEqual(buf.getvalue().strip(), '')

    def test_main_parses_comma_lists_and_flags(self):
        args = [
            '--prohibited-filenames',
            'README.md,LICENSE',
            '--prohibited-patterns',
            '*.pem,**/secrets/*',
            'docs/README.md',
            'a/secrets/x.txt',
            'ok.txt',
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lib.main(args)
        out = buf.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn('docs/README.md', out)
        self.assertIn('a/secrets/x.txt', out)
        self.assertNotIn('ok.txt', out)

    def test_main_no_matches_returns_0(self):
        args = [
            '--prohibited-filenames',
            'LICENSE',
            '--prohibited-patterns',
            '*.pem',
            'src/main.py',
            'README.md',
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lib.main(args)
        self.assertEqual(rc, 0)
        self.assertEqual(buf.getvalue().strip(), '')

    def test_action_comma_separated_list_flattens_multiple_values(self):
        # Cover the branch where the action receives a list of strings.
        parser = argparse.ArgumentParser()
        parser.add_argument('--vals', action=lib.CommaSeparatedList, nargs='*')
        ns = parser.parse_args(['--vals', 'a,b', 'c', 'd,,', ' e , f '])
        self.assertEqual(ns.vals, ['a', 'b', 'c', 'd', 'e', 'f'])


class ProhibitedFilenamesMainGuardTests(unittest.TestCase):
    def test_main_guard_exits_1_on_violation(self):
        argv = [
            'pre_commit_hooks.check_prohibited_filenames',
            '--prohibited-patterns',
            '*.pem',
            'id_rsa.pem',
        ]
        buf = io.StringIO()
        mod = 'pre_commit_hooks.check_prohibited_filenames'
        saved = sys.modules.pop(mod, None)
        try:
            with redirect_stdout(buf), unittest.mock.patch.object(sys, 'argv', argv):
                with self.assertRaises(SystemExit) as ctx:
                    runpy.run_module(mod, run_name='__main__')
        finally:
            if saved is not None:
                sys.modules[mod] = saved
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn('Prohibited filename(s) found:', buf.getvalue())

    def test_main_guard_exits_0_when_clean(self):
        argv = [
            'pre_commit_hooks.check_prohibited_filenames',
            '--prohibited-filenames',
            'LICENSE',
            'ok.txt',
        ]
        buf = io.StringIO()
        mod = 'pre_commit_hooks.check_prohibited_filenames'
        saved = sys.modules.pop(mod, None)
        try:
            with redirect_stdout(buf), unittest.mock.patch.object(sys, 'argv', argv):
                with self.assertRaises(SystemExit) as ctx:
                    runpy.run_module(mod, run_name='__main__')
        finally:
            if saved is not None:
                sys.modules[mod] = saved
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(buf.getvalue().strip(), '')
