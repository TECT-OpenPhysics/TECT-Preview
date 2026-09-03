# Reproduction bundle -- Full-production spectral Galerkin convergence adversarial repair

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260717T152618Z with Python 3.12.10, numpy 1.26.4,
and torch 2.11.0+cpu.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `b-a3f`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/a3f/notes/a3-full-production-discretization-continuum-260717-v2.2.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # dependencies discovered from entry scripts
  python codes/foundations/a3_full_production_spatial_consistency.py
  python codes/foundations/a3_full_production_finite_time_convergence.py
  python codes/foundations/a3_full_production_hessian_ritz_convergence.py
  python codes/foundations/a3_full_production_independent_galerkin.py
  python codes/foundations/a3_full_production_solution_ball_bound.py
  python codes/foundations/a3_full_production_energy_ball_envelope.py
  python codes/foundations/a3_full_production_quantitative_majorant.py
  python codes/foundations/a3_full_production_quantitative_majorant_independent.py
  python codes/foundations/a3_full_production_bundle_verify.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a3_full_production_spatial_consistency: exit 0, `A3-FULL-SPATIAL-CONSISTENCY-PASS`
  a3_full_production_finite_time_convergence: exit 0, `A3-FULL-FINITE-TIME-CONVERGENCE-PASS`
  a3_full_production_hessian_ritz_convergence: exit 0, `A3-FULL-HESSIAN-RITZ-CONVERGENCE-PASS`
  a3_full_production_independent_galerkin: exit 0, `A3-FULL-INDEPENDENT-GALERKIN-PASS`
  a3_full_production_solution_ball_bound: exit 0, `A3-FULL-SOLUTION-BALL-BOUND-PASS`
  a3_full_production_energy_ball_envelope: exit 0, `A3-FULL-ENERGY-BALL-ENVELOPE-PASS`
  a3_full_production_quantitative_majorant: exit 0, `A3-FULL-QUANTITATIVE-MAJORANT-PASS`
  a3_full_production_quantitative_majorant_independent: exit 0, `A3-FULL-QUANTITATIVE-MAJORANT-INDEPENDENT-PASS`
  a3_full_production_bundle_verify: exit 0, `A3-FULL-PRODUCTION-VERIFY-PASS`

## Integrity
`MANIFEST.json` hashes every bundle file except itself and records the
content-addressable bundle digest plus the repository commit.

## Scope / how to attack
See the note's scope, devil's-advocate, falsifier, and no-overclaim statement.
The bundle does not enlarge the claim beyond that pinned scope.
