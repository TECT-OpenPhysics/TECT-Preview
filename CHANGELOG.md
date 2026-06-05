# CHANGELOG — TECT (verification-first repository)

One entry per accepted change set. Newest first. Entries reference claim IDs,
not pillar counts.

---

## [M1/Migration] Sector-B evidence chain migrated + re-validated (277/277 asserts) — 2026-06-05

- **Batch 1 of pull-based migration** (`governance/migration-plan.md` §4 priority 1):
  23 legacy files (11 notes: Math426+AddA/AddB, Math435 v1.0–v1.1, Math437
  v1.0–v1.2, Math440, Math441, Math442; 7 scripts incl. 3 import dependencies;
  5 run JSONs) copied MIGRATED-VERBATIM to `archive/legacy/` at original paths.
- **Re-validation**: all four verification scripts re-run in a fresh
  environment — 10/10 (Math426), 101/101 (Math435), 91/91 (Math437),
  75/75 (Math440) self-test asserts PASS; regenerated JSONs identical to
  archived artefacts within rel_tol 1e-9. Artefacts:
  `runs/A1-KERNEL-CONV/260605-m1-reval/`, `runs/B2-PROPA-HLAYER/260605-m1-reval/`.
- **Finding (STALE-ARTEFACT)**: archived Math437 `step5_class_closure.json`
  predates the R1 repair (v1.0-era verdict string; numerics identical). Fresh
  artefact under `runs/` is canonical for TSv2 citation.
- **Claim updates** [A1-KERNEL-CONV, B1-RH-ENUM, B2-PROPA-HLAYER]: A1 and B2
  are migration-clean with reproduction **AVAILABLE** (two-script commands +
  expected outputs on the cards); B1 partially resolved (Math431-HEX chain
  still `legacy:` — next M1 batch). No tier changes.
- **H-LAYER / H-A0 transcribed verbatim** into `claims/GATES.md` from Math437
  v1.2 §Hypotheses (the H-LAYER beyond-layer residual is exactly STEP-5B).
- Migration ledger: 23 rows added; B2-feeding rows flagged
  **operator sign-off PENDING** per migration-plan §6.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Bootstrap] Repository structure, governance v2.0, seeded claim ledger — 2026-06-05

- Created the P0/P1/P2 three-tier repository layout (`internal/` local-only,
  repository = public verification surface, `publish/{website,papers}` curated).
- Issued `GOVERNANCE.md` v2.0 integrating the "TOE Proof Governance v1.0" and
  "Verification-First" drafts: Master Theorem + sectors A–F + GAP gates +
  TSv2 tier scale + evidence grades + claim-registration rule + no-overclaim +
  competition-closure + negative-result duty.
- Issued detailed policies under `governance/`: publication tiers, tier system
  (with legacy→TSv2 translation table), claim standard, verification standard,
  naming/versioning, migration plan.
- Seeded 17 claim cards (sectors A–F) translated conservatively from the legacy
  `TOE-FACT-SHEET.md` snapshot of 2026-06-05 (last theory tag Math442):
  Reading-H T5 estimator-grade; Prop-A T6 certified on {H-layer, H-A0};
  legacy-PROVED pillars enter as T6 with T7-candidate flags pending
  verification packages (no auto-T7 rule).
- Seeded `claims/GATES.md` (Step-5b gateway, G3'-b(iii), GAP-1..4 and named
  sub-gates), `predictions/prediction-ledger.md` (all OPEN/SCAFFOLD),
  `negative-results/registry.md` (six seeded entries incl. the Math245
  rollback and the eight failed classical-ħ routes).
- Built `verification/scripts/lint_claims.py` (schema + DAG acyclicity +
  tier-monotonicity/hypothesis rule + `--render` generator for `CLAIMS.md`);
  CI workflow at `.github/workflows/verify.yml`.
- `CLAIMS.md` is generated; hand-editing forbidden.

Maintainer: Jusang Lee <jtkor@outlook.com>
