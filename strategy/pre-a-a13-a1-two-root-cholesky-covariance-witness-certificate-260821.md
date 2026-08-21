# R-176 v1.0 certificate

## Scope

R-176 is a T0, claim-nonbearing Lean cross-check under EXP-000891. It
instantiates the hash-pinned A1 production symbol at the two registered roots
`k=(pi/8,0,0)` and `2k=(pi/4,0,0)`.

For `A(a)=a I+M`, with `M` reconstructed from the A1 family masses, lock
projector and `z0`, define the lower factor

`L=[[s1,0,0],[q21,s2,0],[q31,q32,s3]]`

with

`d1=a+M11`, `s1=sqrt(d1)`, `q21=M21/s1`, `q31=M31/s1`,
`d2=a+M22-q21^2`, `s2=sqrt(d2)`,
`q32=(M32-q31*q21)/s2`, and
`d3=a+M33-q31^2-q32^2`, `s3=sqrt(d3)`.

The A1 values give positive pivot chains at both roots. The covariance witness
is the inverse-transpose `U=L^(-T)`, so `C(a)=A(a)^(-1)=U U^T`. The duplicated
six-real witness is `G=diag(U,U)` and `Gamma=diag(C,C)`.

## Exact and independent verification

`verification/lean/Tect/R176.lean` proves the exact symbolic 3 by 3 identity
`L L^T=gram3(s1,q21,q31,s2,q32,s3)` over an arbitrary commutative ring. The
primary SymPy lane derives `M`, `a(k)`, `a(2k)`, all six factor entries and the
inverse-transpose residuals. The independent lane uses only the Python
standard library for the A1 numerical roots, matrix inverses, duplicated
six-real products and a rational Gram fixture. The integrated lane pins all
predecessor authorities, hashes, Lean markers, AST/import independence and
hostile mutations.

The primary run records pivot values approximately

`k: (0.4551260655, 0.4796330819, 0.5132126090)` and
`2k: (0.3837815164, 0.4072673934, 0.4394252578)`.

The inverse-transpose covariance and duplicated six-real residuals are below
the primary `1e-55` threshold and the independent `2e-13` threshold. These are
finite arithmetic witnesses derived from the current A1 manifest, not a claim
that a global square-root field has been canonically selected.

## Boundary and next proof action

R-176 does not freeze heat/root incidence, raw/past/future covariance,
complement, historical-low, forest, returned mean, source/sextic one-use, or
the complete joint scalar owner. It does not close T-050, either A13 gate,
Nelson, a measure, phase selection, PDE replacement, physical-empty comparison,
removal, continuum limits, Sector-A or Pre-A. No tier change, gate closure,
new negative or PDF follows.

The next admissible step is to place these actual `k` and `2k` roots into the
R-174 cylinder, freeze every heat/root incidence and covariance role, and
differentiate the complete owner once with each ordered cross block retained
exactly once.

No R-176 PDF is issued.
