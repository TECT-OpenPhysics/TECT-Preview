# Q3LOCK primary-source scope audit: KP vector DLR versus scalar phase route

Date: 2026-09-08. Exploration: EXP-001673. Task: T-054.
Status: T0 primary-source applicability boundary; claim_bearing=false; PDF deferred.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.

## Source and exact locators

Primary source: Y. Kozitsky and T. Pasurek, *Euclidean Gibbs Measures of
Interacting Quantum Anharmonic Oscillators*, arXiv:math-ph/0609045v1,
https://arxiv.org/pdf/math-ph/0609045v1.

The abstract and the introduction (PDF pages 1--3) state the split explicitly:
the general model has `nu`-dimensional oscillators and yields non-emptiness,
compactness, moment/support properties, and high-temperature uniqueness; the
second group assumes `nu=1` and nonnegative attractive interaction, where FKG,
pressure and the low-temperature phase-transition theorem are developed.

Assumption (A), PDF page 5, equations (2.5)--(2.8), permits a general
`R^nu` onsite potential satisfying continuity, a lower polynomial bound,
an upper envelope and a finite absolute interaction row sum. The Q3LOCK
potential can satisfy this infrastructure condition through the displayed
quartic envelope, with `nu=8`, but the source does not thereby supply its
non-radial phase theorem.

The source's model equations (2.1)--(2.7) use a bilinear dot-product spatial
interaction and a site potential. Q3LOCK's positive-lambda internal `Q_3`
locking term is an additional non-radial onsite polynomial. It is compatible
with the general-vector stability interface only after the manuscript's own
envelope and continuity checks; it is not covered by the source's scalar FKG
phase route by notation alone.

The introduction (PDF pages 5--6) also explains that a global algebraic KMS
dynamics need not exist for the unbounded model and that the Euclidean path
measure is the chosen equilibrium description. This supports the manuscript's
explicit nonclaims about a common infinite-volume real-time dynamics.

## Q3LOCK disposition

| Source component | Q3LOCK use | Disposition |
|---|---|---|
| General Assumption (A)/(B) and Theorem 3.1 infrastructure | Fixed-source DLR existence/compactness crosswalk | Conditional analytic input; signed review remains open |
| `nu=1`, `J>=0` FKG/maximal-minimal and low-temperature phase route | Scalar comparison only | Does not apply directly to the non-radial `R^8` Q3LOCK model |
| Source model's bilinear spatial interaction | Spatial part of Q3LOCK map | Used only through the displayed finite-mesh and DLR interfaces |
| Source's Euclidean-versus-algebraic-KMS boundary | Scope/nonclaim context | Compatible with the paper's nonclaims; no KMS theorem is imported |

This is a source-level comparison, not an absence, novelty, or priority result.
It does not exclude a different anisotropic continuous-oscillator theorem.
The Schneider--Beck--Stoll full-text item and a specialist disposition remain
open before content freeze.

## Adversarial checks and next gate

1. “General `nu`” is not silently converted into “general vector phase
   transition”: the phase route is recorded as `nu=1` in the primary source.
2. A quartic envelope for Q3LOCK is not treated as a radial potential or as a
   scalar reduction.
3. DLR infrastructure is not conflated with FKG, cusp, or state multiplicity.
4. The KMS discussion is retained as a scope boundary, not as a new physical
   conclusion.

Give this exact locator and disposition to the independent literature reviewer.
Keep A6, A10--A13, A16, R3, R4, R12 and R13 open until signed review.
