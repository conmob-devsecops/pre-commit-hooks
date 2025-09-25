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
import fnmatch
import os
from collections.abc import Sequence
from pathlib import PurePosixPath, Path


class CommaSeparatedList(argparse.Action):
    """
    Parse comma-separated lists and merge multiple occurrences.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, [])
        elif isinstance(values, list):
            result = []
            for v in values:
                result.extend([item.strip() for item in v.split(',') if item.strip()])
            setattr(namespace, self.dest, result)
        else:
            result = [item.strip() for item in values.split(',') if item.strip()]
            setattr(namespace, self.dest, result)


def _norm_path(s: str) -> str:
    """Wrapper around os.path.normpath to normalize path separators."""
    return os.path.normpath(s)


def _path(s: str) -> Path:
    """Wrapper around Path to normalize path separators."""
    return Path(_norm_path(s))


def _has_glob_meta(pat: str) -> bool:
    """Check if the pattern contains any glob meta characters."""
    return any(ch in pat for ch in '*?[')


def _normalize_pattern(pat: str) -> str:
    """
    Normalize a pattern to use forward slashes.

    On Windows, `Path.match` requires forward slashes in the pattern.
    On other platforms, it doesn't matter, but we normalize anyway for consistency.
    """
    return pat.replace('\\', '/')


def _to_posix_path(s: str) -> str:
    """Convert a path string to a POSIX-style path with forward slashes."""
    return _norm_path(s).replace('\\', '/')


def _match_filename(path_str: str, filenames: Sequence[str]) -> bool:
    """
    Check if the basename of `path_str` matches any of the given filenames.

    On Windows, the match is case-insensitive; on other platforms, it's case-sensitive.
    """
    base = os.path.basename(_norm_path(path_str))
    if os.name == 'nt':
        base_cf = base.casefold()
        return any(
            base_cf == os.path.basename(_norm_path(f)).casefold() for f in filenames
        )
    else:
        return any(base == os.path.basename(_norm_path(f)) for f in filenames)


def _matches_patterns(path: str, patterns: Sequence[str]) -> bool:
    """
    Check if `path` matches any of the given glob-style patterns.

    For patterns containing a separator, use `PurePosixPath.match` (supports `**`).
    Handle leading `**/` specially by also trying the pattern without it to
    allow zero-directory matches at the start (e.g., `**/keys/*.pem` should
    match `keys/file.pem`).
    """
    posix = _to_posix_path(path)
    basename = posix.rsplit('/', 1)[-1]
    parts = [p for p in posix.split('/') if p and p != '/']

    for pat in patterns:
        pat_norm = _normalize_pattern(pat)

        if '/' in pat_norm:
            candidates = [pat_norm]
            if pat_norm.startswith('**/'):
                candidates.append(pat_norm[3:])
            for cand in candidates:
                if PurePosixPath(posix).match(cand):
                    return True
            continue

        # No separator: basename and component scan
        if _has_glob_meta(pat_norm):
            if fnmatch.fnmatch(basename, pat_norm):
                return True
            if any(fnmatch.fnmatch(part, pat_norm) for part in parts):
                return True
        else:
            # Exact basename match (handles Windows case-insensitivity inside)
            if _match_filename(posix, [pat_norm]):
                return True

    return False


def find_prohibited(
    prohibited_filenames: Sequence[str],
    prohibited_patterns: Sequence[str],
    filenames: Sequence[str],
) -> int:
    """
    Check the given filenames against prohibited filenames and patterns.
    """
    found = []
    for fn in filenames:
        if prohibited_filenames and _match_filename(fn, prohibited_filenames):
            found.append(fn)
        if prohibited_patterns and _matches_patterns(fn, prohibited_patterns):
            found.append(fn)

    if found:
        print(f"Prohibited filename(s) found: {', '.join(found)}")
        return 1

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--prohibited-filenames',
        '--filenames',
        dest='prohibited_filenames',
        action=CommaSeparatedList,
        default=[],
        help='Exact filenames to prohibit',
    )
    parser.add_argument(
        '--prohibited-patterns',
        '--patterns',
        dest='prohibited_patterns',
        action=CommaSeparatedList,
        default=[],
        help='Glob-style patterns to prohibit (e.g., `*.pem`, `**/secrets/*`)',
    )
    parser.add_argument(
        'filenames',
        nargs='+',
        help='Filenames to check against the prohibited list',
    )
    args = parser.parse_args(argv)

    return find_prohibited(
        args.prohibited_filenames,
        args.prohibited_patterns,
        args.filenames,
    )


if __name__ == '__main__':
    raise SystemExit(main())
