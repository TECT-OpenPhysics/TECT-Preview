# Claims-tree restructure — proposal

**Date**: 2026-06-09 · **Status**: PROPOSAL (pending operator approval) ·
**Implements**: `GOVERNANCE.md` §2 (sub-theorem folders) + §8 (verification packages)

> This document is the design record for converting the flat `claims/<ID>/notes/`
> dumps into the constitutionally-mandated sub-theorem-folder structure, with
> per-sub-proof and per-claim synthesis and a generated review index. It is a
> proposal: no files are moved until the operator approves §4 (taxonomy) and §6
> (decisions).

## 1. The structural defect

- **Flat note dumps.** `claims/<ID>/notes/` holds every note for a claim with no
  grouping: B5 = 58 notes, B1 = 28, B2 = 9. The reader cannot see which notes
  belong to which sub-proof.
- **No assembled synthesis.** There is no per-claim document stating the proof of
  record as an assembled whole. That role has defaulted to the `status.json`
  `notes` field, which has grown to ~8,000 words of append-only log (B1) — a
  running audit trail, not a reviewable proof.
- **No hierarchical index.** The only index, `CATALOG.md`, is a flat file
  inventory. There is no *proof-goal → sub-proof → synthesis → status* tree to
  review the theory's state.
- **Symptom.** The SC-SCOPE programme chronicle was misfiled B1↔B5 (no
  sub-structure to guide placement); a duplicate currently exists in both folders.

## 2. Constitutional basis (this is already mandated)

`GOVERNANCE.md` §2: *"The 11 legacy pillars are retained as **sub-theorem
folders**, not as the top-level classification."* The top level is the six
sectors A–F; the 18 claim folders are the staged sector-theorems (the proof
goals). The **sub-theorem layer is specified but was never physically created.**
`GOVERNANCE.md` §8: a claim is a *Verification Package*
(Claim + Assumptions + Proof + Code + Data + Expected Output + Falsification).
A sub-proof folder is a mini-package; the claim folder assembles them.

## 3. Target structure

```
claims/
  INDEX.md                      <- NEW (generated): proof-goal tree, grouped by sector
  GATES.md                      <- (exists) hypothesis / gate registry
  _TEMPLATE/                    <- updated skeleton (now includes the sub-proof scaffold)
  B5-BEYOND-LAYER-BOUND/
    claim.md   status.json      <- (exist) the card; notes-field UNCHANGED (audit log)
    SYNTHESIS.tex.txt           <- NEW: parent synthesis (assembles the sub-proofs into the claim)
    INDEX.md                    <- NEW (generated): sub-proofs -> current notes -> status
    LINEAGE.md  lineage-narrative.md  <- (exist); build_lineage.py made sub-proof-aware
    DR-2/        notes/*.tex.txt  + SYNTHESIS.tex.txt
    SC-SCOPE/    notes/*.tex.txt  + SYNTHESIS.tex.txt
    STEP-5B/     notes/*.tex.txt  + SYNTHESIS.tex.txt
    H-LAYER-AUX/ notes/*.tex.txt
    T5-DOSSIER/  notes/*.tex.txt
    runs/                       <- STAYS at claim level (decision §6b)
  B1-RH-ENUM/ ...               <- 5 sub-proofs (see §4)
  B2-PROPA-HLAYER/ ...          <- 3 sub-proofs (see §4)
```

A sub-proof folder mirrors a claim folder in miniature: its own `notes/` and its
own `SYNTHESIS.tex.txt`. The claim-level `SYNTHESIS.tex.txt` is the parent-level synthesis — it cites each sub-proof synthesis and states how they compose into the
claim. Existing programme chronicles (`dr2-programme-consolidation`,
`scscope-programme-consolidation`) are promoted to the corresponding sub-proof
`SYNTHESIS.tex.txt`.

## 4. Sub-proof taxonomy (data-derived; 100% coverage, 0 unassigned)

### `B5-BEYOND-LAYER-BOUND` — 58 notes → 5 sub-proofs

| Sub-proof folder | Notes | Lineages | Content |
|---|---|---|---|
| `DR-2/` | 16 | 9 | sphere additive-energy / lattice-divisor closure (R-021..R-028) |
| `SC-SCOPE/` | 14 | 7 | second-cumulant scope / all-orders endpoint (R-029) |
| `STEP-5B/` | 21 | 8 | beyond-layer Gershgorin reduction + rectangle/tadpole/sunset/quartic auxiliaries |
| `H-LAYER-AUX/` | 4 | 4 | H-LAYER / admissibility-coherence auxiliaries |
| `T5-DOSSIER/` | 3 | 1 | T5 tier-assignment dossier |

### `B1-RH-ENUM` — 28 notes → 5 sub-proofs

