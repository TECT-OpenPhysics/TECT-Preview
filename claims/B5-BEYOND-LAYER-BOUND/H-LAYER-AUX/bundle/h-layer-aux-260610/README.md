# Reproduction bundle -- B5-BEYOND-LAYER-BOUND / H-LAYER-AUX

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260611T032055Z with Python 3.10.12, numpy 2.2.6.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B5-BEYOND-LAYER-BOUND/H-LAYER-AUX/notes/hlayer-res4-intensity-closure-260609-260609-v1.1.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/beyond_layer_gershgorin_bound.py
  python codes/vacuum/hlayer_res4_intensity_sweep.py
  python codes/vacuum/res5_024_offshell_operator_decision.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  beyond_layer_gershgorin_bound: exit 0, `claims 192/192 PASS`
  hlayer_res4_intensity_sweep: exit 0, `claims 6/6 PASS`
  res5_024_offshell_operator_decision: exit 0, `claims 5/5 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`3e8c88b521ad016fb23b29d75a0d1d71653951a219f2a7b5032b56083207e5f9`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
