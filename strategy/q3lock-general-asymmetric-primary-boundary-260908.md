# Q3LOCK general-asymmetric primary-source boundary

Date: 2026-09-08. Exploration: EXP-001663. Task: T-054.

Status: T0 primary-source literature audit; `claim_bearing=false`.
Authority: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
PDF status: deferred until the manuscript is content-frozen and independently reviewed.

## Question

Does the primary asymmetric quantum-crystal theorem most closely resembling
the Q3LOCK route already cover the eight-component non-radial positive-lambda
model, or does it remain a scalar comparison only?

## Primary source checked

The checked source is A. Kargol and Y. Kozitsky, *A Phase Transition in a
Quantum Crystal with Asymmetric Potentials*, arXiv:math-ph/0611017v1,
https://arxiv.org/abs/math-ph/0611017 and the author-hosted PDF
https://web.ma.utexas.edu/mp_arc/c/06/06-321.pdf.

The source's displayed Hamiltonian uses one real displacement variable
`q_l` at each site of the simple cubic lattice `Z^d`, a positive
nearest-neighbour scalar coupling `J`, and a continuous scalar onsite
potential `V`.  Its Theorem 1.4 states that for every `d >= 3` there are
thresholds `m_*` and `J_*` such that, for `m > m_*` and `J > J_*`, the
thermodynamic polarization is discontinuous at some possibly nonzero field
`h_*`.

## Hypothesis comparison

| Source feature | Primary theorem | Q3LOCK paper | Boundary |
|---|---|---|---|
| Site variable | scalar `q_l in R` | `q_y in R^8` | not the same state space |
| Onsite potential | general continuous scalar potential, possibly asymmetric | even, non-radial Q3 endpoint-weighted polynomial with `lambda > 0` | scalar theorem cannot be imported without a proved reduction |
| Spatial interaction | scalar nearest-neighbour bilinear coupling | vector dot-product coupling after the spatial difference split | related ferromagnetic structure, but not the same local law |
| Phase observable | scalar polarization at some `h_*` | zero-source collective cusp and two parity-related tempered Euclidean DLR states | conclusion and source location differ |
| Euclidean path input | scalar loop route in the cited theorem | continuous `R^8` loops, selected DLR limits, FKG, FSS and source tangent | additional Q3LOCK interfaces are required |

The source therefore supplies a comparison boundary, not a direct theorem
for Q3LOCK.  The fact that the scalar source allows a non-symmetric onsite
potential must not be paraphrased as a theorem for arbitrary finite-dimensional
non-radial vector potentials.

The Kargol--Kondratiev--Kozitsky vector results recorded in the existing
crosswalk are a separate comparison boundary: their relevant vector phase
theorems use rotation-invariant onsite structure, which the Q3 endpoint
polynomial does not have.  The Kozitsky--Pasurek general-vector theorem used
by Q3LOCK supplies fixed-source tempered DLR existence/compactness, not the
phase sign, cusp, or parity-pair conclusion.

## Finding and disposition

The primary source confirms the current scalar/vector firewall and gives an
exact theorem locator for the comparison.  It does not close any Q3LOCK proof
row and does not establish novelty or absence of a broader anisotropic
theorem.  A specialist must still search for, and either exclude or map, any
more general continuous-oscillator theorem before the paper can make a
publication-value or priority statement.

**Disposition: advanced internal literature boundary; direct import rejected
for the stated Q3LOCK model, specialist review still open.**

## Explicit nonclaims

This audit does not certify the Q3LOCK pressure limit, DLR construction,
continuous-loop FKG, infrared estimate, cusp, or DLR multiplicity.  It does
not claim novelty, priority, absence of an applicable theorem, theorem-tier
promotion, TECT sector closure, or a paper PDF.
