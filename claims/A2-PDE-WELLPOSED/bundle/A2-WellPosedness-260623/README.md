# Reproduction bundle -- a2-consolidation-260623-260623-v1.1.tex

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260623T092346Z with Python 3.12.10, numpy 1.26.4.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `A2-WellPosedness-260623`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/A2-PDE-WELLPOSED/notes/a2-consolidation-260623-260623-v1.1.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes\foundations\a2_wellposedness_checks.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a2_wellposedness_checks: exit 0, `A2 well-posedness checks: 8/8 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`7310e0b74520bf3b1b6b14f5aee46e90e682ed514e30399df456b602037bec4c`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
