# D1-SO10-BUNDLE — SO(10) emergence via BCC defect bundle on CP2

**Tier**: T6 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

The BCC defect bundle on $\mathbb{CP}^2$ realises SO(10) emergence: Cech cocycle closure $g_{01}g_{12}g_{20}=I$ with three-patch verification $c_1=1$ (legacy Math162 + Math167), as a conditional theorem.

## Scope

Conditional on the constructed bundle data; gauge-group emergence (sub-task 2) is NOT included.

## Dependencies and hypotheses

- Hard dependencies: none
- Hypotheses (registered in `claims/GATES.md`): H-LEGACY-CHAIN, H-CP2-BUNDLE-DATA
- Soft dependencies (context only): none
- Open gates: none

## Evidence

Grades: ANALYTIC, CONDITIONAL. Legacy evidence pointers (resolve per `governance/migration-plan.md`):

- `legacy:Math162 (bundle construction)`
- `legacy:Math167 (three-patch Cech verification, c_1=1)`

Legacy pillar(s): 4 · Legacy tier label: PROVED CONDITIONAL (legacy; Math162/166/167/168 audit)

## Falsifier

Failure of cocycle closure or of the c_1 computation on re-verification.

## Reproduction

Status: **PACKAGE-PENDING**. Command: `to be provided`.

## No-overclaim

Full gauge-group emergence (sub-task 2 stands at T3 after the Math245 rollback).

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.

## Next required action

M1-migrate Math162/167 and re-verify the cocycle computation as a package.
