from __future__ import annotations

import argparse
from collections.abc import Sequence
from util import cmd_output


def get_git_user_email_global() -> str:
    """Get the global Git user email."""
    try:
        return cmd_output('git', 'config', '--global', 'user.email').strip()
    except Exception as e:
        raise RuntimeError('Error: Could not get global Git user email') from e


def get_git_user_email_local() -> str:
    """Get the local Git user email."""
    try:
        return cmd_output('git', 'config', 'user.email').strip()
    except Exception as e:
        raise RuntimeError('Error: Could not get local Git user email') from e


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--allowed-domains',
        nargs='+',
        required=True,
        help='List of allowed email domains',
    )
    args = parser.parse_args(argv)

    for domain in args.allowed_domains:
        global_email = get_git_user_email_global()
        local_email = get_git_user_email_local()

        if global_email.endswith(domain) or local_email.endswith(domain):
            return 0

    raise RuntimeError(
        """
    Git user email does not match allowed domains,
    please set it using 'git config user.email <email>'
    or globally by 'git config --global user.email <email>'
    """
    )


if __name__ == '__main__':
    raise SystemExit(main())
