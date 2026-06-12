# Reproduction bundle -- DR-2 lattice-class additive-energy theorem: T7 confirmed (standard NT import)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260612T083624Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `DR2-Lattice-T7-NTstandard-260612`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B5-BEYOND-LAYER-BOUND/DR-2/notes/dr-2-referee-package-260610-260612-v1.5.tex.txt`
  (+ its `.pdf`)
- the Lemma NT in-bundle proof note (the pin; unramified case proved in full,
  ramified corner standard-cited + exhaustively machine-covered):
  `claims/B5-BEYOND-LAYER-BOUND/DR-2/notes/dr2-lemma-nt-inbundle-260612-v1.0.tex.txt`
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

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`f44a8b294df6f13d8059b3fc7d675366c399ada4b9594f340f15154593d559f9`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
