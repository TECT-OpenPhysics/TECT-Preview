# HYB-TECT-U1-CHARGED-SPECTRAL-0002 Certificate

Date: 2026-08-23
Task: T-054
Tier: T0 exploratory, claim-bearing false
Admission: comparison candidate only

## Candidate scope

This candidate is a same-parent finite covariantization of the canonical A1
`F_ref` backend on the declared side-4 periodic torus. It uses the nontrivial
charged representation `R(exp(i theta)) = exp(i theta) I_3`, canonical positive
coordinate path transport, endpoint-transported A1 spectral convolution
kernels, `L_U = sum_i (D_i^U)^* D_i^U`, and the A1 family, fixed `z0` lock,
nonlinear, and Class-II coefficients. The reverse-link convention is explicit:
the transporter uses the conjugate of each forward link so that the matrix
operator transforms as `D_i^U -> H D_i^U H^*` when `psi -> H psi`.

The finite checks are implemented by three separate surfaces:

- `codes/foundations/pre_a_hyb_u1_charged_spectral_covariant.py` (20/20 primary)
- `codes/foundations/pre_a_hyb_u1_charged_spectral_covariant_independent.py` (15/15 independent, different site ordering and FFT reconstruction)
- `codes/foundations/pre_a_hyb_u1_charged_spectral_covariant_verify.py` (14/14 integrated)

The exact arithmetic cross-check is
`verification/lean/Tect/HYB0002.lean`, compiled with the pinned Lean/Mathlib
registry toolchain. The generated run records are stored under the A13 claim
run directory and include the exact derived errors and boundaries.

## Checked facts

1. The charged endpoint transporter, each derivative matrix, and the induced
   Laplacian obey endpoint conjugation to numerical tolerance.
2. Setting all links to one recovers the A1 spectral derivative and the full
   finite `F_ref` action on the declared side-4 grid.
3. The A1 quadratic core has positive finite coercivity margin; the Class-II
   coefficient matrix has positive determinant; the sextic lower-bound sign is
   retained.
4. The identity-mobility formal Gibbs residual is an exact rational identity.
5. The Lean file contains no `sorry`, `admit`, `axiom`, or `unsafe` escape.
6. The R-192 crosswalk remains explicitly false for every production slot, with
   `heat_root_incidence` preserved as the first missing slot.

## Adversarial review

- Trivial-representation mutation: rejected. The candidate requires the charged
  scalar U(1) representation and tests nonconstant links and gauges.
- Finite-difference substitution: rejected. The derivative kernel is the A1
  spectral Fourier kernel; the independent verifier compares its gauge-off
  action to an independently reconstructed FFT derivative.
- Endpoint-transport omission: rejected. Dropping the endpoint conjugation
  fails the D and L covariance checks; the implemented reverse-link convention
  is recorded above.
- `F_decl` substitution: rejected. The source manifest is hash-pinned and the
  candidate tests the unchanged `F_ref` coefficients while preserving the
  known A1 `F_decl`/residual mismatch boundary.
- Family/lock mutation: rejected. The family masses and fixed `z0` lock are
  read from A1 and included in the orbit-invariance and gauge-off checks.
- Formal-to-physical promotion: rejected. The finite Gibbs identity is only a
  declared identity-mobility/formal check, not a heat-flow or invariant-measure
  theorem.
- Fabricated production owner: rejected. No root filtration, conditional
  replicas, raw-current spatial intertwiner, or one-use q-ledger is inserted.
- Lean escape hatch: rejected by source-policy and compile checks.

## Boundary and next gate

This is stronger than the prior trivial or external comparison screens because
it preserves the exact A1 finite parent while introducing a nontrivial charged
U(1) orbit. It is still not an A13 production dynamics owner, not a Sector-A
closure, and not a continuum QFT construction. It supplies none of the R-192
production slots, OS/Wightman or KMS reconstruction, thermodynamic limit,
or mass-gap conclusion. The next admissible gate is to recover and verify the
canonical nonlinear heat-root incidence and its one-use q-ledger without
altering the A1 parent or silently importing a different external dynamics.
