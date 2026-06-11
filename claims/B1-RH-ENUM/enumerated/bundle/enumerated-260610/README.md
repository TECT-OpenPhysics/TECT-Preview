# Reproduction bundle -- B1-RH-ENUM / enumerated

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260611T031937Z with Python 3.10.12, numpy 2.2.6.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B1-RH-ENUM/enumerated/notes/enumerated-readings-migration-revalidation-260605-260605-v1.1.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/t6_mainline_useries_checks.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  t6_mainline_useries_checks: exit 0, `claims 57/57 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`bcb0af5f1911f28d0d116bb299aaa413d0852a9c5bf9e97716886c73435e1e88`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
