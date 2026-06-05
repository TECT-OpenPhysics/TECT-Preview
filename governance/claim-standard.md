# Claim Standard — cards, schema, registration (binding)

**Issued**: 2026-06-05. No result exists in TECT unless registered here.

## 1. Anatomy

```
claims/<ID>/
  claim.md      # human-readable card (statement, scope, falsifier, history,
                # devil's-advocate section, no-overclaim statement)
  status.json   # machine-readable single source of truth
  notes/        # working proof notes for this claim, versioned re-issue
                # (<descriptive-slug>-<YYMMDD-first>[-<YYMMDD-this-version>]-
                #  v<major>.<minor>.md; two-date rule from v1.1; all versions
                #  kept; naming-and-versioning.md §3)
  (optional) assumptions.md, proof-sketch.md — for large cards
```

The claim folder is the full verification package in one place: card +
machine state + proof notes. Run artefacts stay in `runs/<ID>/` (size), shared
code in `codes/` (reuse), migrated originals in `archive/legacy/` (immutable);
all are linked from the card.

`CLAIMS.md` at the root is **generated** from all `status.json` files by
`verification/scripts/lint_claims.py --render`. Hand-editing is forbidden.

## 2. Claim IDs

- Format: `<Sector><n>-<SLUG>` (e.g. `B1-RH-ENUM`). Uppercase, hyphenated.
- Slugs SHOULD be fully descriptive English words (`B5-BEYOND-LAYER-BOUND`,
  not `B5-S5B`) so the ID is readable standalone; the 2026-06-05 seeded IDs
  are grandfathered.
- **Immutable once issued.** Never renumbered, never reused — including after
  refutation (the ID lives on in `negative-results/`).
- Before creating an ID, check existence: `ls claims/ | grep '^<Sector>'`.

## 3. `status.json` schema (linter-enforced)

Required fields:

| Field | Type | Constraint |
|---|---|---|
| `id` | string | equals folder name |
| `title` | string | short, neutral |
| `sector` | string | one of A–F |
| `statement` | string | the precise mathematical statement (LaTeX allowed) |
| `scope` | string | what is and is not claimed |
| `tier` | string | `T0`–`T7` |
| `tier_scale` | string | `"TSv2"` |
| `lifecycle` | string | `ACTIVE` / `SUPERSEDED` / `REFUTED` |
| `evidence_grade` | array | ⊆ {ANALYTIC, EXACT, EXECUTED, ESTIMATOR, INHERITED, CONDITIONAL, MATCHED, INSERTED, PREDICTED}, ≥1 |
| `dependencies` | array | claim IDs; must exist; DAG acyclic |
| `hypotheses` | array | named hypotheses (strings, `H-…`); mandatory route for sub-T6 inputs of T6+ claims |
| `open_gates` | array | gate IDs from `claims/GATES.md` |
| `falsifier` | string | explicit falsification condition |
| `reproduction` | object | `{"command": str\|null, "expected": str\|null, "status": "PACKAGE-PENDING"\|"AVAILABLE"}` |
| `legacy_pillar` | array | legacy pillar numbers (may be empty) |
| `tier_legacy` | string\|null | legacy-scale label at migration time |
| `legacy_evidence` | array | `legacy:` paths into the pre-2026-06 corpus, or `archive/...` after migration |
| `t7_candidate` | bool | legacy-PROVED entries awaiting package |
| `no_overclaim` | string | the forbidden stronger reading, spelled out |
| `next_action` | string | next required step |
| `last_review` | string | ISO date |

Optional: `soft_dependencies`, `closure_depth` (C1–C3), `proof_maturity`
(S1–S3), `superseded_by`, `negative_result_ref`, `notes`.

## 4. Linter rules (failing any = result not registered)

1. JSON parses; all required fields present; enumerations valid.
2. `id` = folder name; `claim.md` exists and is non-empty.
3. Dependencies exist; dependency graph acyclic.
4. **Monotonicity/hypothesis rule**: if `tier` ≥ T6, every dependency with
   tier < T6 must be covered by at least one entry in `hypotheses`
   (the card states which); claims at ≤ T5 are exempt.
5. If `tier` = T7: `reproduction.status` = `AVAILABLE` and `t7_candidate` false
   and `legacy_evidence` contains no unresolved `legacy:` pointer.
6. If `lifecycle` = REFUTED: `negative_result_ref` present.
7. If `ESTIMATOR` ∈ `evidence_grade`: scope or notes must state
   controlled/uncontrolled error bound.
8. `no_overclaim` non-empty for every claim at T4+.

## 5. Registration / amendment procedure

1. Write or amend `claims/<ID>/` (card + json).
2. Run `python verification/scripts/lint_claims.py` → exit 0.
3. Regenerate ledger: `--render`.
4. Append a `CHANGELOG.md` entry referencing the claim ID.
5. One git commit containing all of the above (atomic set).

Tier **promotions** additionally require, inside `claim.md`: a
devil's-advocate section (≥3 concrete objections with verdicts), a quantitative
sanity check when numbers are involved, and — for T6→T7 — dual independent
audit + operator sign-off recorded in the card history.

## 6. Result footer (mandatory at the end of every theory note)

```
Result ID:               <claim ID>
Precise statement:       <one sentence or display equation>
Scope:                   <pinned scope>
Dependencies:            <claim IDs / hypotheses>
Evidence grade:          <grades>
Reproduction command:    <command or PACKAGE-PENDING>
Expected output:         <PASS criterion with tolerance>
Falsification gate:      <condition>
Tier before / after:     <Tx> / <Ty>
No-overclaim statement:  <the forbidden stronger reading>
Next required action:    <step>
```

A theory note without this footer is not citable by any claim card.
