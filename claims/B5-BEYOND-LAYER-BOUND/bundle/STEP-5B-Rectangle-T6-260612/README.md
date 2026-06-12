# Reproduction bundle -- STEP-5B rectangle-constant closure: theorem-grade rectangle prefactor

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260612T045435Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `STEP-5B-Rectangle-T6-260612`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B5-BEYOND-LAYER-BOUND/STEP-5B/notes/step-5b-referee-package-260610-260612-v1.2.tex.txt`
  (+ its `.pdf`)
- the provenance theorem note (operator verdicts #9/#10 archive, imported by the
  referee note): `claims/B5-BEYOND-LAYER-BOUND/STEP-5B/notes/rectangle-constant-closure-260605-260605-v1.3.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/beyond_layer_gershgorin_bound.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  beyond_layer_gershgorin_bound: exit 0, `claims 192/192 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`f60864c6ad928d89ef6da16bb944b6fb7544005d0fcf99851e5507ec62e3740b`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
