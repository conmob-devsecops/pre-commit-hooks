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
from __future__ import annotations

import argparse
from collections.abc import Sequence

from pre_commit_hooks.util import cmd_output


def _get_git_user_email_local() -> str:
    """Get the local Git user email."""
    try:
        return cmd_output('git', 'config', 'user.email').strip()
    except Exception as e:
        raise RuntimeError('Error: Could not get local Git user email') from e


def _get_email_domain(email: str) -> str:
    """Extract the domain from an email address."""
    parts = email.split('@')
    if len(parts) < 2:
        raise ValueError(f"Invalid email address: {email}")
    return parts[-1]


def _domain_in_allowed(email_domain: str, allowed_domains: list[str]) -> bool:
    """Check if the email domain is in the list of allowed domains."""
    email_domain_lower = email_domain.lower()
    allowed_domains_lower = [domain.lower() for domain in allowed_domains]
    return email_domain_lower in allowed_domains_lower


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--allowed-domains',
        nargs='+',
        default=[],
        help='List of allowed email domains',
    )
    args = parser.parse_args(argv)

    local_email = _get_git_user_email_local()
    local_email_domain = _get_email_domain(local_email)

    if _domain_in_allowed(local_email_domain, args.allowed_domains):
        return 0

    print(
        f"""
    Git user email does not match allowed domains,
    please set it using 'git config user.email <email>'
    or globally by 'git config --global user.email <email>'

    Domains allowed: {args.allowed_domains}
    """
    )
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
