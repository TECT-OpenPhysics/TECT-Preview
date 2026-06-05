# B1-RH-ENUM — Reading-H selection within enumerated condensate ensembles

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

$\Delta F[\mathcal R]=F_{\rm TECT}[\mathcal R]-F_{\rm TECT}[\mathcal R_H]>0$ for every $\mathcal R$ in the enumerated single-shell and two-shell condensate ensembles at $r_{\rm braz}=\mu^2=0.005$, at estimator grade.

## Scope

CLOSED@ESTIMATOR-GRADE within enumerated ensembles at the corrected canonical operating point. No claim over the full admissible class (STEP-5B open); no controlled error bound (ESTIMATOR-UPGRADE open).

**Notes**: Estimator error bound: uncontrolled; upgrade tracked by ESTIMATOR-UPGRADE (GAP-2 instance). Partial M1 resolution 2026-06-05: Math437 v1.2 / Math442 pointers resolved to archive; Math431-HEX estimator chain still legacy: (claim NOT migration-clean; capped accordingly).

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: STEP-5B, G3PB-III, ESTIMATOR-UPGRADE, ROBUSTNESS-MU2

## Evidence

Grades: ESTIMATOR, EXECUTED. Evidence pointers (`archive/...` = migrated + re-validated; `legacy:` = pending):

- `legacy:Math431-HEX chain (enumerated-ensemble estimator tables; M1 migration pending)`
- `archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt`
- `archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt`

Legacy pillar(s): none · Legacy tier label: T5 CLOSED@ESTIMATOR-GRADE (legacy scale)

## Falsifier

$\exists\,\mathcal R\in\mathcal A_{\rm enum}$ with $\Delta F[\mathcal R]<0$ under the corrected convention.

## Reproduction

Status: **PACKAGE-PENDING**. Command: `to be provided`.

## No-overclaim

Reading-H is the full global minimum over all possible admissible states.

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.
- 2026-06-05 — Partial M1 resolution: Math437 v1.2 / Math442 pointers resolved to archive. Math431-HEX estimator chain remains `legacy:` — NOT migration-clean.
- 2026-06-05 — Archive reorganised to per-tag layout; resolved paths updated.

## Next required action

STEP-5B beyond-layer class-wide bound (pattern-generic Gershgorin attack designated).
