# Migration Ledger — legacy corpus → this repository

Policy: `governance/migration-plan.md`. One row per legacy file touched.
Dispositions: MIGRATED-VERBATIM / REWRITTEN / SUPERSEDED / DROPPED /
COLD-ARCHIVE. A claim is migration-clean when its `legacy_evidence` has no
unresolved `legacy:` pointer.

| Legacy path | Disposition | Target | Consuming claims | Re-validation | Date | Sign-off |
|---|---|---|---|---|---|---|
| _(no rows yet — M1 begins with the Sector-B chain: Math426/435/437/440/441/442)_ | | | | | | |

## Translation events (not file migrations)

| Event | Source | Result | Date |
|---|---|---|---|
| Ledger seeding | legacy `Docs/status/TOE-FACT-SHEET.md` (snapshot 2026-06-05, Math442 state) | 17 claim cards under `claims/`, translated per `governance/tier-system.md` §4 | 2026-06-05 |

## M1 priority queue (from migration plan §4)

1. `B1-RH-ENUM` / `B2-PROPA-HLAYER` evidence chain (Math426, Math435, Math437
   v1.2, Math440, Math441, Math442 + scripts + run JSONs).
2. Packet-A citations (vacuum selection).
3. T7-candidates: `C2-LORENTZ-EMERGENT`, `C3-EP`, `D3-CHIRALITY`.
