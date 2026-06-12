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
| 3 | additive-energy / DR-2 | `claims/B5-BEYOND-LAYER-BOUND/DR-2` | Lemma 1: the sum-circle / lattice additive-energy bound (R-025/026) | **DRAFT ACCEPTED** (v1.1, 2026-06-12; T7-candidate on the lattice class mod Lemma NT; arbitrary-Q OPEN; published-bundle HELD pending operator 7-script clean-run + Lemma NT pin) |
| 4 | SC-SCOPE | `claims/B5-BEYOND-LAYER-BOUND/SC-SCOPE` | (S) the third-cumulant selection floor | **PUBLISHED** (v1.3, T5 thin-certified) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/SC-SCOPE-T5-260612` (4/4 entry scripts, 29/29 asserts PASS, operator clean-run CONFIRMED 2026-06-12); endpoint I=2e-3 + window W_SC only; NOT T6/T7, NOT full C_full |
| 5 | K-budget / STEP-5B | `claims/B5-BEYOND-LAYER-BOUND/STEP-5B` | the rectangle constant K(n) the off-diagonal const rests on | **PUBLISHED** (v1.2, T6) -- bundle `B5-BEYOND-LAYER-BOUND/bundle/STEP-5B-Rectangle-T6-260612` (192/192 asserts PASS, operator clean-run CONFIRMED 2026-06-12); rectangle prefactor + official threshold 1.59e5 only, NOT full STEP-5B closure; uses H-LAYER-AUX RES-4 as input |

(A1-KERNEL-CONV is the named definitional input; it is legacy and has no in-repo
notes folder yet, so no referee package is due until it is migrated.)

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
queue: DR-2 published-confirm only (DRAFT ACCEPTED 2026-06-12; awaiting operator 7-script clean-run + Lemma NT pin). All five main-line packages are now operator-reviewed; per policy sec.15, the claim-level SYNTHESIS capstone (T-013) comes after DR-2 publishes. Full STEP-5B budget comparison + admissibility gates remain separately tracked.
