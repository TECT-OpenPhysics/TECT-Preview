# B1-RH-ENUM — Reading-H selection within enumerated condensate ensembles

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

$\Delta F[\mathcal R]=F_{\rm TECT}[\mathcal R]-F_{\rm TECT}[\mathcal R_H]>0$ for every $\mathcal R$ in the enumerated single-shell and two-shell condensate ensembles at $r_{\rm braz}=\mu^2=0.005$, at estimator grade.

## Scope

CLOSED@ESTIMATOR-GRADE within enumerated ensembles at the corrected canonical operating point. No claim over the full admissible class (STEP-5B open); no controlled error bound (ESTIMATOR-UPGRADE open).

**Notes**: Estimator error bound: uncontrolled; upgrade tracked by ESTIMATOR-UPGRADE (GAP-2 instance). Migration batch 2 re-validated 2026-06-05: 167/167 asserts across the eight enumerated-reading scripts (LAM/HEX/FCC races, Bloch log-det, inhomogeneous Wick, dense surface, two-shell ensemble, LAM/HEX exact-Wick brackets); all regenerated artefacts identical to archive within 1e-9 (claims/B1-RH-ENUM/runs/260605-migration-revalidation/). Migration-clean: no legacy: pointers remain.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: STEP-5B, G3PB-III, ESTIMATOR-UPGRADE

## Evidence

Grades: ESTIMATOR, EXECUTED. Evidence pointers (`archive/...` = migrated + re-validated):

- `archive/legacy/notes/Math427/TECT-Math427-G1prime-Diagonal-Isotropy-Theorem-and-G1doubleprime-Spec-260604-v1.1.tex.txt`
- `archive/legacy/notes/Math428/TECT-Math428-G1doubleprime-BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored-260604-v1.1.tex.txt`
- `archive/legacy/notes/Math429/TECT-Math429-G1pp1prime-Inhomogeneous-Wick-M-Scan-PASS-260604-v1.1.tex.txt`
- `archive/legacy/notes/Math430/TECT-Math430-G1pp2-Dense-Surface-Convergence-PASS-260604-v1.0.tex.txt`
- `archive/legacy/notes/Math431/TECT-Math431-G1pp3-LAM-HEX-FCC-PASS-260604-v1.0.tex.txt`
- `archive/legacy/notes/Math432/TECT-Math432-G3prime-Two-Shell-Ensemble-Race-PASS-260604-v1.1.tex.txt`
- `archive/legacy/notes/Math434/TECT-Math434-Section15p5-Independent-Audit-ReadingH-T5-Candidacy-PASS-260604-v1.0.tex.txt`
- `archive/legacy/notes/Math434/TECT-Math434-AddA-T5-Promotion-Record-ReadingH-Selection-260604-v1.0.tex.txt`
- `archive/legacy/notes/Math436/TECT-Math436-G1pp3b-HEX-Exact-Wick-Bracket-PASS-260604-v1.1.tex.txt`
- `archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt`
- `archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt`
- `archive/legacy/scripts/ (8 enumerated-reading verification scripts, Math427-Math436)`
- `archive/legacy/artefacts/ (per-tag archived run JSONs incl. Math434/Math436 checkpoint states)`

Legacy pillar(s): none · Legacy tier label: T5 CLOSED@ESTIMATOR-GRADE (legacy scale)

## Falsifier

$\exists\,\mathcal R\in\mathcal A_{\rm enum}$ with $\Delta F[\mathcal R]<0$ under the corrected convention.

## Reproduction

Status: **AVAILABLE**. Command: `cd archive/legacy/scripts && python Math427_g1prime_diagonal_isotropy.py && python Math428_g1doubleprime_bloch_logdet.py && python Math429_g1pp1prime_inhomogeneous_wick.py && python Math430_g1pp2_dense_surface_convergence.py && python Math431_g1pp3_lam_hex_fcc.py && python Math432_g3prime_multishell_ensemble.py && python Math434_lam_exact_wick_bracket.py && python Math436_hex_exact_wick_bracket.py`.

Expected: 5/5, 21/21, 19/19, 11/11, 15/15, 25/25, 22/22, 49/49 asserts PASS (167 total; Math434/Math436 are checkpoint-resumable: if '[CHECKPOINT] budget reached' appears, re-run the same script to resume); regenerated JSONs match archived artefacts within rel_tol 1e-9

## No-overclaim

Reading-H is the full global minimum over all possible admissible states.

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.
- 2026-06-05 — Partial resolution in migration batch 1: Math437 v1.2 / Math442
  pointers resolved to archive.
- 2026-06-05 — **Migration batch 2**: full enumerated-reading evidence chain
  (Math427–432, Math434+AddA, Math436 — 14 notes, 8 scripts, 10 artefacts)
  migrated per-tag and re-validated by fresh re-execution: **167/167 asserts
  PASS**, all regenerated JSONs identical to archive within 1e-9, zero
  stale-artefact findings. Reproduction AVAILABLE (8-script chain;
  Math434/436 checkpoint-resumable). **Migration-clean.** Batch record:
  `claims/B1-RH-ENUM/notes/enumerated-readings-migration-revalidation-260605-260605-v1.1.tex.txt`.

## Next required action

STEP-5B beyond-layer class-wide bound (pattern-generic Gershgorin attack) — the gateway for whole-Reading-H T6.
