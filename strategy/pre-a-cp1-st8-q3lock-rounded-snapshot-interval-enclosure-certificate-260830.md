# R-431 rounded-snapshot interval-enclosure certificate

## 1. Result and exact scope

R-431 (`PA-CP1-ST8-Q3LOCK-ROUNDED-SNAPSHOT-INTERVAL-ENCLOSURE-v0`) is a T0,
claim-nonbearing finite certificate for the fixed R-426 failure row:

`V=2`, cutoff dimension `d=16`, `beta=8`, right orientation, conditional row
`7`, core/tail `7/9`, with the unchanged comparison tolerance `5e-7`.

The input is the deterministic R-429 binary64 graph snapshot.  Each stored
binary64 value is represented as its exact binary rational before interval
arithmetic.  The original 256-dimensional Hamiltonian and its Gibbs/coordinate
eigensystems are not enclosed by this result.

## 2. Executed method

The primary lane uses 80-digit directed `mpmath.iv` arithmetic.  It constructs
the symmetric conductance hull, the weighted blockwise zero-mean residual basis,
and the 14-dimensional compressed operator.  An interval Cholesky factorization
of `A - L I` proves positive definiteness at
`L=5.3631875357`.  An interval Rayleigh quotient for an independently obtained
finite eigenvector gives an upper endpoint below
`5.3631875359`.  The resulting bracket has width below `3e-10`.

The independent lane reconstructs the same upstream snapshot without importing
R-431, reverses block/anchor order, reverses the compressed pivot order, and
repeats the interval lower/upper checks.  The hostile lane rejects source,
row, tolerance, interval, status and residual-reuse promotion mutations.
Lean R431 checks the rational threshold inequalities and the finite scope.

## 3. Executed evidence

Primary: `16/16` assertions pass.  The certified lower endpoint is
`5.3631875357`; the interval Rayleigh upper endpoint is
`5.3631875357858094719615598072499099181814069649417...`.

The lower endpoint exceeds the R-422 reference by more than `5e-7`, with lower
margin `0.000002568536301...`.  The upper endpoint is below the R-426 direct
reference by more than `5e-7`, with upper margin
`0.0000008142620005...`.

Independent: `12/12` assertions pass, with upper endpoint
`5.363187535785720770809451305696661...`.  Hostile: `7/7` invalid mutations
are rejected.  Integrated verification: `15/15`; Lean R431 compiles without
`sorry`, `admit`, `axiom` or `unsafe`.

## 4. Adversarial review

1. **Input identity.**  Binary64 values are treated as exact snapshot inputs;
   no hidden decimal conversion is used.  This does not certify the upstream
   Hamiltonian source.
2. **Symmetry.**  Both conductance directions are enclosed by a symmetric
   interval hull, so a one-sided rounded entry cannot manufacture positivity.
3. **Lower bound.**  The lower endpoint is accepted only after every interval
   Cholesky pivot has a positive lower endpoint.  A higher probe
   `5.3631875360` is rejected, but the upper bound is obtained independently
   from the Rayleigh quotient.
4. **Reference comparisons.**  The fixed `5e-7` tolerance is read from the
   manifest and is not relaxed.  Both comparisons use one-sided certified
   endpoints.
5. **Promotion firewall.**  The interval certificate is explicitly marked
   rounded-snapshot-only; hostile mutations attempting original-source or
   residual-reuse closure are rejected.

## 5. Boundary and next unlock

R-431 certifies a narrow eigenvalue bracket and both fixed-reference
separations for one finite rounded graph snapshot.  It does not certify the
original Hamiltonian/Gibbs source, close R-426 for the unrounded model, or give
any cutoff-, volume-, phase- or exhaustion-uniform estimate.  Common Q3 core,
history transfer, OS/KMS/GNS reconstruction, C6, Sector-A, Pre-A, Yang--Mills
and mass-gap conclusions remain open.

The next unlock is a validated interval or ball reconstruction of the original
coordinate and Hamiltonian eigensystems, followed by propagated Gibbs-row and
residual enclosures at the same fixed row.
