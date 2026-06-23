# Reproduction bundle -- A3: renormalisation foundation (UV + spectral continuum limit)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260623T092144Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `A3-Renormalisation-Foundation-260623`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/A3-UV-SUPERRENORMALISABILITY/notes/a3-consolidation-260623-260623-v1.1.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/foundations/a3_renormalisation_checks.py
  python codes/foundations/a3_graphwise_convergence_checks.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a3_renormalisation_checks: exit 0, `A3 renormalisation checks: 6/6 PASS`
  a3_graphwise_convergence_checks: exit 0, `A3 graphwise-convergence (Route A spectral regulator; lattice folding flaw recorded) checks: 8/8 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`d4c49a3ad6e4201ea71e7b2fb05ccae007628fe8e0fee69b61f714410969f087`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
