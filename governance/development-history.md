# governance/development-history.md — theory-development traceability

**Binding from**: 2026-06-06. Operator directive: the notes accumulate without
visible before/after or causal ordering; verification-first requires the
*development record* to be as traceable as `status.json` / `claim.md`, and
results worth publishing separately must be captured as they are proven.

This policy adds two artefacts to the claim package and one registry, all
trace-complete and (where possible) generated.

## 1. Per-claim development lineage — `claims/<ID>/LINEAGE.md` (GENERATED)

Produced by `verification/scripts/build_lineage.py` from the standard note
banners (`Title` / `Claim` / `Version` two-date / `Status` / cumulative
revision history) and the `runs/` directory. It is an ORDERED record:
chronological by first-issue date, supersession chains collapsed (current
version shown, superseded versions marked `†`), with per-note revision history
and tier at each step. **Never hand-edit `LINEAGE.md`.**

Regenerate after ANY change under `claims/<ID>/notes/` or `runs/`:
```
python verification/scripts/build_lineage.py          # all claims
python verification/scripts/build_lineage.py --check   # CI staleness gate (release_check)
```

Because it is derived from banners, the discipline that keeps it correct is the
existing standard-note FORM (banner fields are mandatory and machine-checked by
`build_note_pdf.py`). A note that builds clean already carries everything
`LINEAGE.md` needs — no extra per-note work.

## 2. Curated development arc — `claims/<ID>/lineage-narrative.md` (CURATED)

An optional hand-written Markdown overlay (English-only) that `build_lineage.py`
includes verbatim at the top of `LINEAGE.md` under "Development arc (curated)".
This is where the editorial story lives — *why* each step mattered, what it
superseded, where the verify-loop catches and operator verdicts fell. Write or
update it whenever a claim's arc gains a meaningful new phase (a structural
theorem, a refutation, a tier action, a gate flip). It is the human-legible
companion to the auto timeline; keep it to phases, not file-by-file detail
(the auto table already lists files).

## 3. Standalone-results registry — `RESULTS-LEDGER.md` (CURATED, root)

When a development step proves something with reuse value BEYOND its host claim
— a reusable lemma/theorem/technique, especially one publishable on its own —
register it in `RESULTS-LEDGER.md` in the SAME turn, one row: stable `R-NNN`
id, one-line statement, where proven (claim + note = the verification anchor),
reuse scope, honest tier (within its proven scope), publication target. This is
the binding capture rule: a result good enough to "organize and publish
separately" must not be left buried in a note chain.

The registry is NOT a second claim ledger: a row is a reusable artefact
*extracted from* a claim, pointing back to its proof note. It does not change
the claim's tier or the gate state.

## 4. When each is touched (per-turn checklist)

| Event | Action |
|---|---|
| New / re-issued note under `claims/<ID>/notes/` | run `build_lineage.py` (regenerates that claim's `LINEAGE.md`) |
| New development PHASE in a claim (theorem / refutation / tier action / gate flip) | update `claims/<ID>/lineage-narrative.md`, then regenerate |
| A result gains standalone reuse value | add an `R-NNN` row to `RESULTS-LEDGER.md` |
| Session end / publish | `build_lineage.py --check` must PASS (wired into `release_check.py`) |

## 5. Relationship to existing artefacts

- `CHANGELOG.md` is the GLOBAL chronological log (all claims interleaved,
  one entry per accepted change set). `LINEAGE.md` is its PER-CLAIM projection
  built from the durable note banners — the two agree by construction because
  both derive from the same accepted notes.
- `CATALOG.md` lists every artefact with versions/dates (the file inventory).
  `LINEAGE.md` orders one claim's notes into a development arc (the story of
  that inventory).
- `CLAIMS.md` is the current-state ledger. `LINEAGE.md` is the path that led to
  the current state. `RESULTS-LEDGER.md` is the reusable harvest from that path.

## 7. Record taxonomy: where each kind of record goes (binding from 2026-06-06)

Records are classified by FUNCTION, not by topic. The decision tree (apply
top-down; the first match wins):

1. **Does it establish / advance / refute a specific claim's status (tier or
   gate)?** -> `claims/<ID>/notes/<slug>-<dates>-vN.M.tex.txt` (a TIER-BEARING
   PROOF NOTE: versioned, immutable, FORM-CHECK + PDF, reproduction package;
   feeds `claims/<ID>/LINEAGE.md`). This is "theory progression" -- the only
   record kind that can move a tier or flip a gate.
2. **Is it a reusable theorem/technique extracted from a claim?** -> a row in
   `RESULTS-LEDGER.md` (curated; points back to the proof note).
3. **Is it a refutation / dead branch / retraction?** -> `negative-results/registry.md`.
4. **Is it a binding rule / process?** -> `governance/`.
5. **Is it forward-looking STRATEGY / ANALYSIS / decision-rationale that does
   NOT change any claim's status?** -> `strategy/<slug>-<YYMMDD>.md`
   (NON-tier-bearing; see below). Examples: route/attack-program planning,
   impact or dependency analyses ("if X were proven, what becomes
   unnecessary"), tradeoff studies, prioritisation rationale.
6. **Is it the development trace itself?** -> generated `claims/<ID>/LINEAGE.md`
   (auto; never hand-written).

### 7.1 The `strategy/` directory (NEW, non-tier-bearing)

- **Purpose**: capture the REASONING that steers theory direction without
  itself proving anything. A strategy note may CITE claims, gates, and
  results by ID, and may recommend a tier action, but it NEVER performs one
  and NEVER appears in a claim's tier/hypothesis fields.
- **Format**: Markdown (`.md`, English-only). Lighter than proof notes -- no
  PDF, no FORM-CHECK, no reproduction package. Light inline math is fine.
- **Naming**: `strategy/<descriptive-slug>-<YYMMDD>.md` (first-issue date).
  Strategy notes are LIVING documents: they may be updated in place (atomic
  writes only) with an internal `## Revisions` log, because -- unlike proof
  notes -- they are not citable-at-version immutable artefacts. If a strategy
  analysis HARDENS into a claim, it graduates to a `claims/<ID>/notes/` proof
  note and the strategy note points to it.
- **Index**: `strategy/INDEX.md` lists every strategy note with one-line
  purpose + the claims/gates it bears on. Curated.
- **Separation guarantee**: strategy notes are NOT parsed by
  `build_lineage.py` (lineage stays pure theory-progression) and carry no
  tier semantics. The release gate's English-only check still applies.

### 7.2 Why this matters

The operator observation (2026-06-06): theory-progression notes and
strategic/meta records were accumulating together, blurring "what was proven"
with "what we were thinking about doing." Keeping `claims/<ID>/notes/`
exclusively tier-bearing -- and routing all non-tier-bearing reasoning to
`strategy/` -- preserves the verification-first invariant that a claim's
LINEAGE shows only steps that actually moved its status.

## 6. History

- 2026-06-06: §7 record taxonomy + `strategy/` directory added (route
  non-tier-bearing strategy/analysis records out of `claims/<ID>/notes/`).
- 2026-06-06: created after the operator observed that the note pile had lost
  its before/after legibility. `build_lineage.py` v1.0.0; `RESULTS-LEDGER.md`
  seeded with R-001..R-009 (the B5 STEP-5B arc); B5/B1/B2 narratives written.
