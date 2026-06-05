# B2-PROPA-HLAYER — Proposition A as a conditional theorem on {H-LAYER, H-A0}

**Tier**: T6 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

Proposition A holds as a conditional theorem within the hypothesis pair $\{\mathrm{H\text{-}LAYER},\,\mathrm{H\text{-}A0}\}$; certified for T6-conditional use on 2026-06-05 by dual independent audit plus operator sign-off.

## Scope

Theorem-grade only within the named hypothesis pair. Not a whole-Reading-H statement: the full selection claim stays at T5 pending STEP-5B.

**Notes**: M1 re-validated 2026-06-05: 166/166 asserts pass; STALE-ARTEFACT finding on archived Math437 JSON (pre-repair verdict string, numerics identical) recorded in claims/B2-PROPA-HLAYER/runs/260605-migration-revalidation/summary.json. H-LAYER and H-A0 transcribed verbatim into claims/GATES.md from Math437 v1.2. Migration-clean: no legacy: pointers remain.

## Dependencies and hypotheses

- Hard dependencies: none
- Hypotheses (registered in `claims/GATES.md`): H-LAYER, H-A0
- Soft dependencies (context only): A1-KERNEL-CONV, B1-RH-ENUM
- Open gates: STEP-5B

## Evidence

Grades: ANALYTIC, CONDITIONAL. Evidence pointers (`archive/...` = migrated + re-validated; `legacy:` = pending):

- `archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt`
- `archive/legacy/notes/Math440/TECT-Math440-Section15p5-Consolidated-Audit-SecondWave-PARTIAL-260605-v1.0.tex.txt`
- `archive/legacy/notes/Math441/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt`
- `archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt`
- `archive/legacy/scripts/Math437_step5_class_closure.py`
- `archive/legacy/scripts/Math440_audit_secondwave_recheck.py`
- `archive/legacy/artefacts/Math437/step5_class_closure.json`
- `archive/legacy/artefacts/Math440/audit_recheck.json`

Legacy pillar(s): 4 · Legacy tier label: T6 PROVED CONDITIONAL (legacy certification, Math442)

## Falsifier

A counterexample within the H-layer class violating Proposition A, or failure of the transcribed H-A0 statement to support the proof steps on migration.

## Reproduction

Status: **AVAILABLE**. Command: `cd archive/legacy/scripts && python Math437_step5_class_closure.py && python Math440_audit_secondwave_recheck.py`.

Expected: claims 91/91 then claims 75/75 (both exit 0); numerics match archived artefacts within rel_tol 1e-9 (note: archived Math437 JSON carries a pre-repair verdict string; canonical fresh artefact in claims/B2-PROPA-HLAYER/runs/260605-migration-revalidation/)

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
- 2026-06-05 — Archive reorganised to per-tag layout; evidence paths updated. Batch record note issued: `claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-v1.0.md`.
- 2026-06-05 — Note-format decision: batch record re-issued as v1.1 `.tex.txt`
  (`claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-260605-v1.1.tex.txt`);
  v1.0 `.md` superseded. PDF pipeline verified (`build_note_pdf.py`).
- 2026-06-05 — Batch record re-issued v1.2 (table-width compliance, Overfull 7->0)
  then v1.3 (standard-form banner; FORM-CHECK PASS); PDF now lives beside the
  source in `notes/`; `build/` area retired.
- 2026-06-05 — Migration batch 2: the H-LAYER justification chain (Math427
  isotropic-dressing infimum; Math428–432/434/436 enumerated-reading
  refinements) is now in `archive/legacy/` and re-validated (167/167).

## Next required action

STEP-5B beyond-layer class-wide bound (the H-LAYER residual is exactly Step-5b).
