# Q3LOCK finite-volume Feynman--Kac crosswalk

**Status:** T0 source-scope and sign audit; no claim-card promotion  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782, with the primary
Kozitsky--Pasurek source crosswalk  
**PDF:** deferred until mathematical transcription and independent review are
complete

## 1. Purpose

The Q3LOCK proof plan previously referred to a “standard Feynman--Kac/Trotter
identification”.  That phrase hides two different assertions:

1. the finite-volume quantum Gibbs state is represented by a continuous
   periodic-loop measure; and
2. the particular time-grid Gaussian laws used for the FKG and FSS arguments
   converge to that loop measure.

The first assertion is a direct source-scope import from Kozitsky--Pasurek
(KP), while the second is a Q3LOCK-specific Gaussian covariance, tightness and
weighted weak-limit argument.  This note records the exact mapping and keeps
the two obligations separate.

## 2. KP finite-volume statement and exact Q3LOCK mapping

KP defines the finite-volume Hamiltonian as a sum of harmonic oscillators plus
continuous local potentials and a symmetric pair interaction.  Under their
Assumption (A), the local Hamiltonian is self-adjoint, lower bounded, has
discrete spectrum, and has finite heat trace.  Their periodic harmonic
reference is the Ornstein--Uhlenbeck loop law with covariance operator

```text
A = -m d^2/dtau^2 + a,     m>0, a>0.
```

The finite-volume Euclidean law is given by the Feynman--Kac Gibbs
modification

```text
mu_Lambda(domega)
  = exp[-I_Lambda(omega)] chi_Lambda(domega) / Z_Lambda,
```

where `chi_Lambda` is the product periodic OU law and `I_Lambda` contains the
local potential integrals and the pair interaction inner products.  KP also
identifies ordered bounded multiplication correlators with the corresponding
loop evaluations.  These are the only source-level facts imported here.

For Q3LOCK, fix a finite spatial box `Lambda`, `nu=8`, and

```text
m = chi / hbar^2 > 0.
```

Choose a positive harmonic split `a>0`.  For an undirected nearest-neighbour
edge `{y,z}`, set the KP symmetric coupling `J_yz=J_zy=c`.  Then

```text
-1/2 sum_(y,z) J_yz (omega_y,omega_z)_L2
 = -c sum_{<yz>} (omega_y,omega_z)_L2.
```

Adding the onsite contribution `3c/2 |omega_y|^2` at each cubic site gives

```text
c/2 sum_<yz> |omega_y-omega_z|^2
 = 3c/2 sum_y |omega_y|^2
   - c sum_<yz> (omega_y,omega_z)_L2.
```

Thus the Q3LOCK spatial bond is exactly the KP pair interaction after moving
the positive onsite part into the local potential.  The remaining local
potential is the original `r|q|^2/2`, the onsite quartics, the Q3 locking
quartics, the source `-h u dot q`, the `3c/2 |q|^2` term, and the subtraction
of `a|q|^2/2` associated with the harmonic reference.

## 3. Verification of KP potential hypotheses

On a compact source interval `|h|<=h0`, the Q3 locking term is nonnegative and
the component quartic obeys

```text
sum_e q_e^4 >= |q|^4 / 8.
```

The negative quadratic coefficient and the linear source are absorbed by
Young inequalities.  Therefore there are constants `A>0` and `C<infinity`,
uniform in `|h|<=h0` and in the finite box, such that

```text
V_(h,a)(q) >= A |q|^4 - C.
```

For the upper side of KP's assumption, every Q3 edge satisfies

```text
(q_e-q_f)^2(q_e^2+q_f^2) <= 4(q_e^4+q_f^4),
```

and the cubic internal graph has degree three.  Hence one continuous quartic
upper function works uniformly on the source interval.  The finite-range
coupling has `Jhat_0=6c`.  These checks match the KP vector dimension,
positive mass, continuity, superquadratic coercivity, and interaction-sum
hypotheses.  They do not import any rotation-invariant phase theorem.

## 4. Heat-kernel/grid convention audit

The Q3LOCK time grid has `epsilon=beta/N` and reference action

```text
m/(2 epsilon) sum_(y,k) |x_(y,k+1)-x_(y,k)|^2
 + a epsilon/2 sum_(y,k) |x_(y,k)|^2.
```

