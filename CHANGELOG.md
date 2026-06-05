# CHANGELOG — TECT (verification-first repository)

One entry per accepted change set. Newest first. Entries reference claim IDs,
not pillar counts.

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
