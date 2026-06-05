# B3-BCC-STRUCT — BCC structural selection among tested ordered condensates

**Tier**: T4 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

Within the tested ordered-condensate class $\{\mathrm{LAM},\mathrm{HEX},\mathrm{FCC},\mathrm{SC},\mathrm{BCC}\}$ at one-loop Brazovskii level, BCC minimises the free energy at the operating point ($N_{\rm loop}$, $L_4$ coefficients): $F_{\rm BCC}<F_{\rm FCC}<F_{\rm SC}$.

## Scope

Tested representatives at one-loop; multi-shell caveat explicit; not an exhaustiveness statement.

**Notes**: Estimator error bound: uncontrolled (legacy-grade); multi-shell extension tracked by G3PB-III.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: G3PB-III

## Evidence

Grades: EXECUTED, ESTIMATOR. Legacy evidence pointers (resolve per `governance/migration-plan.md`):

- `legacy:Packet-B lineage (N_loop, L_4, Delta-F tables)`

Legacy pillar(s): none · Legacy tier label: n/a

## Falsifier

A tested-class competitor with lower free energy at the operating point under the corrected convention.

## Reproduction

Status: **PACKAGE-PENDING**. Command: `to be provided`.

## No-overclaim

BCC global optimality over all admissible structures.

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.

## Next required action

Assemble Minimal Review Packet B from the migrated N_loop/L_4 evidence chain.
