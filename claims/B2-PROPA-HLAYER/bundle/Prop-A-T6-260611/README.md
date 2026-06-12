# Reproduction bundle -- Prop-A class-wide H-LAYER closure on A_adm (T'<=13), T6 main-line supporting (PUBLISHED)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260612T023731Z with Python 3.12.10, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `Prop-A-T6-260611`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B2-PROPA-HLAYER/Prop-A/notes/prop-a-referee-package-260610-260611-v1.3.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/hdiag_convexity_probe.py
  python codes/vacuum/res5_016_isotropy_infimum_core.py
  python codes/vacuum/hdiag_offdiag_additive_energy.py
  python codes/vacuum/hdiag_offdiag_constant_certificate.py
  python codes/vacuum/res1_hdiag_offdiag_floor.py
  python codes/vacuum/res5_019_exchange_scalar_identification.py
  python codes/vacuum/hdiag_gershgorin_rowsum.py
  python codes/vacuum/res5_020_classwide_secondcumulant_stability.py
  python codes/vacuum/res5_029_t7_route_audit.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  hdiag_convexity_probe: exit 0, `claims 5/5 PASS`
  res5_016_isotropy_infimum_core: exit 0, `claims 6/6 PASS`
  hdiag_offdiag_additive_energy: exit 0, `claims 6/6 PASS`
  hdiag_offdiag_constant_certificate: exit 0, `claims 5/5 PASS`
  res1_hdiag_offdiag_floor: exit 0, `claims 4/4 PASS`
  res5_019_exchange_scalar_identification: exit 0, `claims 5/5 PASS`
  hdiag_gershgorin_rowsum: exit 0, `claims 3/3 PASS`
  res5_020_classwide_secondcumulant_stability: exit 0, `claims 5/5 PASS`
  res5_029_t7_route_audit: exit 0, `claims 5/5 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`62ee56083305123bc12b757b13adcae890e4dd60c9b15c624d03c33feb163fea`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
