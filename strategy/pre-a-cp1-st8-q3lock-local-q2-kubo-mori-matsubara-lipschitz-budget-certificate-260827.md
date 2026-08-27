# EXP-001217 / R-375 certificate

## Result and boundary

R-375 is a T0, claim-nonbearing finite analytic/executable checkpoint.  It
adds a Matsubara first-variation interface to R-374: each positive layer has
an explicit slope envelope `8/omega_n^2`, and the odd-frequency envelopes
are summable to one.  The exact capped kernel independently has unit scalar
Lipschitz constant.  This is a candidate reduction of spectral-kernel
comparison to a first Liouvillian variation, not a locality theorem.

## Why this is a new route

The positive Matsubara decomposition is treated as a frequency-resolved
stability budget rather than only as a tail approximation.  If two finite
Hamiltonians can be compared by matched transition energies, the scalar
kernel discrepancy is bounded by the one-Lipschitz capped kernel (or by the
finite partial budget `L_N`).  The remaining operator problem is made
explicit: eigenvector rotation and a local commutator estimate must be paid
separately.  This prevents a hidden transfer from scalar spectral stability
to spatial locality.

## Finite verification

The primary and independent scripts use the actual R-373 edge and square
fixtures, all declared beta values, spectra of every translated bond, a
257-point energy grid through each observed transition range, three declared
perturbation scales, and the complete all-prefix context count.  They assert
the layer derivative envelopes, partial-budget finite differences, exact
capped-kernel finite differences, nonnegativity, and primary/independent
agreement.

## Lean cross-check

`verification/lean/Tect/R375.lean` proves positivity of the denominator and
layer and the abstract derivative envelope for positive frequency.  It is a
scalar lemma only; no claim is made about the finite matrices or limits.

## Devil's-advocate review

1. **The odd Basel identity may be imported without proof.**  Status:
   VALID-with-mitigation.  It is recorded as an analytic interface and the
   finite code uses explicit partial sums; no infinite identity is cited as a
   Lean theorem.
2. **A scalar Lipschitz bound may be mistaken for an operator-norm bound.**
   Status: UPHELD.  Eigenvector rotation and divided-difference control are
   explicitly outside scope and are the next obligation.
3. **The layer derivative can be singular at zero if expressed through
   `sqrt(L^2)`.**  Status: UPHELD.  The result differentiates the scalar
   transition variable only and makes no square-root commutator claim.
4. **Finite energy grids can hide a large transition.**  Status:
   VALID-with-mitigation.  The grid includes zero, the observed maximum and
   uniform interior points; the analytic envelope is checked symbolically in
   Lean and is independent of grid coverage.
5. **The exact capped kernel could lose the budget at beta extremes.**
   Status: DISMISSED for the scalar statement: its derivative is the exact
   `sech^2(beta Delta/2)` and is bounded by one for every positive beta.  A
   beta-uniform operator estimate remains open.
6. **All-prefix counting could be confused with evolved-witness evaluation.**
   Status: DISMISSED.  R-375 claims only spectral sensitivity and labels the
   prefix component as a count, not as a dynamical matrix estimate.
7. **A convergent frequency budget might still multiply an unbounded local
   energy.**  Status: UPHELD.  The next gate must prove an energy-constrained
   first-Liouvillian estimate on a common polynomial core.
8. **The result could silently advance C6 or Pre-A.**  Status: DISMISSED by
   the manifest scope firewall and integrated verifier; every downstream flag
   remains false.
9. **Numerical agreement could be caused by importing the primary script.**
   Status: DISMISSED.  The independent lane imports only the independent
   R-372 helper and has a distinct source hash.

## Next gate

Construct a first-Liouvillian-variation form bound with explicit eigenvector
rotation control for the local polynomial core.  Only after that can the
Matsubara budget be connected to a uniform resolvent/locality estimate.
