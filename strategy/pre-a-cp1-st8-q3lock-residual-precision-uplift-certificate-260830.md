# R-429 -- High-precision residual eigensolve on the fixed rounded graph

## Decision

R-429 / EXP-001274 is a T0, claim-nonbearing downstream precision uplift for
the R-426/R-428 failing row.  It retains `V=2`, cutoff `d=16`, `beta=8`,
right orientation, conditional row `7`, core/tail `7/9`, and the immutable
R-426 comparison tolerance `5e-7`.  The finite graph weights and
conductances produced by R-428 are converted from their canonical decimal
strings into 80-digit `Decimal` values.  No new upstream Gibbs or coordinate
diagonalization is substituted.

Two differently ordered weighted-zero-mean bases are built with Decimal
modified Gram--Schmidt, and each 14-dimensional residual compression is
diagonalized by a deterministic symmetric Jacobi iteration stopped at
`1e-60`.  The first eigenvalues agree within `4e-79`:

```text
invariant residual gap   5.3631875357855276117480294524057207054685060592567614...
R-422 reference          5.363184967163699
R-422 mismatch            2.5686218286117480294524057207054685e-06
R-426 direct reference   5.36318835004781
direct-reference gap     8.1426228238825197054759427929453e-07
fixed tolerance           5.000000000000000e-07
basis-gap agreement       4e-79
```

Thus the R-426 mismatch persists after a basis-invariant high-precision
eigensolve of the decimalized graph snapshot.  The finite classification is
`ROUNDED_INPUT_ALGEBRAIC_BOUNDARY`: downstream double-precision eigensolver
conditioning alone is not sufficient to remove the observed separation.
This does not certify that the original unrounded Hamiltonian has the same
gap, because upstream state, coordinate-basis and graph construction errors
are not enclosed.  R-426's route-local failure remains open and is not
repaired.

## Executed evidence

The primary Decimal lane passes `14/14` assertions and converges in `388` and
`391` Jacobi sweeps for the two basis orderings.  The independent non-importing
lane uses reversed block anchors and a separate Jacobi implementation,
passing `7/7`; it obtains the same 80-digit gap and a mismatch above `5e-7`.
The hostile lane passes `10/10`, rejecting nonfinite/negative/unnormalized
graphs, nonsymmetric or negative conductances, precision/tolerance/row
mutations and a forged certified verdict.  The integrated verifier passes
`15/15`.  Lean R429 compiles scalar lower-bound, basis-agreement and finite
scope theorems; Decimal matrix products and Jacobi iterations remain in
Python.

## Adversarial review

1. **Decimal is not an upstream interval enclosure.**  Decimalizing a binary
   float snapshot certifies the downstream arithmetic for that snapshot only;
   it does not recover missing digits in the Gibbs state or coordinate
   eigenbasis.  Disposition: **UPHELD-OPEN**.
2. **Basis-order dependence.**  The anchor and reversed-anchor residual bases
   agree to `4e-79` after independent high-precision solves, so the observed
   separation from R-422 is not explained by the tested basis ordering.  A
   rigorously conditioned original-input calculation is still missing;
   disposition: **UPHELD-OPEN**.
3. **Tolerance manipulation.**  The R-426 comparison tolerance remains
   `5e-7`; the separate Jacobi stopping threshold `1e-60` and parent
   reconstruction threshold `1e-7` do not alter it.  Disposition:
   **DISMISSED-FINITE**.
4. **Jacobi convergence.**  The residual off-diagonal is below `1e-60` in
   both runs, but no interval eigenvalue enclosure is claimed; disposition:
   **UPHELD-OPEN** for the original unrounded source.
5. **Finite-to-physical promotion.**  One decimalized volume-two row cannot
   close cutoff/volume/phase/exhaustion uniformity, a common core,
   OS/KMS/GNS, a physical sector, Yang--Mills or a mass gap; disposition:
   **UPHELD-OPEN**.

## Assumptions and missing assumptions

Assumptions used:

- the R-428 double-precision graph snapshot is the fixed finite input;
- its weights are positive and normalized to the declared finite tolerance,
  and its conductance is symmetric and nonnegative;
- the two blockwise weighted-zero-mean constructions describe one residual
  subspace in exact arithmetic;
- Decimal modified Gram--Schmidt and Jacobi convergence at the declared
  precision are valid for that rounded snapshot; and
- the R-426 row and `5e-7` comparison tolerance are immutable.

Missing for an original-source certification are arbitrary-precision or
interval reconstruction of the Hamiltonian Gibbs state, coordinate
diagonalization and projected graph; propagation of those input enclosures
through the residual operator; and any common-core, regulator/volume-uniform,
history, OS/KMS/GNS or physical-sector transfer.

## Boundary and next action

R-429 closes only the downstream rounded-input precision uplift and confirms a
finite basis-invariant separation from the R-422 reference.  It does not close
R-426 residual reuse, Q3LOCK, C6, Sector-A or Pre-A.  The next unlock is an
interval or arbitrary-precision reconstruction beginning with the original
Hamiltonian Gibbs and coordinate eigenbasis, followed by propagated residual
enclosures at the same fixed row and tolerance.

Evidence level: `T0 / executed 80-digit Decimal downstream precision uplift
on the fixed R-428 graph snapshot; upstream source uncertainty remains open`.

No cutoff-, volume-, phase- or exhaustion-uniform bound, continuum result,
physical-sector result, Yang--Mills result, or mass-gap result is claimed.
