# Relative-modular cocycle and resolvent Cook bridge

This certificate records EXP-001227 as a claim-nonbearing route design for
the unresolved Q3LOCK common-dynamics gate.  It is deliberately different
from the finite two-scale shell in R-384 and from the positive folded-Renyi
route in EXP-001203.

## New perspective

For nested finite Hamiltonians write `H_prime = H + B`, where `B` contains
only the interaction terms added at the boundary.  Instead of expanding every
onsite/bond split history and estimating its norm separately, define the
relative unitary cocycle

`U_prime,H(t) = exp(i t H_prime) exp(-i t H)`.

On the common form/resolvent core, the exact finite identities are

`alpha_prime_t(A) = U_prime,H(t) alpha_t(A) U_prime,H(t)^*`,

`dU_prime,H(t)/dt = i alpha_prime_t(B) U_prime,H(t)`.

The proposal is to apply the phase-local conditional expectation to the
commutator of `B` with a local resolvent before taking a two-sided fixed-beta
GNS norm.  The bulk terms then cancel before the estimate.  The target is a
shell coefficient `b_A(r)` for the boundary cocycle commutator and its modular
derivative.  If the coefficient is uniformly summable in the shell distance,
the Cook/Duhamel integral gives a two-sided strong-star Cauchy estimate for
the finite-volume evolutions on the resolvent core.  The resolvent identity
then carries products and inverses without requiring a raw Weyl point-norm
limit.

This is a change in the order of operations: relative-cocycle resummation,
local conditioning, and state-weighted estimation precede the thermodynamic
limit.  It does not assume that the real-time folded contour is positive and
does not use a global energy window.

## Required lemma and stop rule

The first decisive lemma is a phase-local BKM boundary estimate with constants
uniform in source, cutoff, volume and exhaustion shape.  The second is the
`l1` shell summability of those coefficients in both orientations.  A finite
table, a static Euclidean tail, or a small direct `D` value is not a proof of
either premise.  Failure of summability in one orientation retires this route
only; it does not imply nonexistence of Q3LOCK dynamics.

## QFT interface

The intended chain is

`OS phase mixture -> standard form -> relative modular cocycle -> resolvent
Cook limit -> common alpha -> Hamiltonian/KMS identification -> sector gap`.

The OS mixture and phasewise KMS constructions already registered in the
repository are inputs, not outputs of this certificate.  Spatial embeddings,
the exact Q3 boundary estimate, direct `D,delta-D` convergence, a common
Hamiltonian-derived automorphism, the KMS/GNS gap, continuum, C6, Sector-A and
Pre-A all remain open.

## Adversarial review

1. The ordering of the cocycle and its adjoint must be differentiated
   explicitly; a commuting perturbation shortcut is invalid.
2. `B` is an unbounded quartic boundary polynomial, so bounded-perturbation
   theorems cannot be imported without a declared form/resolvent domain.
3. Exact bulk cancellation requires the same local Hamiltonian convention and
   a verified embedding halo at every exhaustion level.
4. Two-sided GNS convergence is not point-norm convergence and does not by
   itself produce a representation-independent C-star action.
5. Shell summability must be proved, not inferred from the finite R-384
   profiles or from a static Gibbs tail.
6. Even a successful Cook limit would still need the Hamiltonian-to-OS/KMS
   quotient and independent gap/continuum interfaces.

No new result, negative result, tier change, or proof-note PDF is issued by
this route-design checkpoint.
