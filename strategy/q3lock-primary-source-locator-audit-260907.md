# Q3LOCK primary-source locator audit

Date: 2026-09-07. Exploration: EXP-001655. Task: T-054.
Status: T0, claim_bearing=false, primary-source locator and hypothesis audit.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
PDF status: deferred.

## Question

Do the current primary-source locators and import boundaries for Simon's
finite Feynman--Kac formula, Kozitsky--Pasurek's general-vector Euclidean DLR
theorem, Froehlich--Simon--Spencer's finite-mesh Gaussian domination, and the
Kargol--Kondratiev--Kozitsky Falk--Bruch/Griffiths comparators match the roles
assigned to them in the Q3LOCK manuscript?

## Sources checked

* B. Simon, [arXiv:math-ph/9907022v1](https://arxiv.org/pdf/math-ph/9907022v1),
  Theorem 1.1 and equations (1.1)--(1.3): continuous finite-dimensional
  potentials bounded below and the Brownian-bridge Feynman--Kac kernel.
* Y. Kozitsky and T. Pasurek,
  [arXiv:math-ph/0609045v1](https://arxiv.org/pdf/math-ph/0609045v1),
  Assumptions (A)/(B), equations (2.36)--(2.49), Lemma 2.8, and Theorems
  3.1--3.2: general-vector Euclidean Gibbs existence/compactness, the
  projective tempered topology, Feller kernels, and common exponential
  moments. The scalar attractive phase results are not used.
* J. Froehlich, B. Simon and T. Spencer,
  [Commun. Math. Phys. 50 (1976), 79--95](https://math.caltech.edu/SimonPapers/65.pdf),
  Section 2, Theorem 2.1: finite torus spins with a fixed finite component
  dimension, a single-site prior having all quadratic exponential moments,
  and a Gaussian-domination bound for arbitrary finite source fields. The
  theorem is not used as a loop, thermodynamic, or DLR theorem.
* T. Kargol, Y. Kondratiev and T. Kozitsky,
  [arXiv:0710.2303v1](https://arxiv.org/pdf/0710.2303v1), Proposition 3.9,
  Proposition 3.18 and equations (3.21)--(3.24), (3.65)--(3.68): endpoint
  Griffiths and Falk--Bruch comparator normalizations.

## Crosswalk finding

The source statements support the roles currently assigned in the manuscript.
Simon Theorem 1.1 is the bounded-below finite-dimensional formula; the weaker
growth condition associated with Simon's Theorem 1.2 is not silently imported.
The KP general theorem is stated for vector oscillators and its projective
tempered space is explicitly Polish; the Q3LOCK map keeps the physical
quadratic coefficient `r` distinct from the KP growth exponent and places the
Q3 locking polynomial in the onsite potential. FSS Section 2 accepts a fixed
finite vector dimension and a common prior with all quadratic exponential
moments; the Q3LOCK edge-source map is therefore a finite-mesh interface to be
checked in the manuscript, not a radial or scalar import. KKK's Proposition
3.18 has the same `b >= g f(c/(4g))` normalization printed in the manuscript,
while Proposition 3.9 supplies only the comparator for the endpoint moment
bound; the manuscript proves its own squared-tail specialization.

No locator mismatch or direct theorem overclaim was found in this bounded
recheck. The exact mass rescaling, harmonic absolute normalization, FSS
edge-divergence map, and the form-domain passage remain manuscript arguments
and still require signed mathematical review. The source PDFs and hashes must
be recaptured at the final content freeze; this note does not freeze them.

## Disposition

**INCONCLUSIVE INTERNAL PRIMARY-SOURCE AUDIT; SIGNED APPLICABILITY REVIEW
OPEN.** The audit strengthens the source-role record but changes no theorem
tier, claim status, novelty statement, pressure/cusp conclusion, DLR status,
or PDF policy. No scalar/radial result is imported into the non-radial
positive-lambda Q3LOCK model.

## Reproduction boundary

The web locators above are provenance evidence for the human reviewer. The
repository finite diagnostics and replay checkpoints remain non-certifying;
they do not replace a signed proof audit. No paper PDF was generated.
