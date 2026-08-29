# R-424 -- Finite two-block harmonic coarse Schur assembly

## Decision

R-424 / EXP-001269 is a T0, claim-nonbearing finite interface.  It retains
the two block-constant modes that the R-422 residual audit deliberately
excluded, eliminates the residual complement by the exact finite harmonic
solve, and records a conservative combined lower envelope.  The assembly is
performed on the same R-419 conditional law, projected conductance and R-422
core/tail split; no regulator, volume, phase, boundary or limit input is
retuned.

For the transformed finite operator `A`, let `U` be the weighted span of the
two block-constant vectors and `V` its Euclidean orthogonal complement.  The
finite Schur operator is

```text
S = A_UU - A_UV A_VV^(-1) A_VU.
```

The first positive generalized eigenvalue of `S` relative to the harmonic
coarse mass is the coarse Schur gap.  The least eigenvalue of `A_VV` is the
residual gap.  The checked harmonic/residual split gives the recorded finite
envelope `0.5 * min(coarse_gap, residual_gap)`.

## Fixed scope and inputs

The fixed grid is `(V,d)=(2,3),(2,6),(2,12),(3,3),(3,4),(4,4)`, beta values
`{1/2,2,8}`, orientations `right/left`, `alpha=1/40`, tail threshold
`theta=4`, probability floor `1e-300`, comparison tolerance `5e-7`, and gap
floor `1e-8`.  Rows with fewer than two core or tail coordinates are recorded
but not admitted to the two-block assembly; this is why the d=3 systems have
zero eligible rows.

## Executed evidence

The primary lane passes `1471/1471` assertions over 858 conditional rows,
282 rows with a nonempty tail, and 114 eligible rows.  All 114 eligible rows
are assembled (`combined_row_count=114`).  The finite coarse Schur gap ranges
from `9.416287072814253` to `900.9775546526778`; the residual gap ranges from
`2.0659023307146094` to `7.874609499214968`; and the conservative combined
envelope ranges from `1.0329511653573047` to `3.937304749607484`.  The largest
independently recomputed residual difference is
`9.393117395006811e-10`, below the declared comparison tolerance, and the
minimum harmonic lower-bound probe margin is `0.15688515408073822`.

The non-importing independent lane passes `27/27` assertions on four
reversible fixtures.  Its coarse, residual and combined minimum values are
`0.7167320977066365`, `0.7192914012232517` and `0.35836604885331824`, with a
maximum energy-split residual of `8.326672684688674e-17`.  The hostile lane
rejects `7/7` invalid mutations; the integrated verifier passes `22/22`; and
the Lean R424 file compiles.

## Lean cross-check

`verification/lean/Tect/R424.lean` proves the scalar harmonic energy split and
the lower-envelope inequality `min(a,b)(x^2+y^2) <= a*x^2+b*y^2`, with a
finite-parameter scope marker.  It does not formalize the numerical matrix
Schur solve, Gibbs reconstruction, row eligibility, or any limiting domain.

## Adversarial review

1. **Residual invertibility.**  The Schur solve is legal only when the finite
   residual block is positive.  Singular/disconnected mutations are rejected;
   disposition: DISMISSED-FINITE.
2. **Weighted normalization.**  The block vectors use the same normalized
   `pi` and the `sqrt(pi)` transform as the parent rows.  Nonpositive or
   non-normalized weights are rejected; disposition: DISMISSED-FINITE.
3. **Support partition.**  Core and tail supports must be disjoint, in range,
   and large enough for block-mean-zero residual coordinates.  Overlap and
   undersized-block mutations are rejected; disposition: DISMISSED-FINITE.
4. **Schur direction.**  The coupling correction is subtracted from the
   block restriction; an upward or forged combined envelope is rejected;
   disposition: DISMISSED-FINITE.
5. **Residual reuse.**  The R-422 residual eigenvalue is recomputed from an
   independent block-mean-zero basis and compared within `5e-7`; disposition:
   DISMISSED-FINITE.
6. **Coarse-sector completeness.**  The two block modes are retained here,
   but only on the declared finite rows and with no common-core construction;
   disposition: UPHELD-OPEN.
7. **Uniform and physical promotion.**  Positive finite Schur values do not
   control cutoff, volume, phase or exhaustion limits, history transfer,
   OS/KMS/GNS reconstruction, a continuum statement, C6, Sector-A, Pre-A,
   Yang--Mills or a mass-gap statement; disposition: UPHELD-OPEN.

## Boundary and next action

R-424 closes the finite two-block harmonic assembly and confirms that the
coarse and residual pieces can be evaluated together on the fixed Q3 rows.
This is a finite interface, not a uniform coercivity theorem.  The next
analytic target is a domain-controlled coarse-capacity and residual-boundary
estimate on one common core, followed by the R-399/R-415 history transfer and
the OS/KMS/GNS interfaces.  The Q3LOCK parent gates remain open.

## Assumptions and missing assumptions

Assumptions used here:

- positive normalized conditional weights and symmetric nonnegative projected
  conductance from the hash-pinned R-419 construction;
- exact reuse of the R-422 core/tail split, `alpha` and `theta`;
- disjoint nonempty finite blocks and the finite `sqrt(pi)` transform;
- positive residual block on every eligible row, making the harmonic inverse
  well-defined;
- no upward rounding of finite lower bounds, with Lean used as a scalar
  cross-check only.

Missing for promotion:

- cutoff-, volume-, phase- and exhaustion-uniform coarse Schur and residual
  bounds on one Hamiltonian common core;
- a common split-limit map for the block variables and residual coordinates;
- two-sided form-norm control of actual R-399 histories and transfer through
  the R-415 semigroup estimates;
- Hamiltonian-to-OS/KMS/GNS identification and a sectorwise coercive estimate.

Evidence level: `T0 / exact finite harmonic coarse-Schur decomposition plus
executed Q3-row assembly`.  No physical or regulator-independent conclusion
is claimed.
