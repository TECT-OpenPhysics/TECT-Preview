# Reproduction bundle -- A1 N-001 production-kernel manifest (real solver; eta_shell=0)

Self-contained referee reproduction bundle (TECT verification-first repository).
Built 20260623T120854Z with Python 3.10.12, numpy 2.2.6.

**Bundle grade:** PUBLISHED (operator-confirmed) -- `A1-N001-Manifest-260623`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `claims/A1-PRODUCTION-KERNEL-MANIFEST/notes/a1-production-kernel-manifest-260623-260623-v1.4.tex.txt`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
  python codes/foundations/a1_kernel_checks.py
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
  a1_kernel_checks: exit 0, `A1 kernel checks v1.4: 13/13 PASS`

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`3df9d23ddfb85c115c225a54930aa25e89f4bfdeae80f4d995567c16b31899ff`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
