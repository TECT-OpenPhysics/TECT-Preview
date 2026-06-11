# Reproduction bundle -- B1-RH-ENUM / ESTIMATOR-UPGRADE

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260611T033443Z with Python 3.12.10, numpy 2.2.6.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B1-RH-ENUM/ESTIMATOR-UPGRADE/notes/estimator-upgrade-closure-consolidation-260607-v1.0.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/estimator_upgrade_enumerated.py
  python codes/vacuum/estimator_upgrade_knobs.py
  python codes/vacuum/g3pb3_ratio_extraction.py
  python codes/vacuum/res_endpoint_admissible_pin.py
  python codes/vacuum/res5_rpa_screening.py
  python codes/vacuum/res5_a0_skeleton_sensitivity.py
  python codes/vacuum/res5_allorder_commonmode.py
  python codes/vacuum/res5_017_chi_bypass.py
  python codes/vacuum/res5_commonmode_envelope.py
  python codes/vacuum/res5_dr2_kappa_bound.py
  python codes/vacuum/res5_dressed_loop_parameter.py
  python codes/vacuum/res5_endpoint_2pi_bound.py
  python codes/vacuum/res5_higherloop_skeleton.py
  python codes/vacuum/res5_2pi_commonmode_monotonicity.py
  python codes/vacuum/res5_oneloop_disentangle.py
  python codes/vacuum/res5_orderedbcc_parallel.py
  python codes/vacuum/res5_projection_factor.py
  python codes/vacuum/res5_sunset_norm_map.py
  python codes/vacuum/res5_susceptibility_ratio.py
  python codes/vacuum/res5_tail_budget.py
  python codes/vacuum/twoshell_anchored_bracket.py
  python codes/vacuum/twoshell_continuum_bound.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  estimator_upgrade_enumerated: exit 0, `claims 7/7 PASS`
  estimator_upgrade_knobs: exit 0, `claims 13/13 PASS`
  g3pb3_ratio_extraction: exit 0, ``
  res_endpoint_admissible_pin: exit 0, `claims 4/4 PASS`
  res5_rpa_screening: exit 0, `claims 5/5 PASS`
  res5_a0_skeleton_sensitivity: exit 0, `claims 4/4 PASS`
  res5_allorder_commonmode: exit 0, `claims 4/4 PASS`
  res5_017_chi_bypass: exit 0, `claims 3/3 PASS`
  res5_commonmode_envelope: exit 0, `claims 4/4 PASS`
  res5_dr2_kappa_bound: exit 0, `claims 4/4 PASS`
  res5_dressed_loop_parameter: exit 0, `claims 4/4 PASS`
  res5_endpoint_2pi_bound: exit 0, `claims 5/5 PASS`
  res5_higherloop_skeleton: exit 0, `claims 3/3 PASS`
  res5_2pi_commonmode_monotonicity: exit 0, `claims 5/5 PASS`
  res5_oneloop_disentangle: exit 0, `claims 3/3 PASS`
  res5_orderedbcc_parallel: exit 0, `claims 4/4 PASS`
  res5_projection_factor: exit 0, `claims 5/5 PASS`
  res5_sunset_norm_map: exit 0, `claims 4/4 PASS`
  res5_susceptibility_ratio: exit 0, `claims 4/4 PASS`
  res5_tail_budget: exit 0, `claims 5/5 PASS`
  twoshell_anchored_bracket: exit 0, ``
  twoshell_continuum_bound: exit 0, `claims 10/10 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`5e693ffe826b0f52963e48e7359604efb9b82b4f04588fcea5778fa61ec4703f`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
