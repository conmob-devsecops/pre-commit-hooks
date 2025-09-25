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
import contextlib
import io
import unittest
from unittest.mock import patch

import pre_commit_hooks.check_git_user_email as lib


class CheckGitUserEmailTests(unittest.TestCase):
    @patch(
        'pre_commit_hooks.check_git_user_email.cmd_output',
        return_value='  jane.doe@example.net \n',
    )
    def test_get_git_user_email_local_success_strips_and_calls_git(self, cmd):
        email = lib._get_git_user_email_local()
        self.assertEqual(email, 'jane.doe@example.net')
        cmd.assert_called_once_with('git', 'config', 'user.email')

    @patch(
        'pre_commit_hooks.check_git_user_email.cmd_output',
        side_effect=Exception('boom'),
    )
    def test_get_git_user_email_local_wraps_exception(self, cmd):
        with self.assertRaises(RuntimeError) as ctx:
            lib._get_git_user_email_local()
        self.assertIn('Could not get local Git user email', str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, Exception)

    def test_get_email_domain_basic(self):
        self.assertEqual(lib._get_email_domain('user@example.com'), 'example.com')

    def test_get_email_domain_with_plus_and_subdomain(self):
        self.assertEqual(
            lib._get_email_domain('dev+ci@sub.corp.example'), 'sub.corp.example'
        )

    def test_get_email_domain_raises_on_invalid(self):
        with self.assertRaises(ValueError):
            lib._get_email_domain('invalid-email')

    def test_domain_in_allowed_true(self):
        self.assertTrue(
            lib._domain_in_allowed('corp.example', ['corp.example', 'other.com'])
        )

    def test_domain_in_allowed_false(self):
        self.assertFalse(
            lib._domain_in_allowed('bad.example', ['corp.example', 'other.com'])
        )

    def test_deny_empty_allowed_domains(self):
        self.assertFalse(lib._domain_in_allowed('any.example', []))

    def test_deny_empty_user_email(self):
        self.assertFalse(lib._domain_in_allowed('', ['any.example']))

    @patch(
        'pre_commit_hooks.check_git_user_email._get_git_user_email_local',
        return_value='dev@corp.example',
    )
    def test_main_returns_0_when_domain_allowed(self, _get_email):
        rc = lib.main(['--allowed-domains', 'corp.example', 'other.com'])
        self.assertEqual(rc, 0)

    @patch(
        'pre_commit_hooks.check_git_user_email._get_git_user_email_local',
        return_value='dev@bad.example',
    )
    def test_main_returns_1_and_prints_message_when_domain_disallowed(self, _get_email):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = lib.main(['--allowed-domains', 'corp.example'])
        self.assertEqual(rc, 1)
        out = buf.getvalue()
        self.assertIn('Git user email does not match allowed domains', out)
        self.assertIn('corp.example', out)
