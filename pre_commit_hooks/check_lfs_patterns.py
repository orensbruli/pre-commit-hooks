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


def files_in_lfs() -> str:
    return cmd_output("git", "lfs", "ls-files").strip()

def pattern_list_to_regex(patterns: List[str]) -> str:
    # Convertir los patrones fnmatch a una expresión regular
    regex = '|'.join([re.escape(pattern).replace('\\*', '.*') for pattern in patterns])
    return re.compile(regex)


def check_files_against_lfs_patterns(
        filenames: Sequence[str],
        enforce_all: bool = False
) -> int:
    retv = 0
    lfs_patterns = get_lfs_patterns()
    if enforce_all:
        # print("Enforcing all files are checked.")
        filenames = set(cmd_output('git', 'ls-files').splitlines())
    patterns_regex = pattern_list_to_regex(lfs_patterns)
    tracked_lfs_files = files_in_lfs()
    non_tracked_lfs_files = []
    for filename in filenames:
        if patterns_regex.match(filename):
            if filename not in tracked_lfs_files:
                non_tracked_lfs_files.append(filename)
                retv = 1
    if retv:
        print(" ".join(lfs_patterns))
        print("Files matching these patterns must be tracked by LFS.")
        print("\t"+"\n\t".join(non_tracked_lfs_files))
        print("If these files already exist in the repository, you can convert them to LFS with:")
        print(f"  git lfs migrate import --include=\"{' '.join(non_tracked_lfs_files)}\" --no-rewrite")
        print("If these files are new, you should check that you have lfs configured correctly:")
        print("  git lfs install")
        print("If it's installed you can track files with:")
        print(f"  git reset {' '.join(non_tracked_lfs_files)}; git lfs track {' '.join(non_tracked_lfs_files)}")
        print("You can check which files are tracked by LFS with:")
        print("  git lfs ls-files")
    return retv


def main(argv: Sequence[str] | None = None) -> int:
    # print(f"Running {__file__} with argv: {argv}")
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames pre-commit believes are changed.')
    parser.add_argument('--all-files', action='store_true', help='Check all files in the repository.')
    args = parser.parse_args(argv)
    return check_files_against_lfs_patterns(
        args.filenames,
        enforce_all=args.all_files
    )


if __name__ == '__main__':
    raise SystemExit(main())
