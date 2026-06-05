# B4-MASS-GAP — BCC ground-state uniqueness within the single-mode constraint cone

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

The BCC ground state is unique within the single-mode ansatz class intersected with the Math56 constraint cone; the numerical anchor $m^{*2}=+4.247\times 10^{-2}$ at $\mu^2=+5\times 10^{-3}$ reproduces to 4 digits on the subset-4-cosine branch (metastable-branch anchor, not ground state).

## Scope

CLOSED@SINGLE-MODE-CONE. The legacy 'PROVED' label is exactly this pinned scope. Three-regime continuation structure (pitchfork at mu^2 approx -0.05 +/- 0.03; branch termination mu^2 <= -0.5) is recorded evidence; Regime-III interpretation remains undetermined per the legacy G2 audit.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED. Legacy evidence pointers (resolve per `governance/migration-plan.md`):

- `legacy:Math01-v2 (uniqueness within cone)`
- `legacy:Math56 (constraint cone)`
- `legacy:Math82-AddG/G2/G3 (continuation curve + audits)`

Legacy pillar(s): 1 · Legacy tier label: PROVED - single-mode/Math56 cone caveat (legacy)

## Falsifier

A second distinct minimiser within the single-mode + cone class at the operating point, or failure to reproduce the anchor within stated tolerance.

## Reproduction

Status: **PACKAGE-PENDING**. Command: `to be provided`.

## No-overclaim

Ground-state uniqueness beyond the single-mode cone; ground-state status of the subset-4-cosine anchor.

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.

## Next required action

Ground-state continuation with the full 12-mode bcc_analytic seed (legacy Math82-H queue) under TSv2 run recording.
