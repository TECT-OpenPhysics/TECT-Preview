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

## 6. History

- 2026-06-06: created after the operator observed that the note pile had lost
  its before/after legibility. `build_lineage.py` v1.0.0; `RESULTS-LEDGER.md`
  seeded with R-001..R-009 (the B5 STEP-5B arc); B5/B1/B2 narratives written.
