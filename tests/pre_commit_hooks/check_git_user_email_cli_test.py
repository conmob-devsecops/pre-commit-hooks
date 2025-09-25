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
import os
import sys
import shutil
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class CheckGitUserEmailCLITests(unittest.TestCase):
    @unittest.skipIf(shutil.which('git') is None, 'git not available')
    def test_cli_exits_0_when_domain_allowed(self):
        # repo root (one level above 'tests')
        project_root = Path(__file__).resolve().parents[2]
        with TemporaryDirectory() as tmp:
            subprocess.run(
                ['git', 'init'], cwd=tmp, check=True, stdout=subprocess.DEVNULL
            )
            subprocess.run(
                ['git', 'config', 'user.email', 'dev@corp.example'], cwd=tmp, check=True
            )

            env = os.environ.copy()
            env['PYTHONPATH'] = f"{project_root}{os.pathsep}{env.get('PYTHONPATH','')}"

            cp = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'pre_commit_hooks.check_git_user_email',
                    '--allowed-domains',
                    'corp.example',
                    'other.com',
                ],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(
                cp.returncode, 0, msg=f"stdout:\n{cp.stdout}\nstderr:\n{cp.stderr}"
            )

    @unittest.skipIf(shutil.which('git') is None, 'git not available')
    def test_cli_exits_1_and_prints_message_when_domain_disallowed(self):
        project_root = Path(__file__).resolve().parents[2]
        with TemporaryDirectory() as tmp:
            subprocess.run(
                ['git', 'init'], cwd=tmp, check=True, stdout=subprocess.DEVNULL
            )
            subprocess.run(
                ['git', 'config', 'user.email', 'dev@bad.example'], cwd=tmp, check=True
            )

            env = os.environ.copy()
            env['PYTHONPATH'] = f"{project_root}{os.pathsep}{env.get('PYTHONPATH','')}"

            cp = subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'pre_commit_hooks.check_git_user_email',
                    '--allowed-domains',
                    'corp.example',
                ],
                cwd=tmp,
                env=env,
                text=True,
                capture_output=True,
            )

            self.assertEqual(cp.returncode, 1)
            self.assertIn('Git user email does not match allowed domains', cp.stdout)
            self.assertIn('corp.example', cp.stdout)
