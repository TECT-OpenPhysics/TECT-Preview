# Reproduction bundle -- A1 N-001 production-kernel manifest scoped T5

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260716T102649Z with Python 3.12.13, numpy 2.3.5.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `b-a1n`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/a1k/notes/a1-production-kernel-manifest-260623-260716-v1.7.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/foundations/a1_kernel_checks.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a1_kernel_checks: exit 0, `A1 kernel checks v1.7.0: 14/14 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`99b255e767b5c1a6ea12983399f46ae5f23f5d3d76e4d587d3350c5c5ed62f7e`
The repository commit that produced this bundle is recorded in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's scope, devil's-advocate, falsifier, and no-overclaim statement.
The bundle does not enlarge the claim beyond that pinned scope.
