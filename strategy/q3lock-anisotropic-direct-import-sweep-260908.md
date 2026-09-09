# Q3LOCK anisotropic quantum-crystal direct-import sweep

**Date:** 2026-09-08  
**Exploration:** EXP-001668  
**Task:** T-054  
**Status:** T0 literature applicability audit; comparison-only; PDF deferred

## Question

Does the directly checked primary literature already contain a theorem that
covers the positive-lambda, non-radial eight-component Q3LOCK model, or does
the accessible material stop at general-vector DLR infrastructure and scalar
or radial phase-transition results?

## Primary sources checked

1. Y. Kozitsky and R. Pasurek, *Euclidean Gibbs Measures of Quantum
   Anharmonic Crystals*, arXiv:math-ph/0609045.  The checked result supplies
   general-vector Euclidean Gibbs/DLR existence, compactness and moment
   infrastructure under coercive hypotheses.  It is not a phase-coexistence
   theorem for the positive-lambda non-radial Q3LOCK polynomial.
2. A. Kargol, Y. Kondratiev and Y. Kozitsky, arXiv:0710.2303.  The checked
   discussion separates general-vector constructions from the explicit
   phase-transition arguments.  The directly stated phase mechanisms remain
   scalar or rotation-invariant/radial and therefore do not identify the
   Q3LOCK endpoint model.
3. Y. Kozitsky, *Equilibrium States, Phase Transitions and Dynamics in
   Quantum Anharmonic Crystals*, arXiv:1806.08264v1.  The explicit theorem
   inspected in the overview uses one scalar displacement at each site and a
   scalar double-well quartic.  Its low-temperature condition is a scalar or
   radial comparison boundary, not the non-radial R^8 Q3LOCK polynomial.
4. A. Kargol and Y. Kozitsky, *A Phase Transition in a Quantum Crystal with
   Asymmetric Potentials*, arXiv:math-ph/0611017v1.  Theorem 1.4 gives a
   discontinuous scalar polarization in d>=3 for sufficiently large mass and
   coupling.  The Hamiltonian has a one-dimensional displacement per site and
   a scalar nearest-neighbour coupling; it is the closest checked asymmetric
   comparator, but it is not a vector Q3LOCK theorem.

The source PDFs are publicly accessible at:

- <https://arxiv.org/pdf/math-ph/0609045v1>
- <https://arxiv.org/pdf/0710.2303v1>
- <https://arxiv.org/pdf/1806.08264v1>
- <https://arxiv.org/pdf/math-ph/0611017v1>

## Applicability comparison

| Dimension | Checked direct-import boundary | Q3LOCK manuscript |
|---|---|---|
| Site variable | Scalar for the explicit phase theorem; general-vector only for the DLR infrastructure | `q_y in R^8` |
| Onsite potential | Scalar double-well or radial/vector families in the checked phase arguments | Positive-lambda Q3 endpoint polynomial plus scalar quartic; non-radial on `R^8` |
| Interaction | Scalar bilinear or rotation-invariant/radial forms in the checked phase arguments | Positive difference form on eight-component vectors |
| Order parameter | Scalar polarization or radial/vector observable | Collective source tangent and parity witness |
| Mechanism | Euclidean-DLR compactness, scalar/radial infrared or polarization arguments | Continuous-loop FKG, Hilbert reflection positivity, collective lower bound, strict source cusp and selected DLR tangent states |
| Conclusion | Comparison-model phase multiplicity or scalar polarization discontinuity | Conditional cusp and two parity-related tempered DLR states under the manuscript's explicit sufficient regime |

The common phrases “quantum anharmonic crystal”, “d>=3” and “Euclidean
Gibbs measure” do not identify the same theorem.  The site dimension,
onsite polynomial, interaction, order parameter and lower-bound mechanism all
matter.  Projecting to the collective line or setting `lambda=0` changes the
finite-volume law and is not an allowed reduction of the manuscript's model.

## Disposition

The sweep advances the specialist handoff by fixing the strongest directly
checked comparison boundary: general-vector sources support DLR
infrastructure, while the explicit phase-transition results checked here are
scalar or radial.  No direct theorem import into the non-radial positive-
lambda `R^8` Q3LOCK model is accepted.

This is not an exhaustive absence search and does not establish novelty,
priority or independence from every later anisotropic continuous-oscillator
result.  The Schneider--Beck--Stoll full-text item and any later
Hilbert-valued or relative-form theorem still require a specialist's signed
assessment before content freeze.

## Adversarial checks

| objection | disposition | reason |
|---|---|---|
| “General-vector Euclidean Gibbs existence” already proves Q3LOCK phase coexistence. | **UPHELD AS FALSE** | Existence/compactness is not the strict cusp or multiplicity argument. |
| A scalar asymmetric theorem can be lifted by restricting to the collective line. | **UPHELD AS FALSE** | The restriction changes the finite-volume measure and discards transverse Q3 degrees of freedom. |
| A bounded primary-source sweep proves that no anisotropic theorem exists. | **UPHELD AS FALSE** | The search is bounded and comparison-only, not an exhaustive literature or priority audit. |
| The comparison establishes Q3LOCK novelty or priority. | **DISMISSED** | Those conclusions require the open specialist literature gate and signed review. |

## Boundary

No theorem tier, claim card, R-497 scope, Sector A--F status, publication
status, submission status or PDF status changes.  The first PDF remains
deferred until mathematical and literature review, content/notation freeze,
clean replay and final visual QA are complete.

