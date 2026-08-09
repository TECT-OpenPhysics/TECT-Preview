# TECT — Topological Energy Condensate Theory

**A verification-first research programme toward a unified field theory.**

Maintainer: Jusang Lee (jtkor@outlook.com) · Bootstrapped: 2026-06-05

---

## Positioning (binding, honest-scope)

TECT is operated as a **Unified Classical Field Theory (UCFT) / partial-TOE research
programme**. No TOE-level claim is made at the programme level; the TOE statement is
managed as an explicit **Master Theorem** decomposed into sector theorems with a
tracked dependency DAG (see `GOVERNANCE.md` §1). Every result is registered as a
**claim card** with a precise statement, pinned scope, dependency list, evidence
grade, falsification gate, and maturity tier. Nothing in this repository should be
read as stronger than its registered tier.

The operating principle of this repository:

> Do not make TECT look complete. Make TECT impossible to misunderstand.

## What is in this repository

| Path | Content | Publication tier |
|---|---|---|
| `management/INDEX.md` | Bounded current task, gate, result, and reader dashboard -- start here for live work | P1 |
| `CLAIMS.md` | Master claim ledger (auto-generated — start here) | P1 |
| `theory/proof-evidence/INDEX.md` | Compact proof-evidence entry with targeted lookup commands; complete compatibility maps remain under `theory/` and `verification/` | P1 |
| `catalog/INDEX.md` | Compact current artefact catalog; machine manifest/shards in `verification/catalog/` | P1 |
| `changelog/INDEX.md` | Compact current change history; append-only authority in `changelog/log.jsonl` | P1 |
| `results/INDEX.md` | Compact reusable-result index; full curated authority in `RESULTS-LEDGER.md` | P1 |
| `negative-results/INDEX.md` | Compact failed-route and audit index; full authority in `negative-results/registry.md` | P1 |
| `explorations/log.jsonl` | Append-only proof-route decisions: checks, failures, boundaries, and revisit conditions | P1 |
| `strategy/` | Non-tier-bearing strategy / analysis / decision-rationale notes (route planning, impact studies) | P1 |
| `ROADMAP.md` | Long-form staged roadmap and historical planning narrative; live priority is in `management/INDEX.md` | P1 |
| `GOVERNANCE.md` | Operating constitution (tiers, gates, registration rules) | P1 |
| `REVIEWING.md` | How to review or attack TECT in 30 minutes | P1 |
| `governance/` | Detailed binding policies | P1 |
| `claims/` | One folder per claim: card + `status.json` + proof notes (`notes/`) + run artefacts (`runs/`) + development lineage (`LINEAGE.md`, generated; `lineage-narrative.md`, curated) — the complete verification package | P1 |
| `theory/` | Layer-2 synthesis: consolidated sector expositions citing claim IDs at registered tiers | P1 |
| `verification/` | Claim linter, verification scripts, tests | P1 |
| `codes/` | Numerical codes by domain (vacuum, topology, gravity, flavor, cosmology) | P1 |
| `predictions/` | Prediction ledger with input-freeze protocol | P1 |
| `negative-results/` | Registry of failed branches and retracted claims | P1 |
| `reviews/` | External review rounds and errata | P1 |
| `publish/website/` | Website-bound curated content (generated from claims) | P2 |
| `publish/papers/` | Paper manuscripts, one folder per paper | P2 |
| `archive/` | Curated migration target for the legacy corpus (2024–2026) | P1 |
| `internal/` | Local-only working area — **never synced to GitHub** | P0 |

Publication tiers P0/P1/P2 are defined in `governance/publication-tiers.md`.

## Quickstart for reviewers

```bash
# 1. Validate the claim ledger (schema, DAG, tier-monotonicity)
python verification/scripts/lint_claims.py

# 2. Read bounded current state, then the master claim ledger
#    management/INDEX.md — live tasks, cited gates, and reader routes
#    CLAIMS.md           — every claim, its tier, falsifier, and open gates

# 2b. Search the complete proof evidence map by an exact ID
rg -n "<claim-result-gate-or-exploration-id>" theory/proof-evidence-map.md

# 2c. Search the append-only route-decision source
python verification/scripts/exploration.py search --claim <ID>

# 3. Pick a claim and try to break it
#    claims/<ID>/claim.md  — statement, scope, falsifier, reproduction command
```

See `REVIEWING.md` for the recommended attack surface.

## Relationship to the legacy corpus

The 2024–2026 research record (≈440 math notes, solvers, run archives) lives in a
separate legacy repository (`TECT2/Contents`). It is being migrated into this
repository **pull-based and re-validated**, claim by claim — never bulk-copied.
Disposition of every legacy file is tracked in `archive/MIGRATION-LEDGER.md`.
Until a legacy evidence pointer is migrated, claim cards cite it with the prefix
`legacy:` and the claim cannot rise above tier T6 (see
`governance/migration-plan.md`).

## Language policy

All tracked files are English-only. Korean is reserved for the conversational
layer with AI collaborators and never appears in tracked content.
