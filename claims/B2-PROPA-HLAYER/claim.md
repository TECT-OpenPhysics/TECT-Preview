# B2-PROPA-HLAYER — Proposition A as a conditional theorem on {H-LAYER, H-A0}

**Tier**: T6 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

Proposition A holds as a conditional theorem within the hypothesis pair $\{\mathrm{H\text{-}LAYER},\,\mathrm{H\text{-}A0}\}$; certified for T6-conditional use on 2026-06-05 by dual independent audit plus operator sign-off.

## Scope

Theorem-grade only within the named hypothesis pair. Not a whole-Reading-H statement: the full selection claim stays at T5 pending STEP-5B.

**Notes**: M1 re-validated 2026-06-05: 166/166 asserts pass; STALE-ARTEFACT finding on archived Math437 JSON (pre-repair verdict string, numerics identical) recorded in runs/B2-PROPA-HLAYER/260605-m1-reval/summary.json. H-LAYER and H-A0 transcribed verbatim into claims/GATES.md from Math437 v1.2. Migration-clean: no legacy: pointers remain.

## Dependencies and hypotheses

- Hard dependencies: none
- Hypotheses (registered in `claims/GATES.md`): H-LAYER, H-A0
- Soft dependencies (context only): A1-KERNEL-CONV, B1-RH-ENUM
- Open gates: STEP-5B

## Evidence

Grades: ANALYTIC, CONDITIONAL. Evidence pointers (`archive/...` = migrated + re-validated; `legacy:` = pending):

- `archive/legacy/Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt`
- `archive/legacy/Docs/math/TECT-Math440-Section15p5-Consolidated-Audit-SecondWave-PARTIAL-260605-v1.0.tex.txt`
- `archive/legacy/Docs/math/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt`
- `archive/legacy/Docs/math/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt`
- `archive/legacy/Codes/supplementary/Math437_step5_class_closure.py`
- `archive/legacy/Codes/supplementary/Math440_audit_secondwave_recheck.py`
- `archive/legacy/Runs/math/Math437/step5_class_closure.json`
- `archive/legacy/Runs/math/Math440/audit_recheck.json`

Legacy pillar(s): 4 · Legacy tier label: T6 PROVED CONDITIONAL (legacy certification, Math442)

## Falsifier

A counterexample within the H-layer class violating Proposition A, or failure of the transcribed H-A0 statement to support the proof steps on migration.

## Reproduction

Status: **AVAILABLE**. Command: `cd archive/legacy/Codes/supplementary && python Math437_step5_class_closure.py && python Math440_audit_secondwave_recheck.py`.

Expected: claims 91/91 then claims 75/75 (both exit 0); numerics match archived artefacts within rel_tol 1e-9 (note: archived Math437 JSON carries a pre-repair verdict string; canonical fresh artefact in runs/B2-PROPA-HLAYER/260605-m1-reval/)

## No-overclaim

Prop-A certification does NOT promote the full Reading-H selection. 'Reading-H is T6' is forbidden while STEP-5B is open.

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.
- 2026-06-05 — M1 migration: Math437 v1.0-v1.2 + Math440/441/442 audit chain, scripts, artefacts migrated; re-validated 166/166 asserts. STALE-ARTEFACT finding (archived Math437 JSON predates R1 repair; numerics identical) logged in runs/. H-LAYER/H-A0 transcribed verbatim into GATES.md. Reproduction AVAILABLE. Migration-clean.

## Next required action

STEP-5B beyond-layer class-wide bound (the H-LAYER residual is exactly Step-5b).
