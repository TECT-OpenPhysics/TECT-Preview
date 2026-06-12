# Reproduction bundle -- SC-SCOPE: second- and third-cumulant endpoint closure of the selection floor

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260612T064215Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `SC-SCOPE-T5-260612`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B5-BEYOND-LAYER-BOUND/SC-SCOPE/notes/sc-scope-referee-package-260610-260612-v1.4.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/scscope_ghat4_pertransfer.py
  python codes/vacuum/scscope_floor_sharpening.py
  python codes/vacuum/scscope_mendpoint_eval.py
  python codes/vacuum/scscope_quartic_certificate.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  scscope_ghat4_pertransfer: exit 0, `claims 7/7 PASS`
  scscope_floor_sharpening: exit 0, `claims 5/5 PASS`
  scscope_mendpoint_eval: exit 0, `claims 12/12 PASS`
  scscope_quartic_certificate: exit 0, `claims 5/5 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`bca6ca0cd6005ce4c97511fa7980207ef0cc75dce5c511bfd9ea02f4a7592bee`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
