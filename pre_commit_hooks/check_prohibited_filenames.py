from __future__ import annotations

import argparse
import fnmatch
import os
import re
from collections.abc import Sequence


def _matches_patterns(path: str, patterns: Sequence[str]) -> bool:
    base = os.path.basename(path)
    return any(
        fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(base, pat) for pat in patterns
    )


def _matches_regexes(path: str, regexes: Sequence[re.Pattern[str]]) -> bool:
    base = os.path.basename(path)
    return any(rx.search(path) or rx.search(base) for rx in regexes)


def find_prohibited(
    prohibited_filenames: set[str],
    prohibited_patterns: Sequence[str],
    prohibited_regexes: Sequence[re.Pattern[str]],
    filenames: Sequence[str],
) -> int:
    for fn in filenames:
        if fn in prohibited_filenames:
            print(f"Prohibited filename found: {fn}")
            return 1
        if prohibited_patterns and _matches_patterns(fn, prohibited_patterns):
            print(f"Prohibited filename found: {fn}")
            return 1
        if prohibited_regexes and _matches_regexes(fn, prohibited_regexes):
            print(f"Prohibited filename found: {fn}")
            return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--prohibited-filenames',
        nargs='+',
        default=[],
        help='Exact filenames to prohibit',
    )
    parser.add_argument(
        '--prohibited-patterns',
        nargs='*',
        default=[],
        help='Shell-style patterns to prohibit (e.g., `*.pem`, `docs/*/README.md`)',
    )
    parser.add_argument(
        '--prohibited-regex',
        nargs='*',
        default=[],
        help='Python regex patterns to prohibit',
    )
    parser.add_argument(
        'filenames',
        nargs='*',
        help='Filenames to check against the prohibited list',
    )
    args = parser.parse_args(argv)

    try:
        regexes = [re.compile(pat) for pat in args.prohibited_regex]
    except re.error as exc:
        raise RuntimeError('Error: Invalid regex pattern') from exc

    prohibited_filenames = set(args.prohibited_filenames)

    return find_prohibited(
        prohibited_filenames,
        args.prohibited_patterns,
        regexes,
        args.filenames,
    )


if __name__ == '__main__':
    raise SystemExit(main())
