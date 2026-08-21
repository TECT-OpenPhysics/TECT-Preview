# R-174: exact two-root production-cylinder cross-synthesis boundary

## Status

This is a T0, claim-nonbearing finite-cylinder interface result. It is the
next construction step after R-150/R-151 and does not close T-050, A13, or
Sector A.

## Frozen chart

Use the hash-pinned A1 `L=16` torus and the registered antipodal roots
`k=(pi/8,0,0)` and `q=2k=(pi/4,0,0)`. The A1 mass matrix is reconstructed from
the family masses, lock projector and `z0`; the two scalar kinetic symbols are
`a(k)=r+Z|k|^2+Y|k|^4` and `a(q)=r+Z|q|^2+Y|q|^4`, both positive at the
registered parameters. R-150 owns the one-root antipodal synthesis and R-151
owns a zero-past two-root Hessian boundary; neither freezes their joint
pointwise cross blocks.

For one polarization write the two phase rows as

`X_j=(a_j c_j, a_j s_j)` and
`V_j=w_j(-a_j s_j, a_j c_j)`,

where `c_j` and `s_j` are the phase cosine and sine and `w_j` is the root
frequency multiplier. The same formulas lift entrywise to actual square-root
bases, with `a_1 a_2` replaced by the ordered matrix product
`S_1 S_2^*` and its transpose.

## Exact identities

The same-root cross block is zero. The two ordered cross blocks are

`X_1 V_2^* = w_2 a_1 a_2 (s_1 c_2-c_1 s_2)`,

`X_2 V_1^* = -w_1 a_1 a_2 (s_1 c_2-c_1 s_2)`,

and hence their sum is

`(w_2-w_1)a_1a_2(s_1c_2-c_1s_2)`.

The field and current cross blocks are respectively
`a_1a_2(c_1c_2+s_1s_2)` and
`w_1w_2a_1a_2(c_1c_2+s_1s_2)`. The registered fixture
`(a_1,a_2,w_1,w_2,c_1,s_1,c_2,s_2)=(1,1,1,2,1,0,0,1)` gives cross block
`-1`. Equal phases or equal frequency multipliers kill the ordered sum, but
the actual dyadic roots have different multipliers and a varying phase
difference. The one-period sine and cosine averages vanish, while the
pointwise cross blocks do not.

These identities show exactly why a diagonal sum of the two one-root
covariances is not the complete pointwise cylinder owner. They do not assign a
sign to the complete action; the missing owner still includes the square-root
bases, heat and root incidence, output complement, historical-low and forest,
returned mean, source, and terminal sextic.

## Lean and independent verification

`verification/lean/Tect/R174.lean` proves the polynomial identities over
`Rat` with `ring`/`norm_num`, without `sorry`, `admit`, `axiom`, or `unsafe`.
The primary lane reconstructs the A1 mass and frequencies and checks the
symbolic identities with SymPy. The independent lane uses only Python's
standard library and `Fraction`, deriving the same fixture and zero cases.
The integrated lane hashes the A1/R-150/R-151/status authorities, the pinned
Lean toolchain and Lake files, runs both children and Lean, and rejects the
registered hostile mutations.

## Boundary and next proof action

No A13 gate closure, phase choice, PDE replacement, physical-empty comparison,
T-050/Nelson/measure theorem, removal or continuum statement follows. The
next proof packet must freeze explicit square-root bases and every remaining
owner block in this same cylinder, differentiate the complete scalar action
once, and test the exact `K_E+K_6` threshold without reusing any block twice.

No R-174 PDF is issued at this interface checkpoint.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_two_root_production_cylinder_cross_synthesis.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_root_production_cylinder_cross_synthesis_independent.py --output %TEMP%\r174-independent.json
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_root_production_cylinder_cross_synthesis_verify.py --staged --no-store
```

