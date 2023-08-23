from __future__ import annotations

import argparse
import subprocess
import re
from typing import Sequence, List

from pre_commit_hooks.util import added_files


def get_lfs_patterns() -> List[str]:
    output = subprocess.check_output(["git", "lfs", "track"], encoding='utf-8').strip()
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
    if not enforce_all:
        filenames = set(filenames) & added_files()

    print(f"Checking {len(lfs_patterns)} LFS patterns against {len(filenames)} files.")
    for filename in filenames:
        for pattern in lfs_patterns:
            if re.match(pattern, filename) and not check_file_in_lfs(filename):
                print(f"File '{filename}' matches pattern '{pattern}' but is not tracked by LFS.")
                retv = 1
                break

    return retv


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='Filenames pre-commit believes are changed.',
    )
    parser.add_argument(
        '--enforce-all', action='store_true',
        help='Enforce all files are checked, not just staged files.',
    )

    args = parser.parse_args(argv)

    return check_files_against_lfs_patterns(
        args.filenames,
        enforce_all=args.enforce_all
    )


if __name__ == '__main__':
    raise SystemExit(main())
