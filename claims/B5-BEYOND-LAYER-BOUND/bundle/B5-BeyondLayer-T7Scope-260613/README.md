# Reproduction bundle -- B5 beyond-layer bound: T7-SCOPE on the admissibility-bounded statement (route-3 promotion)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260613T104550Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `B5-BeyondLayer-T7Scope-260613`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/B5-BEYOND-LAYER-BOUND/T5-DOSSIER/notes/b5-t7scope-assignment-260613-v1.0.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/vacuum/dr2_t030_route3_nonloadbearing.py
  python codes/vacuum/beyond_layer_gershgorin_bound.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  dr2_t030_route3_nonloadbearing: exit 0, `claims 6/6 PASS`
  beyond_layer_gershgorin_bound: exit 0, `claims 192/192 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`da8a30e76cf75ef6b8ceef8ec489959a48af7015e9795623dbf194311953ce21`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
