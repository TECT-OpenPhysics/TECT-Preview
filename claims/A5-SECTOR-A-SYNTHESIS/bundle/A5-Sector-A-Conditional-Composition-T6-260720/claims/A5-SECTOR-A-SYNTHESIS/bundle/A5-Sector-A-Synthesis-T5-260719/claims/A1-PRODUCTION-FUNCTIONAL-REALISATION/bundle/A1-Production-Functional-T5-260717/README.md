# Reproduction bundle -- A1 standalone production-functional discrete variational matrix

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260716T180315Z with Python 3.12.10, numpy 1.26.4,
and torch 2.11.0+cpu.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `A1-Production-Functional-T5-260717`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/notes/a1-production-functional-realisation-260717-v1.3.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # dependencies discovered from entry scripts
  python codes/foundations/a1_production_backend_verify.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a1_production_backend_verify: exit 0, `P1 production backend: PRODUCTION-BACKEND-MULTIGRID-PASS`

## Integrity
`MANIFEST.json` hashes every bundle file except itself and records the
content-addressable bundle digest plus the repository commit.

## Scope / how to attack
See the note's scope, devil's-advocate, falsifier, and no-overclaim statement.
The bundle does not enlarge the claim beyond that pinned scope.
