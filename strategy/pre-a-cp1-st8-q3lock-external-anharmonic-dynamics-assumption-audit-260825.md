# External anharmonic-dynamics assumption audit

**Status:** reference-only QFT interface audit; no claim or tier change

**Date:** 2026-08-25

## Decision

The external infinite-volume oscillator literature supplies a legitimate QFT
route for constructing a common real-time dynamics, but it does not close the
exact Q3LOCK common-alpha gate by direct import. The exact Q3 model must first
be placed in a resolvent-algebra or a regularized polynomial interaction
framework and its uniform estimates must be proved for the declared
unbounded onsite and intersite terms.

## Audited authorities

1. Nachtergaele, Schlein, Sims, Starr and Zagrebnov, *On the Existence of the
   Dynamics for Anharmonic Quantum Oscillator Systems*, arXiv:0909.2249,
   especially Theorem 5.1 and the preceding Theorem 4.3. The paper constructs
   a thermodynamic-limit W-star dynamics from finite-volume dynamics and
   Lieb--Robinson bounds. Its perturbation class is described through Weyl
   integrals with finite complex measures and finite first/pair moments with
   spatial decay. Under those hypotheses finite-volume Weyl evolutions converge
   in norm and the limit is weakly continuous.

2. Buchholz, *The resolvent algebra for oscillating lattice systems: Dynamics,
   ground and equilibrium states*, arXiv:1605.05259. The resolvent-algebra
   framework gives a global automorphism dynamics and KMS/ground-state
   constructions for bounded nearest-neighbor interactions, and discusses
   regularization routes for singular or non-harmonic interactions. The stated
   bounded-interaction theorem is not an exact Q3 polynomial theorem.

## Exact Q3 comparison

The registered Q3LOCK Hamiltonian has a confining quartic onsite polynomial
and an unbounded bilinear spatial coupling `q_y dot q_z`, in addition to the
kinetic term. These are multiplication operators with polynomial growth, not
finite-variation Weyl-integral perturbations with the cited moment contract.
The repository currently has no source-, volume-, beta-, orientation- and
regularization-uniform estimate that would turn a smooth polynomial
regularization into the hypotheses of either cited theorem. Therefore the
external results are admissible references and route constraints, but not
proof evidence for the exact Q3 common alpha.

This is an applicability boundary, not a nonexistence theorem. The unresolved
successor is the registered
`PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-COMMON-ALPHA-CLOSURE`
gate.

## Required bridge before QFT promotion

The live route must establish, in one fixed carrier and for both phase
orientations:

1. self-adjointness and a lower bound for the finite Q3 Hamiltonians on a
   common polynomial/resolvent core;
2. a regularized interaction family whose generator acts inside the chosen
   resolvent or energy-damped algebra;
3. a Lieb--Robinson or Duhamel estimate uniform in volume, source, beta,
   orientation and regularization;
4. full-versus-regularized Cauchy convergence for local observables and the
   first modular derivative;
5. exhaustion independence, products, star, group law and strong continuity;
6. only after these steps, Hamiltonian-to-OS/KMS identification and the
   beta-independent common algebra.

The present audit closes none of these items. It narrows the proof target from
an attempted direct import to a precise regularization-removal/common-core
problem.

## Adversarial review

- **Weyl-integral mismatch:** UPHELD. Polynomial multipliers are not silently
  treated as finite-variation Weyl measures.
- **Bounded-versus-unbounded interaction:** UPHELD. Buchholz's main lattice
  theorem is not cited as an exact unbounded Q3 result.
- **Representation change:** UPHELD. A resolvent-algebra limit is not assumed
  to equal the existing configuration OS mixture without an explicit bridge.
- **Uniformity:** UPHELD. Finite-volume or fixed-cutoff estimates cannot be
  promoted to all-exhaustion or cutoff-uniform bounds.
- **QFT promotion:** UPHELD. No common alpha, KMS/OS identification, GNS gap,
  continuum limit, C6, Sector A or Pre-A closure follows from this audit.

## Scope

This is a T0 claim-nonbearing source-applicability and route-refinement note.
It preserves the phasewise OS/KMS results and the finite Q3 stress packages,
while leaving the thermodynamic common dynamics and every downstream gate
open.
