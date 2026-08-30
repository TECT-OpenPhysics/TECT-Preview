# R-428 -- High-cutoff residual-basis conditioning diagnostic

## Decision

R-428 / EXP-001273 is a T0, claim-nonbearing finite diagnostic for the
route-local residual-reuse mismatch recorded by R-426.  The hash-pinned
R-419 conditional law, R-416 log-domain row, R-422 residual construction,
R-406 block complement, R-426 failing row and comparison tolerance `5e-7`
are held fixed.  The diagnostic compares four orthonormal descriptions of
the same weighted-zero-mean core/tail residual subspace:

- the R-406 block-complement basis;
- the R-422 blockwise weighted-zero-mean basis;
- an explicit normalized-constraint projector nullspace; and
- a complete-QR (Householder) constraint nullspace.

The fixed row is `V=2`, cutoff `d=16`, `beta=8`, right orientation,
conditional row `7`, with core/tail sizes `7/9`.  The primary reconstruction
reports:

```text
pi_min                    5.622948645880553e-13
pi_max                    2.864501401805248e-01
pi_dynamic_range          5.094304753972490e+11
operator two-norm         5.7168562623339745e+10
projector distance        9.775397033159746e-16
conditioning budget       1.117690794916405e-04
basis residual-gap spread 4.318739463826660e-06
R-406/R-422 gap mismatch  3.309604201362504e-06
```

All four bases satisfy the declared `1e-12` orthogonality and constraint
checks, and their cross-Gram singular values differ from one by at most the
declared `1e-12`.  The operator norm nevertheless makes the recorded
two-norm perturbation budget much larger than the unchanged `5e-7` audit
tolerance.  The independent non-importing reconstruction gives the same
classification, with spread `1.9067128844696413e-06`, mismatch
`9.865446628509744e-07`, and budget `1.0355183044578828e-04`.

The honest verdict is `INCONCLUSIVE_CONDITIONING`.  This supports a
conditioning-sensitive finite boundary as a repair target, but it does not
identify the mismatch as solely floating-point or solely algebraic.  R-426's
`FAIL_ROUTE_LOCAL` result is preserved; no repair, tolerance relaxation,
clipping, or residual-reuse closure is claimed.

## Executed evidence

The primary lane passes `31/31` assertions and writes the fixed-row metrics.
The independent lane reconstructs the row without importing the R-428
primary module and passes `21/21`.  The hostile lane passes `10/10` checks,
rejecting nine mutations of weights, conductance, basis dimensions, row
identity, tolerance and verdict while preserving the R-426 failure.  The
integrated verifier passes `16/16`.  Lean R428 compiles three scalar
theorems: the projector-distance bound, the conditioning-budget comparison,
and the finite-scope inequalities.  Lean does not formalize the numerical
matrix reconstruction or any limit.

## Adversarial review

1. **Basis-invariant interpretation.**  Near-machine-precision projector and
   cross-Gram agreement could be mistaken for an exact algebraic identity.
   The operator norm and the observed basis-gap spread remain finite-precision
   diagnostics; disposition: **UPHELD-OPEN** pending arbitrary-precision or
   interval certification.
2. **Hidden tolerance change.**  The reconstruction check uses a declared
   `1e-7` reproducibility threshold because independent double-precision QR
   realizations vary at that scale, but the R-426 comparison tolerance remains
   exactly `5e-7`; no mismatch is accepted by changing the audit tolerance;
   disposition: **DISMISSED-FINITE**.
3. **Single-row selection.**  The row, orientation, beta, cutoff and block
   sizes are hash-pinned to the first R-426 failure.  Substituting a more
   stable row or the opposite orientation would answer a different question;
   disposition: **UPHELD-OPEN**.
4. **Conditioning budget as an error theorem.**  The product
   `2*||A||*||P_1-P_2||` is recorded as a scale diagnostic only; it is not an
   eigensolver error bound or a proof that conditioning is the sole cause;
   disposition: **UPHELD-OPEN**.
5. **Finite-to-uniform or physical promotion.**  One finite high-cutoff row
   gives no cutoff-, volume-, phase- or exhaustion-uniform statement and no
   Hamiltonian, OS/KMS/GNS, physical-sector, Yang--Mills or mass-gap result;
   disposition: **UPHELD-OPEN**.

## Assumptions and missing assumptions

Assumptions used:

- the hash-pinned R-419, R-416, R-422, R-406 and R-426 manifests are the
  declared finite inputs;
- the positive normalized graph and reversible conductance are reconstructed
  exactly as specified by those parents;
- the normalized block constraints describe the same residual subspace in
  exact arithmetic;
- the `5e-7` R-426 comparison tolerance is immutable; and
- the two-norm product is a diagnostic scale, not a certified perturbation
  estimate.

Missing for any repair or promotion are an arbitrary-precision or
interval-certified residual eigensolve, a basis-independent exact or
rigorously bounded residual-reuse value, a common unbounded Q3 Hamiltonian
core and cutoff/volume-uniform estimate, and history/OS/KMS/GNS/physical
sector transfer.

## Boundary and next action

R-428 closes only the finite conditioning and basis-crosswalk diagnostic.  It
does not close the R-426 residual-reuse route, the Q3LOCK broken-sector,
higher-moment, common-alpha, C6, Sector-A or Pre-A gates.  The next unlock is
an arbitrary-precision or interval-certified, basis-invariant eigensolve of
this same row with the unchanged `5e-7` comparison tolerance.  Only after
that result is available can the residual-reuse route be classified as
repaired or remain an algebraic boundary.

Evidence level: `T0 / executed finite conditioning and basis-crosswalk
diagnostic; cause of the R-426 mismatch remains inconclusive`.

No cutoff-, volume-, phase- or exhaustion-uniform bound, continuum result,
physical-sector result, Yang--Mills result, or mass-gap result is claimed.
