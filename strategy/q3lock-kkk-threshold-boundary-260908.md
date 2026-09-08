# Q3LOCK KKK phase-threshold boundary (EXP-001679)

## Scope

This is a bounded primary-source recheck for the literature and novelty
boundary of the Q3LOCK paper.  It is comparison-only: it does not import a
phase theorem, promote R-497, establish absence or priority, or generate a
PDF.  The paper remains T0, `claim_bearing=false`, and in content review.

## Question

Does the closest Kargol--Kondratiev--Kozitsky phase-threshold result already
cover the positive-lambda, non-radial eight-component Q3LOCK onsite
polynomial, or are its hypotheses restricted to radial/rotation-invariant or
scalar models?

## Primary-source recheck

The primary record is Kargol--Kondratiev--Kozitsky, *Phase Transitions and
Quantum Stabilization in Quantum Anharmonic Crystals*, arXiv:0710.2303v1,
DOI [10.48550/arXiv.0710.2303](https://doi.org/10.48550/arXiv.0710.2303),
with the source PDF at
<https://arxiv.org/pdf/0710.2303v1>.  The checked source advertises a
translation- and rotation-invariant vector phase route in Section 3.3,
including Theorem 3.20 and the threshold equations (3.71)--(3.75).  Its
potential displayed in (3.57) is radial, of the form
`-b |u|^2 + b_2 |u|^4`; the vector argument uses the corresponding internal
rotation invariance.  The same source treats asymmetric onsite potentials in
its scalar route (Sections 3.4--3.5), not as a non-radial vector theorem.

The primary record for the scalar asymmetric comparator is Kargol--Kozitsky,
*A Phase Transition in a Quantum Crystal with Asymmetric Potentials*,
arXiv:math-ph/0611017v1, DOI
[10.1007/s11005-007-0140-8](https://doi.org/10.1007/s11005-007-0140-8),
<https://arxiv.org/pdf/math-ph/0611017v1>.  Its abstract and Theorem 1.4
concern a one-component scalar crystal with a continuous general/asymmetric
onsite potential and a polarization discontinuity at a nonzero field under
large-mass/large-interaction conditions.

## Q3LOCK comparison

Q3LOCK has eight components, the componentwise quartic term, and the positive
Q3 locking polynomial
`lambda/4 (x-y)^2 (x^2+y^2)`.  This onsite block is not a function of
`|q|^2` alone, so the internal `O(8)` rotation hypothesis in the KKK vector
route fails.  Flattening the eight components into a scalar route does not
preserve the scalar theorem: the Q3 term becomes additional non-bilinear
quartic pair interactions.  Therefore the checked KKK results are exact
comparators for the threshold shape and standard inequalities, but neither is
an analytic import for the Q3LOCK cusp or parity-related DLR pair.

## Finding and boundary

The closest checked primary results narrow the direct-import boundary but do
not decide novelty.  The Q3LOCK manuscript must continue to prove its own
continuous-loop FKG, collective lower bound, infrared subtraction, cusp, and
source-selected DLR construction.  A specialist must still check later
anisotropic continuous-oscillator literature before content/hash freeze.
The result does not alter A1--A23 dispositions; in particular A20 and the
literature gate remain OPEN.

## Reproducibility

The source locators and comparison role are recorded in
`publish/papers/q3lock-phase-coexistence/literature-crosswalk.md` and the
current source ledger.  No manuscript PDF is created at this checkpoint.
