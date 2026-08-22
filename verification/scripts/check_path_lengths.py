#!/usr/bin/env python3
"""Fail-closed repository-relative path-length audit.

The publication surface must keep every repository-relative path at or below
the Windows-compatible 256-character budget. An absolute-path check is
available only when the caller supplies ``--absolute-root``: CI checkout roots
are environment-specific, and GitHub's Linux runner does not apply Windows
MAX_PATH to its absolute workspace prefix.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

__version__ = "1.1.0"
__first_issued__ = "2026-08-22"
__version_issued__ = "2026-08-22"
MAX_PATH_CHARS = 256


def scan(
    repo: Path,
    max_chars: int = MAX_PATH_CHARS,
    absolute_root: Path | None = None,
) -> list[tuple[int, str]]:
    """Return repository-relative offenders and optional deployment-root offenders."""
    offenders: list[tuple[int, str]] = []
    repo = repo.resolve()
    root = absolute_root.resolve() if absolute_root is not None else None
    for path in repo.rglob("*"):
        try:
            rel = path.relative_to(repo)
        except ValueError:
            continue
        if ".git" in rel.parts:
            continue
        relative_text = rel.as_posix()
        if len(relative_text) > max_chars:
            offenders.append((len(relative_text), f"relative: {relative_text}"))
        if root is not None:
            absolute_text = str(root / rel)
            if len(absolute_text) > max_chars:
                offenders.append((len(absolute_text), f"absolute: {relative_text}"))
    offenders.sort(reverse=True)
    return offenders


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--max", type=int, default=MAX_PATH_CHARS, dest="max_chars")
    parser.add_argument(
        "--absolute-root",
        type=Path,
        default=None,
        help="optional deployment root for an environment-specific absolute-path audit",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        assert len("C:/repo/" + "a" * 249) > MAX_PATH_CHARS
        assert len("C:/repo/" + "a" * 240) <= MAX_PATH_CHARS
        assert not scan(Path("C:/repo"), absolute_root=None)
        print("PATH-LENGTH SELF-TEST: PASS")
        return 0

    repo = args.repo.resolve()
    offenders = scan(repo, args.max_chars, args.absolute_root)
    if offenders:
        print(f"PATH-LENGTH: FAIL ({len(offenders)} paths > {args.max_chars} characters)")
        for length, rel in offenders:
            print(f"{length}\t{rel}")
        return 1
    if args.absolute_root is None:
        print(f"PATH-LENGTH: PASS (all repository-relative paths <= {args.max_chars} characters)")
    else:
        print(f"PATH-LENGTH: PASS (repository-relative and supplied absolute-root paths <= {args.max_chars} characters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
