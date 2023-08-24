from __future__ import annotations

import argparse
import subprocess
import re
from fnmatch import fnmatch
from typing import Sequence, List

from pre_commit_hooks.util import added_files, cmd_output


def get_lfs_patterns() -> List[str]:
    output = cmd_output("git", "lfs", "track").strip()
    # Extract patterns based on the provided format
    return re.findall(r'^\s*(\*\.[A-Za-z0-9]+)', output, re.MULTILINE)


def check_file_in_lfs(filename: str) -> bool:
    try:
        output = subprocess.check_output(
            ["git", "lfs", "ls-files"],
            encoding='utf-8'
        ).strip()
        return filename in output
    except subprocess.CalledProcessError:
        return False


def check_files_against_lfs_patterns(
        filenames: Sequence[str],
        *,
        enforce_all: bool = False
) -> int:
    retv = 0
    lfs_patterns = get_lfs_patterns()
    if enforce_all:
        print("Enforcing all files are checked.")
        filenames = set(cmd_output('git', 'ls-files').splitlines())
    print(f"enforce_all: {enforce_all}")
    print(f"Checking {len(lfs_patterns)} LFS patterns against {len(filenames)} files.")
    print(f"Patterns: {lfs_patterns}")
    for filename in filenames:
        for pattern in lfs_patterns:
            if fnmatch(pattern, filename) and not check_file_in_lfs(filename):
                print(f"File '{filename}' matches pattern '{pattern}' but is not tracked by LFS.")
                retv = 1
    return retv


def main(argv: Sequence[str] | None = None) -> int:
    print(f"Running {__file__} with argv: {argv}")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='Filenames pre-commit believes are changed.',
    )
    parser.add_argument(
        '--all-files', action='store_true',
        help='Enforce all files are checked, not just staged files.',
    )

    args = parser.parse_args(argv)

    return check_files_against_lfs_patterns(
        args.filenames,
        enforce_all=args.all_files
    )


if __name__ == '__main__':
    raise SystemExit(main())
