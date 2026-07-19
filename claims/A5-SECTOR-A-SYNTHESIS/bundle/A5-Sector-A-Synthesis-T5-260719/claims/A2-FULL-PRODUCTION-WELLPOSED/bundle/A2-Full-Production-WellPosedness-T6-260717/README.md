# Reproduction bundle -- Full production three-component gradient-flow well-posedness

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260717T023217Z with Python 3.12.13, numpy 2.3.5,
and torch not-installed.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `A2-Full-Production-WellPosedness-T6-260717`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-full-production-wellposedness-260717-v2.0.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # dependencies discovered from entry scripts
  python codes/foundations/a2_full_production_wellposedness_checks.py
  python codes/foundations/a2_full_production_nonlinear_mapping_audit.py
  python codes/foundations/a2_full_production_energy_continuation_audit.py
  python codes/foundations/a2_full_production_smoothing_audit.py
  python codes/foundations/a2_full_production_verify.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a2_full_production_wellposedness_checks: exit 0, `Verdict: A2-FULL-COERCIVITY-BASELINE-PASS`
  a2_full_production_nonlinear_mapping_audit: exit 0, `Diagnosis: A2-FULL-NONLINEAR-MAPPING-AUDIT-PASS`
  a2_full_production_energy_continuation_audit: exit 0, `Diagnosis: A2-FULL-ENERGY-CONTINUATION-AUDIT-PASS`
  a2_full_production_smoothing_audit: exit 0, `A2-FULL-SMOOTHING-AUDIT-PASS`
  a2_full_production_verify: exit 0, `A2-FULL-PRODUCTION-VERIFY-PASS`

## Integrity
`MANIFEST.json` hashes every bundle file except itself and records the
content-addressable bundle digest plus the repository commit.

## Scope / how to attack
See the note's scope, devil's-advocate, falsifier, and no-overclaim statement.
The bundle does not enlarge the claim beyond that pinned scope.
