# Reproduction bundle -- B1-RH-ENUM / near-gap

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260611T031942Z with Python 3.10.12, numpy 2.2.6.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B1-RH-ENUM/near-gap/notes/neargap-residual-closure-260606-v1.0.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/neargap_common_mode_repair.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  neargap_common_mode_repair: exit 0, `claims 14/14 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`0c708c9ac23592374b8b8f26599939707396d0f83912975be3af21fedcbe0566`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