The free one-step kinetic factor is the heat kernel of
`-(2m)^(-1) Delta` at time `epsilon`, up to its usual normalization.  The
onsite harmonic term is inserted with the Riemann factor `epsilon`; the
residual local and spatial terms are inserted in the same way.  For every
fixed finite `Lambda`, the interpolated Gaussian covariance converges to the
periodic Green kernel of `A`, as proved in the separate covariance and
tightness audits.  The weighted weak-limit argument then converges the
normalized grid laws to the KP loop density.

This is a convergence of probability measures and bounded continuous
functionals.  It is not a claim that the finite-grid measures converge in
total variation, nor is it a replacement for the source theorem's operator
semigroup statement.

## 5. What is imported and what is proved locally

| Item | Authority | Status in Q3LOCK paper |
|---|---|---|
| Finite-volume self-adjoint lower-bounded Hamiltonian and finite heat trace | KP finite-volume Assumption (A) consequence | Import after the explicit potential crosswalk |
| Periodic OU reference law and covariance operator | KP harmonic construction | Import after `m=chi/hbar^2`, `a>0` check |
| Feynman--Kac Gibbs modification and bounded multiplication correlators | KP finite-volume path representation | Import after sign and factor check |
| Discrete covariance convergence and interpolation tightness | Q3LOCK audits | Paper-local lemma; independent audit required |
| Uniform-on-compact Riemann sums, tail control and normalizer division | Q3LOCK weighted weak-limit audit | Paper-local lemma; independent audit required |
| FKG association and finite-grid FSS transfer | Q3LOCK proofs | Paper-local; not supplied by KP |

In particular, the KP source does not prove the Q3LOCK nonradial continuous-loop
FKG statement or the Q3LOCK Hilbert-valued infrared inequality.  It only
provides the exact finite-volume loop representation after the hypotheses are
matched.

## 6. Sign, factor and boundary checks

* The source term is `-h sum_y u dot q_y` in the Hamiltonian and therefore
  `+h X_L` in the exponential moment `exp(h X_L)`.
* The pair interaction is counted with symmetric `J_yz` in KP, so the factor
  `-1/2 sum_(y,z)` produces exactly one `-c` term per undirected spatial edge.
* The positive onsite `3c/2` term is part of the local potential and must not
  be counted a second time in the pair interaction.
* The harmonic split parameter `a` is an auxiliary reference choice.  The
  residual potential and the normalized loop law are independent of `a` once
  the terms are recombined; all estimates must retain a fixed `a>0`.
* KP's representation is fixed finite volume and fixed source.  Source removal,
  spatial thermodynamic limits, strict cusp, and DLR multiplicity remain the
  separate Q3LOCK obligations in EXP-000781/782.

## 7. Remaining independent-audit items

1. Verify the bibliography version and equation/theorem numbering of the KP
   source used in the manuscript.
2. Recompute the edge-count and onsite `3c/2` factor for both periodic and open
   finite boxes used by the pressure argument.
3. Check that the chosen interpolation and compact cutoff make every test
   functional continuous in the exact topology used by KP.
4. Verify the source-uniform quartic moment bound used to remove clips from
   unbounded coordinate products.
5. Confirm that no KP result requiring one-dimensional oscillations,
   ferromagnetic scalar order, or rotational invariance is imported into the
   eight-component nonradial Q3LOCK theorem.

Until these checks are signed by an independent reviewer, P-06 and P-09 retain
their `PROOF TEXT AND EXTERNAL AUDIT REQUIRED` status.

## 8. Nonclaims and publication boundary

This crosswalk does not register a claim, change a tier, create a P2
manuscript, or generate a PDF.  It proves no strict cusp, phase coexistence,
real-time dynamics, KMS state, ground state, gap, continuum limit, physical
vacuum statement, or cosmological interpretation.  PDF compilation, rendering
and visual review remain final-stage actions after the content and independent
audits are complete.

## 9. Primary source

Y. Kozitsky and T. Pasurek, *Euclidean Gibbs States of Interacting Quantum
Anharmonic Oscillators*, arXiv:math-ph/0609045, especially the finite-volume
Hamiltonian and potential assumptions, the periodic harmonic reference, and
the Feynman--Kac representation in Section 2.
