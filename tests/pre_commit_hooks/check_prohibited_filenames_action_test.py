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
import unittest

import pre_commit_hooks.check_prohibited_filenames as lib


class CommaSeparatedListActionTests(unittest.TestCase):
    def test_values_none_sets_empty_list(self):
        action = lib.CommaSeparatedList(option_strings=['--vals'], dest='vals')
        ns = argparse.Namespace()
        action(None, ns, None, option_string='--vals')
        self.assertEqual(ns.vals, [])

    def test_values_string_splits_trims_and_ignores_empty(self):
        action = lib.CommaSeparatedList(option_strings=['--vals'], dest='vals')
        ns = argparse.Namespace()
        action(None, ns, ' a , b ,, c ', option_string='--vals')
        self.assertEqual(ns.vals, ['a', 'b', 'c'])

    def test_values_list_flattens_trims_and_ignores_empty(self):
        action = lib.CommaSeparatedList(option_strings=['--vals'], dest='vals')
        ns = argparse.Namespace()
        action(None, ns, ['d,e', ' f ', ' , ', ',', 'g'], option_string='--vals')
        self.assertEqual(ns.vals, ['d', 'e', 'f', 'g'])

    def test_argparse_integration_with_nargs_star(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--vals', action=lib.CommaSeparatedList, nargs='*')
        ns = parser.parse_args(['--vals', 'a,b', 'c', 'd,,', ' e , f '])
        self.assertEqual(ns.vals, ['a', 'b', 'c', 'd', 'e', 'f'])
