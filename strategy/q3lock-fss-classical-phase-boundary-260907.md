# Q3LOCK FSS classical phase-theorem boundary audit

Date: 2026-09-07
Exploration: EXP-001645
Task: T-054
Status: T0, claim_bearing=false, INTERNAL_REVIEW_ONLY
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497
PDF status: deferred

## Purpose

This note records a primary-source boundary check that is easy to miss when
reading the Froehlich--Simon--Spencer (FSS) paper. The Q3LOCK manuscript
uses only the finite-vector Gaussian-domination input in Section 2, Theorem
2.1. The same source also contains a classical phase-transition theorem in
Section 3. That theorem is a comparison result, not an unlisted premise of
the Q3LOCK quantum-loop argument.

## Primary source

The source is J. Froehlich, B. Simon, and T. Spencer,
*Infrared Bounds, Phase Transitions and Continuous Symmetry Breaking*,
Communications in Mathematical Physics 50 (1976), 79--95,
https://math.caltech.edu/SimonPapers/65.pdf.

The source's Section 3, Theorem 3.3 states, in the classical finite-dimensional
lattice-gas setting, that an a priori measure invariant under
sigma -> -sigma has a phase transition for sufficiently large ferromagnetic
coupling in dimension at least three, in the sense that a periodic state is
not ergodic. The theorem is obtained from the preceding classical
finite-volume infrared argument and is not a theorem about quantum
Hamiltonians, imaginary-time loop limits, or tempered DLR specifications.

## Exact boundary for Q3LOCK

At each fixed time mesh N, Q3LOCK can be represented as a classical
finite-dimensional vector-spin model, and at zero source its finite prior is
even. This observation does not license a direct import of FSS Theorem 3.3:

1. the spin dimension and the one-site prior change with N;
2. the theorem supplies no uniform N-to-infinity estimate for the
   continuous-loop passage;
3. it does not provide the source-window DLR compactness and tangent-state
   construction used by the manuscript;
4. nonergodicity of a classical periodic state is not the displayed strict
   source cusp plus two parity-related tempered Euclidean DLR states.

The Q3LOCK proof therefore retains Section 2, Theorem 2.1 only as a
fixed-mesh upper bound, followed by its own loop/UI, Duhamel, infrared
subtraction, collective lower bound, pressure endpoint, and DLR passages.
This is a source-scope firewall, not a novelty certificate.

## Adversarial checks

* Do not cite the classical Theorem 3.3 as if it were an infinite-dimensional
  Euclidean-DLR theorem.
* Do not turn a theorem applied separately at each N into a uniform continuum
  statement.
* Do not identify periodic-state nonergodicity with the bounded witness and
  source-selected DLR pair in the Q3LOCK manuscript.
* Do not convert this boundary check into a world-first or priority claim.
* Keep A1--A23, independent mathematical review, specialist literature review,
  claim-lineage review, final freeze, clean replay, and PDF generation open.

## Disposition

The result is a strengthened non-subsumption boundary for the literature
crosswalk: FSS Section 3, Theorem 3.3 is comparison-only and does not replace
any Q3LOCK loop/DLR block. The finite source reading is internal provenance,
not signed external acceptance. No theorem tier, claim status, TECT sector,
or PDF status changes.