# Q3LOCK primary literature audit: vector framework versus scalar phase theorems

Date: 2026-09-07. Exploration: EXP-001631. Task: T-054.
Status: T0 literature-applicability audit, claim_bearing=false, no priority claim.
The sole Q3LOCK research authority remains EXP-000780 -> EXP-000781 ->
EXP-000782 / R-497.  This note is a comparison record, not a new proof
premise and not an external specialist signature.

## Question

The outstanding R4 question is whether an existing Euclidean quantum-crystal
or continuous-spin theorem already covers the untruncated positive-lambda
Q3LOCK model: a three-dimensional lattice, an eight-dimensional continuous
onsite oscillator, a non-radial onsite polynomial, nearest-neighbour
ferromagnetic coupling, and the stated source/cusp and two-DLR-state
conclusion.  The search must distinguish a general-vector DLR framework from
a phase theorem whose extra radial, scalar, or symmetry assumptions fail.

## Kargol--Kozitsky asymmetric-potential theorem

Primary source: Kargol and Kozitsky, *A Phase Transition in a Quantum Crystal
with Asymmetric Potentials*, arXiv:math-ph/0611017v1,
https://arxiv.org/html/math-ph/0611017v1.

The paper's abstract says that the anharmonic potential may be of general type
and need not have symmetry, and that a discontinuity is proved in dimension
at least three for sufficiently large mass and interaction.  Its displayed
model, however, makes the displacement explicitly one-dimensional:

* equations (1)--(5), HTML lines 45--64, use (q_\ell\in\mathbb R), a
  scalar product (q_\ell q_{\ell'}), and a scalar (V_0:\mathbb R\to\mathbb R);
* the lower bound is (A_V x^{2r}+B_V\le V_0(x)), again scalar;
* Theorem 1.4, HTML lines 107--109, gives a first-order pressure/polarization
  discontinuity for that scalar model when (d\ge3), with sufficiently large
  mass and coupling.

Therefore this is a close methodological comparator for the source-pressure,
infrared, and discontinuity route, but it is not a direct theorem for the
Q3LOCK (\mathbb R^8) non-radial onsite interaction.  It does not justify a
scalar reduction of the Q3LOCK (Q_3)-locked quartic.

## Kargol--Kondratiev--Kozitsky vector framework

Primary source: Kargol, Kondratiev and Kozitsky, *Phase Transitions and
Quantum Stabilization in Quantum Anharmonic Crystals*, arXiv:0710.2303v1,
https://arxiv.org/html/0710.2303v1.

The paper does contain a general vector Euclidean-oscillator setup:

* equations (1.1)--(1.4), HTML lines 90--100, allow (q_\ell\in\mathbb R^\nu)
  and (m=m_{\rm ph}/\hbar^2);
* equations (2.1)--(2.3), HTML lines 126--136, allow continuous
  (V_\ell:\mathbb R^\nu\to\mathbb R) with quartic-or-higher coercivity,
  ferromagnetic interaction, and vector source;
* the Euclidean Gibbs/DLR and compactness machinery is consequently a genuine
  general-vector comparator, subject to the exact hypothesis map already
  recorded in the Q3LOCK KP audit.

The phase conclusions in that source use additional restrictions:

* the rotation-invariant vector phase subsection begins at HTML line 1001 and
  uses the radial quartic (V(u)=-b|u|^2+b_2|u|^4) at lines 1007--1009;
* Theorem 3.20 (lines 1099--1106) is for that radial quartic and its
  (\vartheta_*) condition;
* Theorem 3.21 (lines 1130--1132) explicitly assumes rotation invariance;
* Theorem 3.25 (lines 1248--1250) is explicitly scalar.

The Q3LOCK onsite polynomial is not (O(8))-invariant: the coordinate
quartics and the (Q_3) edge polynomial select internal directions.  Thus the
general-vector existence framework is relevant, but the listed vector phase
theorems cannot be imported without a new reduction or a theorem covering the
actual non-radial interaction.  The Q3LOCK proof's positive-lambda collective
estimate remains a model-specific candidate, not an established novelty
certificate.

## Continuous-spin Pirogov--Sinai comparator

M. Zahradnik, *Contour Methods and Pirogov Sinai Theory for Continuous Spin
Lattice Models*, mp_arc 99-19, https://web.ma.utexas.edu/mp_arc-bin/mpa?yn=99-19,
develops a classical continuous-spin contour reduction for multiple-well
potentials.  The abstract does not state a quantum oscillator path-space
theorem, a Feynman--Kac source cusp, or a tempered Euclidean DLR result for an
unbounded onsite Hilbert space.  It is therefore a valid discovery lead and a
classical comparison method, but direct applicability to the Q3LOCK quantum
model is not established here.  A specialist must decide whether a separate
quantum extension covers the exact untruncated model.

## Disposition

The primary-source check narrows, but does not close, the novelty boundary:

1. Existing scalar asymmetric-potential results are close in dimension,
   infrared strategy, and pressure discontinuity, but their onsite field is
   one-dimensional.
2. Existing vector quantum-crystal work supplies a general Euclidean-DLR
   framework, while its displayed vector phase theorems impose radial or
   rotation-invariant potentials; its scalar asymmetric theorem is not an
   (\mathbb R^8) theorem.
3. Classical continuous-spin contour methods are not automatically quantum
   Feynman--Kac/DLR results.

No exhaustive literature claim follows.  In particular, this audit does not
exclude an unlocated anisotropic continuous-oscillator theorem or an immediate
corollary.  R4, R12 and R13 remain open; the external handoff must include
this note and request a specialist's exact-covering-theorem decision.

## Nonclaims and next gate

This note does not promote R-497, prove the Q3LOCK phase theorem, establish
priority, or alter the manuscript.  It does not assert extremality, purity,
clustering, KMS dynamics, a ground-state gap, a continuum limit, a physical
vacuum, or any TECT/C6/CP1/Sector-A conclusion.  The next gate is a signed
specialist literature disposition and, separately, an independent mathematics
audit of the load-bearing proof rows.  The paper PDF remains deferred until
all content and hash gates are frozen.
