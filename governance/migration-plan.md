# Migration Plan — legacy corpus → verification-first repository (binding)

**Issued**: 2026-06-05.
**Legacy corpus**: the 2024–2026 repository (`TECT2/Contents`): ≈440 math notes
(`Docs/math/TECT-Math*.tex.txt`), solvers and tools (`Codes/`), run archives
(`Runs/`), status ledgers (`Docs/status/`), website tree (`Website/`).

## 1. Principles

1. **Pull-based, never bulk.** Content migrates only when a claim card needs
   it. The claim card is the demand signal; migration without a consuming
   claim is forbidden.
2. **Re-validation at the boundary.** A legacy result enters at its translated
   tier (`governance/tier-system.md` §4) and rises only through TSv2
   procedures. Migration itself never promotes.
3. **Everything is ledgered.** Every legacy file touched gets a row in
   `archive/MIGRATION-LEDGER.md` with a disposition. Files never migrated will
   eventually get a terminal disposition (`DROPPED` or `COLD-ARCHIVE`) so that
   the ledger converges to a complete account of the legacy corpus.
4. **Traceability is two-way.** Archive copies keep original filenames; new
   notes cite their archive sources; the ledger links both directions.

## 2. Dispositions

| Disposition | Meaning |
|---|---|
| MIGRATED-VERBATIM | copied to `archive/legacy/<path>`; cited as evidence as-is |
| REWRITTEN | modernised into `theory/...` (Markdown+LaTeX, TSv2 footer); archive copy kept |
| SUPERSEDED | content replaced by a newer TECT result; archive copy kept for history |
| DROPPED | not carried forward (reason recorded) |
| COLD-ARCHIVE | retained only in the frozen legacy repo; no copy here |

## 3. Phases

- **M0 — Freeze (immediate).** The legacy repository becomes read-only
  reference. New results land only here. Claim cards cite legacy evidence with
  the `legacy:` prefix (path relative to the legacy repo root).
- **M1 — Demand-driven migration (continuous).** When work touches a claim:
  migrate exactly the evidence chain that the card cites — note(s), the
  scripts that generated cited numbers, and the run JSONs. Re-run scripts
  where feasible; record the re-validation result in the ledger row.
- **M2 — Pointer resolution.** A claim card is "migration-clean" when its
  `legacy_evidence` contains no `legacy:` pointers (all resolved to
  `archive/...` or rewritten `theory/...` paths). **T7 requires
  migration-clean** (linter rule). P2 artefacts may only cite
  migration-clean claims.
- **M3 — Terminal sweep (end state).** Remaining legacy files get terminal
  dispositions; the legacy repo is retired to cold storage.

## 4. Priority order for M1

1. Claims on the critical path (Sector B: `B1-RH-ENUM`, `B2-PROPA-HLAYER` —
   the Math426/435/437/440/441/442 chain and its scripts).
2. Claims cited by the first Minimal Review Packet (Packet A).
3. T7-candidates (legacy-PROVED entries) — package construction doubles as
   migration.
4. Everything else on demand.

## 5. What does NOT migrate

- Legacy process machinery superseded by this governance (mirror-sync
  scripts, website generators bound to the old tree, snapshot pipeline).
  Lessons learned are already encoded in `governance/`; the code is
  COLD-ARCHIVE.
- Legacy status ledgers (`TOE-FACT-SHEET.md`, etc.) — translated once into
  seeded claim cards (done 2026-06-05); thereafter historical documents,
  COLD-ARCHIVE.
- Session handoffs, operator logs → never (P0-class content).

## 6. Quality gate per migrated item

Checklist recorded in the ledger row: original path; disposition; target path;
consuming claim IDs; convention check against the corrected production kernel
($r_{\rm braz}=K(q_0)=\mu^2$ lineage — stale-convention content must be
flagged or corrected on entry); re-validation evidence (re-run artefact or
reasoned waiver); date; operator sign-off for anything feeding a T6+ claim.
