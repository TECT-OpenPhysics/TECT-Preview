# C5-NEWTON-G — Newton-constant relation (T6/T7-SPLIT management)

**Tier**: T6 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

The relation $G=\dfrac{c^3 a_{\rm BCC}^2}{16\pi\hbar}$ is derived within the emergent-gravity chain. Constants firewall: RELATION DERIVED; VALUE MATCHED ($G_{\rm obs}$ fixes $a_{\rm BCC}$); NOT YET PREDICTED.

## Scope

T6/T7-SPLIT: the relation track (theorem-grade candidate) is strictly separated from the value track (OPEN until a_BCC is derived without G_obs).

## Dependencies and hypotheses

- Hard dependencies: none
- Hypotheses (registered in `claims/GATES.md`): H-LEGACY-CHAIN
- Soft dependencies (context only): none
- Open gates: GAP-3, PRED-G-FREEZE

## Evidence

Grades: ANALYTIC, MATCHED. Legacy evidence pointers (resolve per `governance/migration-plan.md`):

- `legacy:Newton-G relation chain (emergent gravity notes)`

Legacy pillar(s): 3 · Legacy tier label: T6/T7-SPLIT (governance draft v1.0)

## Falsifier

An internal derivation of a_BCC yielding G outside the declared error band; or a defect in the relation's derivation chain on re-validation.

## Reproduction

Status: **PACKAGE-PENDING**. Command: `to be provided`.

## No-overclaim

'G has been independently predicted' is forbidden unless a_BCC is derived without G_obs under a registered freeze (PRED-G).

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.

## Next required action

Open the PRED-G freeze: define the allowed input set {c, hbar, a_BCC-derivation} and register it before any numerical comparison.
