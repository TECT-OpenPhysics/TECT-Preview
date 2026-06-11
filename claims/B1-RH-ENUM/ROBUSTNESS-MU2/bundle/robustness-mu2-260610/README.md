# Reproduction bundle -- B1-RH-ENUM / ROBUSTNESS-MU2

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260611T031957Z with Python 3.10.12, numpy 2.2.6.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B1-RH-ENUM/ROBUSTNESS-MU2/notes/robustness-mu2-step5b-remargin-260606-260606-v1.3.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/robustness_mu2_margin_recompute.py
  python codes/vacuum/robustness_mu2_sweep.py
  python codes/vacuum/robustness_mu2_step5b_remargin.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  robustness_mu2_margin_recompute: exit 0, `claims 9/9 PASS`
  robustness_mu2_sweep: exit 0, `claims 9/9 PASS`
  robustness_mu2_step5b_remargin: exit 0, `claims 5/5 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`a1fb4d421bd19b3e211ca8b15537315cb247b5f5d2a6a4c7bda439bb797e7a5e`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