| Sub-proof folder | Notes | Lineages | Content |
|---|---|---|---|
| `Reading-H/` | 7 | 3 | the core Reading-H selection + T6 entry |
| `ROBUSTNESS-MU2/` | 7 | 3 | off-anchor mu^2 robustness |
| `near-gap/` | 3 | 3 | near-gap small-amplitude structural floor |
| `ESTIMATOR-UPGRADE/` | 6 | 6 | error-control upgrade (single/two-shell, G3PB) |
| `enumerated/` | 5 | 4 | enumerated-class + U-series triage |

### `B2-PROPA-HLAYER` — 9 notes → 3 sub-proofs

| Sub-proof folder | Notes | Lineages | Content |
|---|---|---|---|
| `Prop-A/` | 4 | 1 | Proposition A migration re-validation |
| `H-A0-removal/` | 3 | 1 | H-A0 removal pathway |
| `G-A0-DUI/` | 2 | 1 | G-A0 DUI regularity closure |


Assignment is by note-descriptor prefix; the scan script reports zero unassigned
notes across all three populated claims. Folder names and membership are the
operator's to confirm or adjust (§6a).

## 5. Tooling impact — safety analysis

| Tool | Globs / contract | Effect of nesting | Action |
|---|---|---|---|
| `build_catalog.py` | `claims/<ID>.rglob("*")`; claim-id = first path component; `"/notes/" in p` ⇒ proof-note | nested notes attributed to `<ID>`, classified proof-note | **NO CHANGE** |
| `lint_claims.py` | `claims/<ID>/status.json` + `claim.md` (card-level) | none | **NO CHANGE** |
| `release_check.py` | `REPO.rglob` + `claims/<ID>/status.json` | none | **NO CHANGE** |
| `build_lineage.py` | `(<ID>/notes).glob("*.tex.txt")` — **non-recursive** | would miss nested notes | **UPDATE**: rglob + group rows by sub-proof folder |
| `build_index.py` | — | — | **NEW**: emit `claims/INDEX.md` + per-claim `INDEX.md` |
| `classify()` | — | claim-level `SYNTHESIS*` falls to "claim-card" | minor: add a `synthesis` rule |

**Physical moves are feasible from the sandbox**: `os.replace` (atomic rename)
succeeds into and out of subfolders; only `unlink`/delete is blocked. Notes are
*moved*, never deleted, so no blocked operation is required. (The same mechanism
cleanly resolves the B1↔B5 duplicate.)

## 6. Decisions requested

- **(a) Taxonomy** — confirm the §4 sub-proof grouping, or adjust folder
  names/membership. This is the only expensive-to-reverse choice.
- **(b) `runs/` placement** — *recommend keep at claim level.* Nesting runs into
  sub-proof folders would force rewriting ~30 scripts' hardcoded
  `claims/<ID>/runs/<run-id>` output paths and every note footer that cites them
  (high churn, low gain; runs are already date+sub-proof prefixed).
- **(c) `status.json` `notes` field** — *recommend keep as-is* (the append-only
  audit trail). The new `SYNTHESIS.tex.txt` docs become the clean readable layer;
  slimming the notes field is a separate, later cleanup.
- **(d) Sector directory** — *recommend keep flat-18* (no `claims/B/...` layer).
  The letter prefix + the generated `INDEX.md` sector grouping already encode the
  six sectors; a physical sector layer adds churn for no review benefit.

## 7. Migration plan (ordered; each step verified, one claim per commit)

1. **Tooling first (no file moves).** Update `build_lineage.py` (recursive +
   sub-proof grouping); add `build_index.py`; add the `classify()` synthesis rule.
   Run all generators on the current flat layout to confirm they are no-ops /
   backward-compatible. Run `release_check.py` (must PASS).
2. **B5** (largest): create the 5 sub-proof folders, `os.replace` each note in,
   promote the two chronicles to `SYNTHESIS.tex.txt`, write the parent
   `SYNTHESIS.tex.txt`, regenerate catalog/lineage/index, `release_check.py`,
   commit.
3. **B1** then **B2**: same procedure (5 and 3 sub-proofs).
4. **Resolve the B1↔B5 duplicate** within step 2 (the SC-SCOPE chronicle lands in
   `B5/SC-SCOPE/`; the B1 copy is `os.replace`d into place, not deleted).
5. **Update `_TEMPLATE/`** with the sub-proof scaffold so future migrated claims
   (C/D/E/F) inherit it from the start.
6. **Record**: `CHANGELOG.md`, update the layout pointer in `GOVERNANCE.md`/`CLAUDE.md`,
   commit-queue entry per claim.

## 8. Why now

Per the operator's migration plan, TECT is rebuilt by migrating TECT2 records
claim-by-claim and proving each from scratch. Sectors C/D/E/F are still empty
scaffolds. Establishing the sub-proof structure **now**, while only A1/B1/B2/B5
carry content, means every future migrated claim inherits the correct
verification-package skeleton instead of accreting another flat dump.
