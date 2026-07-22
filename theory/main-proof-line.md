# Main proof line -- referee-package work list (CONFIRMED by operator 2026-06-11)

Per `governance/reproduction-bundle-policy.md` sec.12, a PUBLISHED referee package
is written only for the MAIN PROOF LINE of the published claim, not for every
sub-proof folder. The published result is the Reading-H full-class vacuum
selection (B1/B2, T7-SCOPE_{C_full}, given the A1 kernel convention). Its headline
package cites, as load-bearing dependencies: A1 kernel convention; Lemma 1
(sum-circle additive-energy bound); Lemma 2 (coherence circle-packing, in-document);
(D) T-016 diagonal isotropy; (S) SC-SCOPE selection floor; the layer K-budget;
res5_032--036.

## Main proof line (referee package each -- PUBLISHED, operator-confirmed)

| # | result | folder | role in the published theorem | status |
|---|---|---|---|---|
| 1 | Reading-H C_full | `claims/B1-RH-ENUM/Reading-H` | the comparison theorem (D)(O)(S) + window | **PUBLISHED** -- bundle `B1-RH-ENUM/bundle/Reading-H-cFull-T7-260611` |
| 2 | Prop-A | `claims/B2-PROPA-HLAYER/Prop-A` | (D) diagonal isotropy + (O) class-wide closure (T-016..T-024) | **PUBLISHED** (v1.2, T6) -- bundle `B2-PROPA-HLAYER/bundle/Prop-A-T6-260611` (9/9, 44/44 asserts PASS); scope A_adm T'<=13 |
| 3 | additive-energy / DR-2 | `claims/B5-BEYOND-LAYER-BOUND/DR-2` | Lemma 1: the sum-circle / lattice additive-energy bound (R-025/026) | **PUBLISHED, T7 CONFIRMED on lattice shells** (v1.5, standard NT import) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/DR2-Lattice-T7-NTstandard-260612` (8/8 scripts, 38/38 asserts, operator promotion 2026-06-12; pin note in-bundle; T7Candidate bundle retained as tier history); lattice shells only, arbitrary-Q OPEN, not full C_full |
| 4 | SC-SCOPE | `claims/B5-BEYOND-LAYER-BOUND/SC-SCOPE` | (S) the third-cumulant selection floor | **PUBLISHED** (v1.3, T5 thin-certified) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/SC-SCOPE-T5-260612` (4/4 entry scripts, 29/29 asserts PASS, operator clean-run CONFIRMED 2026-06-12); endpoint I=2e-3 + window W_SC only; NOT T6/T7, NOT full C_full |
| 5 | K-budget / STEP-5B | `claims/B5-BEYOND-LAYER-BOUND/STEP-5B` | the rectangle constant K(n) the off-diagonal const rests on | **PUBLISHED** (v1.2, T6) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/STEP-5B-Rectangle-T6-260612` (192/192 asserts PASS, operator clean-run CONFIRMED 2026-06-12); rectangle prefactor + official threshold 1.59e5 only, NOT full STEP-5B closure; uses H-LAYER-AUX RES-4 as input |

(A1-KERNEL-CONV is the named definitional input; it is legacy and has no in-repo
notes folder yet, so no referee package is due until it is migrated.)

## Sector-A production-functional verification line (operator-confirmed 2026-07-17)

This line is a main-line support result for the future full-production-functional
implementation track.  It does not alter, supply a missing premise for, or enlarge
the published Reading-H C_full theorem above.

| # | result | folder | role | status |
|---|---|---|---|---|
| A1-PFR | Production-functional discrete variational matrix | `claims/A1-PRODUCTION-FUNCTIONAL-REALISATION` | reproducible standalone all-coupling functional implementation; future full-production-functional support only | **PUBLISHED** (T5 CLOSED@DISCRETE-VARIATIONAL-MATRIX) -- bundle `A1-PRODUCTION-FUNCTIONAL-REALISATION/bundle/A1-Production-Functional-T5-260717`; N=4,6,8 only; no historical-solver, continuum, BCC, minimizer, or stability claim |
| A2-FULL | Full-production three-component gradient-flow well-posedness | `claims/A2-FULL-PRODUCTION-WELLPOSED` | continuum PDE theorem for the canonical P1 functional: unique global H2 flow, continuous dependence, exact energy identity, and positive-time smoothing | **PUBLISHED** (T6 CONDITIONAL-THEOREM on `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`) -- bundle `A2-FULL-PRODUCTION-WELLPOSED/bundle/A2-Full-Production-WellPosedness-T6-260717`; 22 files, 5/5 entry scripts PASS, aggregate 61/61; excludes historical backend, eta_shell nonzero, infinite volume, minimizer/BCC selection, stability, and T7 |
| A3-PERT | Scalar spectral perturbative continuum limit | `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS` | order-by-order fixed-external-momentum cutoff removal for the scalar Brazovskii branch, supported jointly by the A3 UV theorem | **PUBLISHED** (T6 PROVED CONDITIONAL, operator-approved 2026-06-23) -- bundle `A3-PERTURBATIVE-CONTINUUM-CORRELATORS/bundle/A3-Perturbative-Continuum-T6-260719`; 2/2 entry scripts PASS (6/6 + 8/8), all 11 hashes and digest `6783ee6637936675...` verify; spectral/Galerkin only, not Route B, constructive, full Class-II, or T7 |
| A4-SCALAR | Finite-volume scalar spectral constructive Gibbs measure | `claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE` | non-perturbative cutoff removal for the separate real-scalar branch: weak full-sequence convergence, lifted L1/TV density convergence, and smeared cylinder-polynomial correlations | **T6 PUBLISHED** -- operator-confirmed corrected v2.1 uses `m0=max(1,ceil(sqrt(2)q0/alpha))`; claim-level bundle `claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE/bundle/A4-Scalar-Constructive-T6-260719` passes 18/18 + 15/15 = 33/33 standalone, all 18 file hashes, and digest `b1a215465956443ce22a7dcf42caaa9a3dfb61305759f4be4f55eab630cd3162`; excludes derivative Class-II, infinite volume, phase transition, Route B, BCC, parameter identity, and T7 |
| A5-T5 | Branch-aware Sector-A synthesis and termination package | `claims/A5-SECTOR-A-SYNTHESIS` | dependency and non-implication capstone joining the full-production P1/P2/P3 chain with the separate scalar perturbative/constructive arms without identifying their mass or functional scopes | **T5 PUBLISHED** -- exact v1.2 entry operator-confirmed by explicit batch authorization after initial form validation; six support bundles attested; direct and standalone bundle runs pass 16/16 + 16/16 = 32/32; bundle `A5-SECTOR-A-SYNTHESIS/bundle/A5-Sector-A-Synthesis-T5-260719` has 155 hashed files, note-PDF completeness PASS, and digest `5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5`; excludes parameter identity, full derivative Class-II construction, BCC, physical closure, T6, and T7 |
| A5-T6 | Branch-aware Sector-A conditional-composition theorem | `claims/A5-SECTOR-A-SYNTHESIS` | conditional theorem composing the full-production variational/PDE/positive-time exact-Galerkin implication chain and the separate scalar perturbative/constructive conjunction under exactly seven named hypotheses | **T6 PUBLISHED CONDITIONAL** -- exact v1.0 candidate confirmed by Jusang Lee on 2026-07-20; v1.1 binds candidate commit and reviewed hashes; direct and standalone runs pass 22/22 + 13/13 = 35/35; bundle `A5-SECTOR-A-SYNTHESIS/bundle/A5-Sector-A-Conditional-Composition-T6-260720` has 307 hashed files and digest `7779f98a945cf1b393023ab7d41cd30af6e68572797ab698368265a392f4a526`; immutable T5 history retained; excludes parameter identity, full derivative Class-II construction, BCC, physical closure, and T7 |

The separate full derivative Class-II successor is now one theorem family,
not a sequence of peer-level capstones. A6 closes the fixed-floor canonical
$K_A$ definition after its UV power-counting obstruction; A7 closes the
covariance-normal energy composite; A8 and A9 close the decoupled reference
and interpolation identities. A10--A13 retain the exact replacement/no-go
lineage. A13 is the active subproof host: its universal $Q$ child and
finite-cutoff coefficient-jet forest are closed at scoped T4, while balanced
jet continuum convergence, exact A7 reconstruction, and the one-use/Nelson
bound remain open. This family is not a new premise of A5 and has no current
PUBLISHED measure theorem.

## Auxiliary / cited (DRAFT bundle only -- NO referee package, NOT a coverage obligation)

| folder | why auxiliary |
|---|---|
| `claims/B1-RH-ENUM/ESTIMATOR-UPGRADE` | T4 controlled-error numerical robustness of the enumerated estimator; cited, not load-bearing |
| `claims/B1-RH-ENUM/ROBUSTNESS-MU2` | off-anchor robustness evidence across the mu^2 band |
| `claims/B1-RH-ENUM/enumerated` | migration / provenance re-validation record (not a result) |
| `claims/B1-RH-ENUM/near-gap` | convention exactness + a self-caught retraction |
| `claims/B5-BEYOND-LAYER-BOUND/H-LAYER-AUX` | RES-4 layer-ratio; supports STEP-5B's K-budget |
| `claims/B2-PROPA-HLAYER/G-A0-DUI` | A=0 uniqueness sub-lemma (supports the A1 reference) -- candidate fold into Prop-A / A1 |
| `claims/B2-PROPA-HLAYER/H-A0-removal` | A=0 uniqueness sub-lemma (supports the A1 reference) -- candidate fold into Prop-A / A1 |

The DRAFT referee documents already written for the auxiliary folders remain as
internal consolidation notes; they are NOT promoted to PUBLISHED and are not
coverage obligations.

## Status (operator-confirmed 2026-06-11)

The main-line set (rows 2--5) and the auxiliary classification are CONFIRMED. The
main-line packages are refined to publication grade, operator-confirmed per result
(sec.11 gate), and bundled at `claims/<ID>/bundle/<Result>-<Tier>-<YYMMDD>/` (sec.13).
The auxiliary folders keep DRAFT bundles only; their referee DRAFTs are marked
AUXILIARY and are NOT promoted.

**Progress (2026-06-11)**: Reading-H and Prop-A are PUBLISHED. Prop-A v1.2 was
operator-confirmed after a reconstructed clean-run (9/9 scripts, 44/44 asserts
PASS) and published as `B2-PROPA-HLAYER/bundle/Prop-A-T6-260611` (T6, scope
A_adm T'<=13; does NOT independently enact full C_full). Per policy sec.14 (2026-06-11) bundles are main-line-only, claim-level, and built
only post-confirmation (no DRAFT bundle; packaging is the LAST step, followed by
the final integrity check). All per-sub-folder bundles and the pre-confirmation
DRAFT bundles are being removed Windows-side; only the two main-line PUBLISHED
bundles (`Reading-H-cFull-T7-260611`, `Prop-A-T6-260611`) remain. Remaining review
queue: T-013 COMPLETE AND CONFIRMED -- all four synthesis notes are PUBLISHED and operator-registered: `Main-Line-Synthesis-T013-260612` (v1.2, aggregate count corrected to the MANIFEST-derived 27 scripts / 330 asserts with inline provenance), `B1-RH-ENUM-Synthesis-T013-260612`, `B2-PROPA-HLAYER-Synthesis-T013-260612`, `B5-BEYOND-LAYER-BOUND-Synthesis-T013-260612` (all v1.1). The synthesis layer is FREEZE-READY. The Reading-H main line is a single claim-level theorem archive (head + five published bundles + four registered synthesis documents). Remaining tracks: T-004 R-U6-1 proof delivered (operator review pending), T-031 STEP-5B exhaustiveness decision layer, T-030 arbitrary-Q DR-2 (frontier), T-006 infra.
