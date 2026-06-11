# Reproduction bundle -- Reading-H C_full vacuum selection (T7-SCOPE)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260611T030445Z with Python 3.10.12, numpy 2.2.6.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B1-RH-ENUM/Reading-H/notes/reading-h-cfull-referee-package-260610-v1.1.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/res5_032_window_certification.py
  python codes/vacuum/res5_033_ext_adversarial_map.py
  python codes/vacuum/res5_034_DS_nonlattice_extension.py
  python codes/vacuum/res5_035_cfull_scope_enactment.py
  python codes/vacuum/res5_036_coherence_offdiag_bound.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  res5_032_window_certification: exit 0, `claims 6/6 PASS`
  res5_033_ext_adversarial_map: exit 0, `claims 5/5 PASS`
  res5_034_DS_nonlattice_extension: exit 0, `claims 6/6 PASS`
  res5_035_cfull_scope_enactment: exit 0, `claims 5/5 PASS`
  res5_036_coherence_offdiag_bound: exit 0, `claims 5/5 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`8bf65213e36fa6aca2104bd127002b47798ee1688fc7b7df7ed03e3d6b0c27b3`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
