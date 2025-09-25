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
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#
#
#
import io
import os
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pre_commit_hooks.check_prohibited_filenames as lib


class ProhibitedFilenamesExtraUnitTests(unittest.TestCase):
    def test_normalize_pattern_replaces_backslashes(self):
        self.assertEqual(lib._normalize_pattern(r'a\b\c.txt'), 'a/b/c.txt')

    def test_has_glob_meta_true_and_false(self):
        self.assertTrue(lib._has_glob_meta('*a[bc]?'))
        self.assertFalse(lib._has_glob_meta('plain.txt'))

    def test_norm_path_wrapper(self):
        s = 'a/../b//c'
        self.assertEqual(lib._norm_path(s), os.path.normpath(s))

    def test_path_wrapper_returns_path(self):
        s = 'x/y/z.txt'
        p = lib._path(s)
        self.assertIsInstance(p, Path)
        self.assertEqual(str(p), os.path.normpath(s))

    def test_match_filename_windows_case_insensitive(self):
        # Simulate Windows behavior: case-insensitive basename comparison.
        with patch.object(lib.os, 'name', 'nt'):
            self.assertTrue(lib._match_filename('dir/ReadMe.md', ['README.md']))
            self.assertTrue(lib._match_filename('README.md', ['dir/readme.MD']))
            self.assertFalse(lib._match_filename('notes.md', ['README.md']))

    def test_matches_patterns_component_scan_including_root_part(self):
        # Absolute path includes a root part that should be skipped in component scan.
        abs_path = os.path.join(os.sep, 'var', 'whoopie', 'z.txt')
        self.assertTrue(lib._matches_patterns(abs_path, ['*whoop*']))
        self.assertFalse(lib._matches_patterns(abs_path, ['*nope*']))

    def test_matches_patterns_with_backslash_separators(self):
        # Pattern contains backslashes; normalization should make it match.
        path = 'dir/sub/file.txt'
        pat = r'dir\sub\file.txt'
        self.assertTrue(lib._matches_patterns(path, [pat]))

    def test_matches_patterns_basename_and_fullpath(self):
        self.assertTrue(lib._matches_patterns('a/b/file.txt', ['*.txt']))
        self.assertFalse(lib._matches_patterns('a/b/file.txt', ['*.md']))
        self.assertTrue(lib._matches_patterns('keys/id_rsa.pem', ['**/keys/*.pem']))
        self.assertFalse(lib._matches_patterns('keys/id_rsa.pem', ['**/secrets/*.pem']))

    def test_find_prohibited_reports_duplicates_when_both_conditions_match(self):
        # Filename matches exact list and also matches pattern -> appears twice.
        filenames = ['docs/README.md']
        prohibited_filenames = ['README.md']
        prohibited_patterns = ['*.md']
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lib.find_prohibited(
                prohibited_filenames, prohibited_patterns, filenames
            )
        out = buf.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn('Prohibited filename(s) found:', out)
        self.assertEqual(out.count('docs/README.md'), 2)

    def test_find_prohibited_no_lists_returns_0(self):
        rc = lib.find_prohibited([], [], ['ok.txt', 'more/ok.py'])
        self.assertEqual(rc, 0)

    def test_comma_action_none_and_string_and_list(self):
        # Directly exercise CommaSeparatedList branches.
        action = lib.CommaSeparatedList(option_strings=['--vals'], dest='vals')
        ns = argparse.Namespace()

        # values=None branch
        action(None, ns, None, option_string=None)
        self.assertEqual(ns.vals, [])

        # values is string branch
        action(None, ns, ' a , b ,, c ', option_string='--vals')
        self.assertEqual(ns.vals, ['a', 'b', 'c'])

        # values is list branch (nargs="*" style)
        action(None, ns, ['d,e', ' f ', ' , ', 'g'], option_string='--vals')
        self.assertEqual(ns.vals, ['d', 'e', 'f', 'g'])


# Local import to avoid test discovery ordering issues
import argparse  # noqa: E402
