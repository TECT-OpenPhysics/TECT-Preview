# Reproduction bundle -- SC-SCOPE sunset-hardened endpoint: comfortable closure (S x2.994; joint x2.023; worst mixed-dressing x1.886)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260613T011125Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `SC-SCOPE-SunsetHardened-T6-260612`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B5-BEYOND-LAYER-BOUND/SC-SCOPE/notes/scscope-sunset-pertransfer-hardening-260612-260612-v1.3.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/scscope_ghat4_pertransfer.py
  python codes/vacuum/scscope_floor_sharpening.py
  python codes/vacuum/scscope_mendpoint_eval.py
  python codes/vacuum/scscope_quartic_certificate.py
  python codes/vacuum/scscope_sunset_pertransfer.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  scscope_ghat4_pertransfer: exit 0, `claims 7/7 PASS`
  scscope_floor_sharpening: exit 0, `claims 5/5 PASS`
  scscope_mendpoint_eval: exit 0, `claims 12/12 PASS`
  scscope_quartic_certificate: exit 0, `claims 5/5 PASS`
  scscope_sunset_pertransfer: exit 0, `claims 10/10 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`17dffa1acc8dacc5ca7f09bb22522ed1bcfcf2acb44a8e4643e2d73a90b5d36d`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
