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
| `CLAIMS.md` | Master claim ledger (auto-generated — start here) | P1 |
| `CATALOG.md` | Every artefact with versions, dates, claim links (auto-generated) | P1 |
| `ROADMAP.md` | 6-Stage roadmap v2 with exit conditions and current status | P1 |
| `GOVERNANCE.md` | Operating constitution (tiers, gates, registration rules) | P1 |
| `REVIEWING.md` | How to review or attack TECT in 30 minutes | P1 |
| `governance/` | Detailed binding policies | P1 |
| `claims/` | One folder per claim: card + `status.json` + working proof notes (`notes/`) — the verification package | P1 |
| `theory/` | Layer-2 synthesis: consolidated sector expositions citing claim IDs at registered tiers | P1 |
| `verification/` | Claim linter, verification scripts, tests | P1 |
| `codes/` | Numerical codes by domain (vacuum, topology, gravity, flavor, cosmology) | P1 |
| `runs/` | Run artefacts (JSON results tracked; large binaries ignored) | P1 |
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

# 2. Read the master ledger
#    CLAIMS.md  — every claim, its tier, its falsifier, its open gates

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
