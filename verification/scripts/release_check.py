#!/usr/bin/env python3
"""release_check.py — pre-publication gate for the public GitHub surface.

Usage:
    python verification/scripts/release_check.py        # full gate, exit 0/1

Run before EVERY push to the public remote. Verifies that what is about to
become public satisfies the publication invariants
(governance/publication-tiers.md):

  1. claim ledger valid + CLAIMS.md / BY-CLAIM.md in sync (lint_claims)
  2. catalog in sync (build_catalog --check)
  3. P0 fence: `internal/` is gitignored and never referenced from P1/P2 text
  4. English-only policy: no Hangul in any publishable file
  5. no-overclaim phrase scan on claim/theory/publish surfaces
  6. P2 integrity: publish/ may only cite migration-clean claims
  7. file hygiene: NUL bytes, JSON parse, python AST, oversized files (>5 MB)

Changelog:
  1.0.0 (2026-06-05) first issue.
  1.0.1 (2026-06-05) P0 fence narrowed to file pointers; Hangul regex via escapes (self-match fix).
  1.0.2 (2026-06-05) skip git-ignored build/ area.
  1.0.3 (2026-06-05) english-only scan extended to .html/.js/.css (website shell).
"""
__version__ = "1.0.3"
__first_issued__ = "2026-06-05"
__version_issued__ = "2026-06-05"

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "internal", "__pycache__", ".pytest_cache", "build"}
FORBIDDEN = ["essentially proved", "almost closed", "at theorem level",
             "near closure", "conjecturally established"]
PHRASE_SCOPE = ("claims/", "theory/", "publish/", "README.md", "CLAIMS.md")
HANGUL = re.compile("[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]")
CLAIM_ID = re.compile(r"\b([A-F]\d+-[A-Z0-9-]{3,})\b")


def files():
    for f in sorted(REPO.rglob("*")):
        if f.is_file() and not any(p in SKIP_DIRS for p in f.parts):
            yield f


def run(label, cmd, errors):
    r = subprocess.run([sys.executable] + cmd, capture_output=True, text=True, cwd=REPO)
    print(f"  [{label}] {'PASS' if r.returncode == 0 else 'FAIL'}")
    if r.returncode != 0:
        errors.append(f"{label}: {r.stdout.strip()[:300]}")


def main():
    errors, warnings = [], []
    print("RELEASE-CHECK: pre-publication gate")

    # 1+2. generated surfaces in sync
    run("ledger", ["verification/scripts/lint_claims.py", "--render", "--check"], errors)
    run("catalog", ["verification/scripts/build_catalog.py", "--check"], errors)

    # 3. P0 fence
    gi = (REPO / ".gitignore").read_text(encoding="utf-8")
    if not re.search(r"^internal/$", gi, re.M):
        errors.append("P0 fence: 'internal/' missing from .gitignore")
    fence = re.compile(r"internal/[A-Za-z0-9_./-]*\.[A-Za-z0-9]+")
    for f in files():
        if f.suffix in (".md", ".json", ".py", ".yml") and f.name != "release_check.py":
            if fence.search(f.read_text(encoding="utf-8", errors="replace")):
                errors.append(f"P0 fence: {f.relative_to(REPO)} cites a FILE under internal/ "
                              "(folder mentions in policy prose are allowed)")
    print("  [p0-fence] done")

    # 4. English-only
    for f in files():
        if f.suffix in (".md", ".py", ".json", ".yml", ".txt", ".tex", ".html", ".js", ".css"):
            if HANGUL.search(f.read_text(encoding="utf-8", errors="replace")):
                errors.append(f"english-only: Hangul found in {f.relative_to(REPO)}")
    print("  [english-only] done")

    # 5. no-overclaim phrases (definition sites in governance/ are exempt)
    for f in files():
        rel = str(f.relative_to(REPO)).replace("\\", "/")
        if rel.startswith(PHRASE_SCOPE) and f.suffix == ".md":
            low = f.read_text(encoding="utf-8", errors="replace").lower()
            for ph in FORBIDDEN:
                if ph in low:
                    errors.append(f"no-overclaim: '{ph}' in {rel}")
    print("  [no-overclaim] done")

    # 6. P2 may only cite migration-clean claims
    cards = {}
    for d in (REPO / "claims").iterdir():
        sj = d / "status.json"
        if d.is_dir() and sj.exists():
            cards[d.name] = json.loads(sj.read_text(encoding="utf-8"))
    for f in (REPO / "publish").rglob("*.md"):
        text = f.read_text(encoding="utf-8", errors="replace")
        for cid in set(CLAIM_ID.findall(text)):
            c = cards.get(cid)
            if c and any(str(p).startswith("legacy:") for p in c["legacy_evidence"]):
                errors.append(f"P2: {f.relative_to(REPO)} cites {cid} which is not migration-clean")
    print("  [p2-clean-citation] done")

    # 7. hygiene
    for f in files():
        b = f.read_bytes()
        rel = f.relative_to(REPO)
        if b"\x00" in b and f.suffix in (".md", ".py", ".json", ".yml", ".txt"):
            errors.append(f"hygiene: NUL bytes in {rel}")
        if f.suffix == ".json":
            try:
                json.loads(b.decode("utf-8"))
            except Exception as e:
                errors.append(f"hygiene: JSON parse {rel}: {e}")
        if f.suffix == ".py" and "archive/legacy" not in str(rel):
            try:
                ast.parse(b.decode("utf-8"))
            except Exception as e:
                errors.append(f"hygiene: python parse {rel}: {e}")
        if len(b) > 5 * 1024 * 1024:
            warnings.append(f"large file (>5MB): {rel} ({len(b)//1024} KB)")
    print("  [hygiene] done")

    for w in warnings:
        print(f"  WARN {w}")
    if errors:
        print(f"RELEASE-CHECK: FAIL ({len(errors)} error(s))")
        for e in errors:
            print(f"  ERR {e}")
        return 1
    print("RELEASE-CHECK: PASS — safe to push the public surface")
    return 0


if __name__ == "__main__":
    sys.exit(main())
