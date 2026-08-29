# R-423 -- Finite directed boundary-capacity Cauchy envelope

## Decision

R-423 / EXP-001268 is a T0, claim-nonbearing finite interface.  It replaces
the R-422 restricted numerical cross norm by a transparent directed-capacity
envelope.  For disjoint core and tail supports, put

```text
B_ij = c_ij / sqrt(pi_i*pi_j),
rho_C = max_i sum_{j in T} c_ij/pi_i,
rho_T = max_j sum_{i in C} c_ij/pi_j.
```

Factoring each edge gives

```text
|sum_ij B_ij x_i y_j|
  <= sqrt(rho_C*rho_T) ||x||_2 ||y||_2.
```

Consequently the finite sufficient reserve is

```text
lambda_capacity = min(a,kappa) - sqrt(rho_C*rho_T).
```

The capacity bound is deliberately conservative.  It is an analytic target
for the later common-core proof, not a claim that the tested finite Q3 rows
have a positive uniform reserve.

## Fixed scope and inputs

The R-419 conditional Gibbs law, projected momentum conductance, beta values
`{1/2,2,8}`, both collar orientations, `alpha=1/40`, tail threshold `4`, and
the six systems `(V,d)=(2,3),(2,6),(2,12),(3,3),(3,4),(4,4)` are reused
without retuning.  The R-422 block-mean-zero core/tail split and R-421 tail
Hardy floor are retained.  Directed capacities are computed from the same
conductance and conditional weights; no diagonal term crosses the disjoint
supports.

## Executed evidence

The primary lane passes `2209/2209` assertions over 858 conditional rows and
114 eligible residual rows.  The exact R-422 restricted cross norm is bounded
by the capacity envelope on every eligible row.  The capacity range is
`[2.5432351046609147, 3654.481957885938]`, while the capacity-reserve range is
`[-3650.2671476576393, -1.7429838727911164]`.  Thus zero of the 114 eligible
Q3 rows has a positive capacity reserve; all 114 nonpositive rows are retained
as a sufficient-budget boundary rather than clipped or relabeled.

The non-importing independent lane passes `40/40` assertions on four
reversible fixtures, with three positive and one nonpositive reserve.  The
hostile lane rejects `7/7` mutations, including nonpositive weights,
non-symmetric or negative conductance, invalid supports, a cross norm above
capacity, a negative cross norm, and a forged reserve.  The integrated verifier
passes `18/18`, and `lake env lean Tect/R423.lean` passes.

## Lean cross-check

`verification/lean/Tect/R423.lean` proves the scalar weighted
Cauchy-capacity inequality and the resulting reserve bound.  It does not
formalize the Q3 eigensolver, directed maxima, common Hamiltonian domain, or
any limit.

## Adversarial review

1. **Wrong normalization.**  The transformed cross block must use
   `c_ij/sqrt(pi_i*pi_j)`; omitting either weight changes the capacity.
   The primary and independent lanes construct the factors explicitly;
   disposition: DISMISSED-FINITE.
2. **Support leakage.**  The edgewise factorization requires disjoint core and
   tail supports.  Invalid overlap and out-of-range support mutations are
   rejected; disposition: DISMISSED-FINITE.
3. **Capacity sign.**  Negative or nonfinite directed rates are rejected and
   no square root is evaluated on invalid inputs; disposition: DISMISSED-FINITE.
4. **Cross-term omission.**  The capacity is subtracted from the reserve;
   a claimed cross norm above the envelope is rejected; disposition:
   DISMISSED-FINITE.
5. **Reserve clipping.**  The high-cutoff negative values are preserved and
   never replaced by zero; disposition: DISMISSED-FINITE.
6. **Coarse-sector leakage.**  The two block-mean modes and their Schur
   complement are not controlled by this envelope; disposition: UPHELD-OPEN.
7. **Uniform/physical promotion.**  The tested capacity grows strongly with
   cutoff and the finite reserve is nonpositive on every eligible Q3 row; no
   uniform, GNS, continuum, C6, Sector-A, Pre-A, Yang--Mills or mass-gap
   statement follows; disposition: UPHELD-OPEN.

## Boundary and next action

R-423 closes only the finite edgewise capacity inequality and its numerical
cross-check.  The all-nonpositive Q3 capacity reserves show that this direct
max-rate envelope is too coarse to unlock the residual coercivity route at the
tested cutoffs.  This is a boundary of the sufficient estimate, not a theorem
of physical gaplessness.

The next useful route is to derive a sharper boundary-capacity estimate from
the Hamiltonian common core (for example, a localized trace or weighted
Carleson estimate), then combine it with the two-dimensional block-mean Schur
sector and the R-399/R-415 history transfer.  Until those estimates are
uniform and domain-controlled, the Q3LOCK common-alpha and broken-sector GNS
parents remain open.

## Assumptions and missing assumptions

Assumptions used here:

- positive normalized conditional weights and symmetric nonnegative
  conductance from the fixed R-419 construction;
- exact reuse of the R-421 tail floor and R-422 residual split;
- finite disjoint supports and the square-root-of-`pi` coordinate transform;
- finite directed rates computed with the same normalization as the parent;
- Lean checks only the scalar algebraic envelope.

Missing for promotion:

- cutoff-, volume-, phase- and exhaustion-uniform directed capacities on one
  Hamiltonian common core;
- a positive reserve after combining the capacity envelope with core and tail
  floors at every scale;
- control of the block-mean coarse Schur sector;
- two-sided R-399 history/form convergence and the split-limit map;
- Hamiltonian-to-OS/KMS/GNS identification and a sectorwise coercive rate.

Evidence level: `T0 / exact finite edgewise Cauchy envelope plus executed
Q3-row diagnostic`.  No physical or regulator-independent conclusion is
claimed.
