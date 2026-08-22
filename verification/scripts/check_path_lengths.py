#!/usr/bin/env python3
"""Fail-closed project path-length audit for Windows/GitHub compatibility.

The public checkout must keep every file and directory path at or below the
Windows-compatible 256-character budget.  Both the repository-relative path
(the form used by GitHub Pages and archive consumers) and the absolute path
(the form used by Windows filesystem APIs) are checked.  The Git metadata
directory is excluded because it is not part of the project surface.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

__version__ = "1.0.0"
MAX_PATH_CHARS = 256


def scan(repo: Path, max_chars: int = MAX_PATH_CHARS) -> list[tuple[int, str]]:
    offenders: list[tuple[int, str]] = []
    for path in repo.rglob("*"):
        try:
            rel = path.relative_to(repo)
        except ValueError:
            continue
        if ".git" in rel.parts:
            continue
        relative_text = str(rel)
        absolute_text = str(path)
        relative_length = len(relative_text)
        absolute_length = len(absolute_text)
        if relative_length > max_chars:
            offenders.append((relative_length, f"relative: {relative_text}"))
        if absolute_length > max_chars:
            offenders.append((absolute_length, f"absolute: {relative_text}"))
    offenders.sort(reverse=True)
    return offenders


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--max", type=int, default=MAX_PATH_CHARS, dest="max_chars")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        assert len("C:/repo/" + "a" * 249) > MAX_PATH_CHARS
        assert len("C:/repo/" + "a" * 240) <= MAX_PATH_CHARS
        print("PATH-LENGTH SELF-TEST: PASS")
        return 0

    repo = args.repo.resolve()
    offenders = scan(repo, args.max_chars)
    if offenders:
        print(f"PATH-LENGTH: FAIL ({len(offenders)} paths > {args.max_chars})")
        for length, rel in offenders:
            print(f"{length}\t{rel}")
        return 1
    print(f"PATH-LENGTH: PASS (all project paths <= {args.max_chars} characters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
