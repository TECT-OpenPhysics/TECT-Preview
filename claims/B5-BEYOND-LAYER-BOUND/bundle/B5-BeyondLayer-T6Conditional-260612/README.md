# Reproduction bundle -- B5 beyond-layer bound: T6 PROVED-CONDITIONAL on H_B5^T6 (T-031 enactment)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260612T162946Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `B5-BeyondLayer-T6Conditional-260612`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B5-BEYOND-LAYER-BOUND/T5-DOSSIER/notes/t6-conditional-assignment-260612-v1.0.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/dr2_circle_richness.py
  python codes/vacuum/dr2_divcirc_proof.py
  python codes/vacuum/dr2_lattice_divisor.py
  python codes/vacuum/dr2_cross_energy_lemma.py
  python codes/vacuum/dr2_weighted_energy.py
  python codes/vacuum/dr2_decoupling_iteration.py
  python codes/vacuum/dr2_decoupling_exponent.py
  python codes/vacuum/dr2_lemma_nt_exhaustive.py
  python codes/vacuum/beyond_layer_gershgorin_bound.py
  python codes/vacuum/scscope_ghat4_pertransfer.py
  python codes/vacuum/scscope_floor_sharpening.py
  python codes/vacuum/scscope_mendpoint_eval.py
  python codes/vacuum/scscope_quartic_certificate.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  dr2_circle_richness: exit 0, `claims 5/5 PASS`
  dr2_divcirc_proof: exit 0, `claims 4/4 PASS`
  dr2_lattice_divisor: exit 0, `claims 7/7 PASS`
  dr2_cross_energy_lemma: exit 0, `claims 6/6 PASS`
  dr2_weighted_energy: exit 0, `claims 3/3 PASS`
  dr2_decoupling_iteration: exit 0, `claims 4/4 PASS`
  dr2_decoupling_exponent: exit 0, `claims 4/4 PASS`
  dr2_lemma_nt_exhaustive: exit 0, `claims 5/5 PASS`
  beyond_layer_gershgorin_bound: exit 0, `claims 192/192 PASS`
  scscope_ghat4_pertransfer: exit 0, `claims 7/7 PASS`
  scscope_floor_sharpening: exit 0, `claims 5/5 PASS`
  scscope_mendpoint_eval: exit 0, `claims 12/12 PASS`
  scscope_quartic_certificate: exit 0, `claims 5/5 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`b0a3472bf6a4f318a6a8ccc4d8d753733561c97ca87761c6618bbf7dddbbfb1b`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
