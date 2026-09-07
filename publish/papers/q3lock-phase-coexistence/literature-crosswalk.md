# Q3LOCK literature and non-subsumption crosswalk

Status: BOUNDED INTERNAL REVIEW / NO PRIORITY CLAIM / PDF DEFERRED.
The historical source-freeze hashes are in
strategy/q3lock-literature-source-freeze-260905.md and the R-497 manifest.
Their allowed citation scope is not the current import list. The current
list and per-hypothesis dispositions are in imported-source-ledger.md.

## Imported tools and comparison citations

| Primary source | Feature inspected | Use here | Boundary |
|---|---|---|---|
| B. Simon, arXiv:math-ph/9907022v1, [source](https://arxiv.org/pdf/math-ph/9907022v1) | Theorem 1.1 / (1.1)--(1.3), page 2 | Finite-dimensional free-bridge input; mass scaling and harmonic reweighting are explicit | Not Theorem 1.2 or an infinite-volume operator theorem; new source byte freeze remains open |
| Y. Kozitsky and T. Pasurek, Euclidean Gibbs Measures of Interacting Quantum Anharmonic Oscillators, arXiv:math-ph/0609045v1, [source](https://arxiv.org/pdf/math-ph/0609045v1) | Assumptions (A)/(B), Proposition 2.2, Theorem 3.1 | Harmonic Gaussian regularity and general-vector fixed-source DLR existence/compactness | Theorem 3.2 is only a fixed-model scope comparator; no Q3LOCK phase sign or scalar order theorem |
| J. Froehlich, B. Simon, and T. Spencer, CMP 50 (1976), 79--95, [source](https://math.caltech.edu/SimonPapers/65.pdf) | Finite-dimensional ferromagnetic vector infrared inequality using a Poisson edge shift | Nonzero-mode Duhamel upper bound at fixed time mesh | Not an infinite-dimensional loop theorem; no zero-mode lower bound |
| C. Fortuin, P. Kasteleyn, and J. Ginibre, CMP 22 (1971), 89--103, [source](https://math.bme.hu/~balint/oktatas/perkolacio/percolation_papers/fortuin_kasteleyn_ginibre.pdf) | Finite partially ordered association mechanism | Historical antecedent; the actual continuous-loop implication is written and audited separately | No direct citation of a path-space or DLR theorem |
| A. Kargol, Y. Kondratiev, and Y. Kozitsky, Phase Transitions and Quantum Stabilization in Quantum Anharmonic Crystals, arXiv:0710.2303v1, [source](https://arxiv.org/pdf/0710.2303v1) | Proposition 3.9 / (3.23), Proposition 3.18 / (3.65), (3.68) | Comparators for the directly proved squared-tail specialization and finite Falk--Bruch inequality; infinite spectral removal is separate | These standard inequalities are not novelty claims; scalar and rotation-invariant phase theorems require separate hypotheses |

## Closest model comparators

| Source | Exact comparison | Disposition |
|---|---|---|
| A. Kargol and Y. Kozitsky, A Phase Transition in a Quantum Crystal with Asymmetric Potentials, arXiv:math-ph/0611017, [primary record](https://arxiv.org/abs/math-ph/0611017) | Scalar crystal in d>=3; source discontinuity under large mass and coupling | Does not directly supply the non-radial eight-component theorem |
| Kargol--Kondratiev--Kozitsky, same 0710.2303 source, Section 3.3 | Translation- and rotation-invariant vector phase theorem | Full internal rotation invariance is absent from the Q3 polynomial |
| Kargol--Kondratiev--Kozitsky, same source, Sections 3.4--3.5 | Symmetric scalar and asymmetric scalar cases | Component reduction must be proved before these theorems can be premises |

The three malformed bibliography entries in v0.1.0 are corrected against
primary-source records on 2026-09-06 (EXP-001604). This is metadata and
applicability repair, not a complete novelty audit. Peripheral phase-field
references from v0.1.0 have been removed from this comparison because their
relevance and bibliographic accuracy were not established here.

## Focused comparison audit -- 2026-09-07

The original-source checks were KP Assumptions (A)/(B), Proposition 2.2
and Theorem 3.1; FSS Section 2; KKK (3.57), Theorems 3.20--3.22 and
3.25; and Kargol--Kozitsky Theorem 1.4. The current-use ledger supersedes
the broader historical source-freeze lists for deciding what is actually imported.

Two further author-origin survey papers were used for discovery, not as new
proof premises: [1204.6279v1](https://arxiv.org/pdf/1204.6279v1),
printed pages 17--18, Theorems 3--5 and (76)--(85), and
[1806.08264v1](https://arxiv.org/pdf/1806.08264v1), (1.1)--(1.4) and
Theorem 2.1. They lead back to radial vector and scalar families, respectively;
their book references are candidate follow-up sources, not checked imports.

The bounded discovery queries were "quantum anharmonic crystals non
rotational invariant vector phase transition quartic anisotropic" and
"quantum anharmonic crystals anisotropic many component nonradial phase
transition". These queries do not exhaust anisotropic comparison theorems.
Search snippets and peripheral experimental results were not proof evidence.

| Comparison target | Exact boundary | Disposition for direct phase-theorem import |
|---|---|---|
| KKK Theorem 3.20, potential (3.57) | Radial quartic versus Q3 polynomial with unequal energies on a unit sphere | DOES-NOT-APPLY |
| KKK Theorem 3.21 | Full internal rotation invariance fails; spatial cubic symmetry is still present | DOES-NOT-APPLY |
| KKK Theorems 3.22 / 3.25; KK Theorem 1.4 | Scalar hypothesis fails for the R^8 onsite block; flattening gives additional nonbilinear quartic pair terms | DOES-NOT-APPLY without a separately proved reduction |
| FSS Theorem 2.1 | Nonradial priors are already allowed | APPLIES-CONDITIONALLY as the finite-mesh upper-bound input, not a new Q3 phase theorem |
| An unexamined general anisotropic comparison theorem | No exhaustive search or specialist disposition yet | NOT-YET-ASSESSED |

The manuscript now gives two algebraic witnesses rather than merely naming
nonradiality: eq:nonradial-witness evaluates the quartic on equal-norm
vectors; eq:nonbilinear-scalar-obstruction shows that a Q3 edge is not an
onsite-plus-bilinear scalar interaction. Neither rules out all possible
reductions. In particular positive lambda is not replaced by zero or infinity.

The threshold shape is also already present in KKK (3.71)--(3.75):
with f(x tanh x)=tanh(x)/x, our d_beta equals
theta_Q f(beta/(4m theta_Q)). Thus the novel candidate is not the
8 m c theta_Q^2 comparison or the inverse-temperature functional form.
What still needs model-specific proof is that this particular theta_Q is a
valid collective lower bound for the actual nonradial quantum model.

## Novelty boundary

The proposed contribution is the exact positive-lambda Q3 collective
lower-bound argument and its loop/DLR composition with standard tools.
Nonradial infrared domination, scalar Falk--Bruch/Griffiths inequalities,
and the threshold shape are established methods, not novelty claims.
The comparisons above explain why the listed model-specific phase theorems
cannot simply be cited as the Q3LOCK result. They do not exclude another
existing theorem or an immediate corollary that covers it. A focused survey
of scalar/vector phi^4 and anisotropic quantum-crystal citation chains, and
a specialist's publication-value disposition, remain open.
