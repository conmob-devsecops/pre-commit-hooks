from __future__ import annotations

import argparse
from collections.abc import Sequence
from pre_commit_hooks.util import cmd_output


def get_git_user_email_local() -> str:
    """Get the local Git user email."""
    try:
        return cmd_output("git", "config", "user.email").strip()
    except Exception as e:
        raise RuntimeError("Error: Could not get local Git user email") from e


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allowed-domains",
        nargs="+",
        required=True,
        help="List of allowed email domains",
    )
    args = parser.parse_args(argv)

    local_email = get_git_user_email_local()
    splits = local_email.split("@")
    used_domain = splits[-1]

    if used_domain in args.allowed_domains:
        return 0

    raise RuntimeError(
        f"""
    Git user email does not match allowed domains,
    please set it using 'git config user.email <email>'
    or globally by 'git config --global user.email <email>'

    Domains allowed: {args.allowed_domains}
    """
    )


if __name__ == "__main__":
    raise SystemExit(main())
