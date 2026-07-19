# Reproduction bundle -- A4 finite-volume scalar spectral constructive Gibbs measure

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260719T044125Z with Python 3.12.10, numpy 1.26.4,
and torch 2.11.0+cpu.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `A4-Scalar-Constructive-T6-260719`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE/notes/a4-scalar-constructive-referee-package-260719-v2.1.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # dependencies discovered from entry scripts
  python codes/foundations/a4_scalar_constructive_measure.py
  python codes/foundations/a4_scalar_constructive_measure_independent.py
  python codes/foundations/a4_scalar_constructive_measure_verify.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a4_scalar_constructive_measure: exit 0, `A4-SCALAR-CONSTRUCTIVE-PRIMARY-PASS`
  a4_scalar_constructive_measure_independent: exit 0, `A4-SCALAR-CONSTRUCTIVE-INDEPENDENT-PASS`
  a4_scalar_constructive_measure_verify: exit 0, `A4-SCALAR-CONSTRUCTIVE-INTEGRATED-PASS`

## Integrity
`MANIFEST.json` hashes every bundle file except itself and records the
content-addressable bundle digest plus the repository commit.

## Scope / how to attack
See the note's scope, devil's-advocate, falsifier, and no-overclaim statement.
The bundle does not enlarge the claim beyond that pinned scope.
