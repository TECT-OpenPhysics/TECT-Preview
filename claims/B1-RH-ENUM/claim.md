# B1-RH-ENUM — Reading-H selection within enumerated condensate ensembles

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

$\Delta F[\mathcal R]=F_{\rm TECT}[\mathcal R]-F_{\rm TECT}[\mathcal R_H]>0$ for every $\mathcal R$ in the enumerated single-shell and two-shell condensate ensembles at $r_{\rm braz}=\mu^2=0.005$, at estimator grade.

## Scope

CLOSED@ESTIMATOR-GRADE within enumerated ensembles at the corrected canonical operating point. No claim over the full admissible class (STEP-5B open); no controlled error bound (ESTIMATOR-UPGRADE open).

**Notes**: Estimator error bound: uncontrolled; upgrade tracked by ESTIMATOR-UPGRADE (GAP-2 instance).

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: STEP-5B, G3PB-III, ESTIMATOR-UPGRADE, ROBUSTNESS-MU2

## Evidence

Grades: ESTIMATOR, EXECUTED. Legacy evidence pointers (resolve per `governance/migration-plan.md`):

- `legacy:Math431-HEX chain`
- `legacy:Math437 v1.2 (F10-REPAIR RESOLVED)`
- `legacy:Math442 (operator verdict 2026-06-05)`

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

## Next required action

STEP-5B beyond-layer class-wide bound (pattern-generic Gershgorin attack designated).
