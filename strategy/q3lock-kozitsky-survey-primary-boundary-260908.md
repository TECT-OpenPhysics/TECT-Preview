# Q3LOCK primary survey boundary: scalar theorem versus the R^8 model

**Date:** 2026-09-08  
**Exploration:** EXP-001667  
**Task:** T-054  
**Status:** T0 literature applicability audit; comparison-only; PDF deferred

## Question

Does the accessible primary Kozitsky overview already contain a finite-
temperature theorem that directly covers the positive-lambda, non-radial
eight-component Q3LOCK model, or does it only summarize scalar/radial
quantum-crystal results?

## Primary sources checked

1. Y. Kozitsky, *Equilibrium States, Phase Transitions and Dynamics in
   Quantum Anharmonic Crystals*, arXiv:1806.08264v1, especially equations
   (1.1)--(1.5), the path-measure construction (1.11)--(1.15), and Theorem
   2.1.  The source defines one scalar displacement `q` per site, the local
   Hamiltonian with `p^2/(2m)+a q^2/2+V(q)`, and then specializes to
   `V(q)=-b_1 q^2+b_2 q^4` with `b_1,b_2>0`.  Its Theorem 2.1 assumes
   `d>=3` and a scalar sufficient inequality involving the well parameter
   `upsilon`, the scalar interaction intensity `J_b`, mass `m`, and the
   lattice constant `theta(d)`; it concludes multiplicity of thermodynamic
   phases for `beta>beta_*`.
2. S. Albeverio, Y. Kozitsky, Y. Kondratiev and M. Roeckner, *Phase
   transitions and quantum effects in anharmonic crystals*,
   arXiv:1204.6279v1, especially the vector/scalar split around its general
   vector framework and the displayed condition (90).  The overview
   identifies general-vector Euclidean-DLR infrastructure but the explicit
   low-temperature phase inequalities used in the checked sections reduce to
   radial/vector or scalar families; it does not state the Q3LOCK non-radial
   endpoint polynomial theorem.
3. A. Kargol and Y. Kozitsky, *A Phase Transition in a Quantum Crystal with
   Asymmetric Potentials*, arXiv:math-ph/0611017v1, Theorem 1.4, remains the
   closest directly checked asymmetric result.  It is one-component scalar,
   with a scalar nearest-neighbour coupling and a possibly nonzero field
   discontinuity.

The primary records are publicly accessible at:

- <https://arxiv.org/pdf/1806.08264v1>
- <https://arxiv.org/pdf/1204.6279v1>
- <https://arxiv.org/pdf/math-ph/0611017v1>

## Hypothesis comparison

| Item | Checked primary survey/theorem | Q3LOCK manuscript |
|---|---|---|
| Site variable | `q_l in R` in the checked phase theorem | `q_y in R^8` |
| Onsite structure | scalar double-well quartic `-b_1 q^2+b_2 q^4` | positive-lambda Q3 endpoint polynomial plus scalar quartic, non-radial on `R^8` |
| Spatial interaction | scalar bilinear nearest-neighbour coupling `J q_l q_l'` | positive difference form on eight-component vectors |
| Phase mechanism | imported scalar/radial infrared and Euclidean-Gibbs result | continuous-loop FKG, non-radial Hilbert-valued reflection positivity, collective lower bound, source cusp and selected DLR tangent states |
| Conclusion | phase multiplicity or polarization discontinuity in the checked scalar/radial model | conditional strict collective-source cusp and a parity-related tempered DLR pair under `r<0`, `A_0>I_3`, `beta>beta_*` |

The dimension condition `d>=3` and the broad path-measure/DLR language are not
enough to transfer Theorem 2.1.  The site dimension, onsite symmetry, spatial
coupling, order parameter and lower-bound mechanism all differ.  Setting
`lambda=0` or restricting the vectors to the collective line changes the
finite-volume law and is not a permitted reduction in this paper.

## Disposition

The checked overview is a useful primary citation for Euclidean Gibbs/DLR
context and for the scalar/radial comparison boundary.  It is **not** a
direct analytic import for the non-radial positive-lambda `R^8` Q3LOCK phase
route.  This result narrows one likely misreading in the literature packet but
does not establish that no other anisotropic continuous-oscillator theorem
exists, does not establish novelty or priority, and does not sign any A1--A23
proof row.

The specialist reviewer must still inspect the Schneider--Beck--Stoll full
text if access is obtained and search for any later anisotropic continuous-
oscillator or relative-form theorem with the same finite-beta DLR and
source-cusp quantifiers.  Until that review is signed, the manuscript's
literature gate remains open.

## Adversarial checks

| objection | disposition | reason |
|---|---|---|
| “Quantum anharmonic crystal” plus `d>=3` automatically covers Q3LOCK. | **UPHELD AS FALSE** | The checked theorem is scalar and radial in its explicit model; its site variable and interaction differ. |
| The scalar theorem can be imported after projecting to `u=(1,...,1)/sqrt(8)`. | **UPHELD AS FALSE** | Projection changes the finite-volume measure and discards transverse Q3 degrees of freedom. |
| The overview proves absence of any broader anisotropic theorem. | **UPHELD AS FALSE** | It is a bounded source check, not an exhaustive literature search. |
| The comparison establishes Q3LOCK novelty or priority. | **DISMISSED** | The note records only an applicability boundary and explicitly leaves specialist review open. |

## Boundary

No theorem tier, claim card, R-497 scope, Sector A--F status, publication
status, submission status or PDF status changes. The first PDF remains
deferred until mathematical and literature review, content freeze and clean
replay are complete.

