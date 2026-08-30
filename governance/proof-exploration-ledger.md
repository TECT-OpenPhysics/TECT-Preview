# Proof-exploration ledger policy

**Binding from:** 2026-07-24.  This policy closes the gap between a formal
proof/no-go package and the smaller route assessments that steer proof work.

## 1. Purpose and authority boundary

`explorations/log.jsonl` is the canonical append-only ledger of every
**substantive proof-route assessment**.  A record is required when a route,
objection, assumption, comparison, or scope test reaches a stable decision
that could save another researcher from repeating work or could change the
next proof step.

The ledger preserves a finite, researcher-reusable account: the precise
question, methods/checks, finding, verdict, decision reason, boundary, next
action or resume condition, and exact evidence references.  It does not store
private token-by-token chain-of-thought, transient algebra, or untested ideas.

An exploration record has **no tier or theorem authority**.  In particular:

- `advanced` means that a route survived the recorded checks; it never means
  proved;
- `failed` is scoped to the exact architecture and boundary in that record;
  it is not a global no-go unless promoted to `negative-results/registry.md`;
- a formal theorem or reusable lemma still requires a proof note and, when
  appropriate, `RESULTS-LEDGER.md`;
- a formal refutation, dead branch, retraction, or process audit still requires
  `negative-results/registry.md`.

## 2. Capture threshold and batching

Record an exploration when at least one condition holds:

1. it rejects, parks, repairs, or selects a proof architecture;
2. it tests a load-bearing sign, factor, convention, independence, summability,
   regularity, or scope assumption;
3. it identifies the exact missing discriminator or resume condition;
4. it corrects a previously communicated route assessment;
5. omitting it would make a competent researcher likely to repeat the same
   work or mistake.

Do not record every algebra line, stylistic choice, or undeveloped thought.
During a proof-first batch, accumulate lightweight records as stable decisions
are reached.  PDF generation, formal note updates, full regeneration,
verification, commit, and push occur together at the next logical checkpoint;
they are not repeated for each exploration entry.

### PDF release boundary

The exploration ledger, route manifest, strategy certificate, and reproducible
run JSON are the development record. While a proof route is being developed,
do not issue or reissue a `.tex.txt`/PDF note for an individual lemma, audit,
or route decision. A source-only form check with `build_note_pdf.py <note>
--no-compile` is permitted when a future synthesis note is drafted. At a
single logical gate-level checkpoint, package the surviving result in one
synthesis note, build its PDF once, and render-review that final artifact
before commit. This batching changes the cadence, not the fresh-PDF release
requirement.

Before communicating a substantive route verdict to the operator, append its
record in the same response.  This file-write-before-verdict rule is the only
practical completeness control for decisions that no static release gate can
discover after omission.

## 3. Canonical schema

Each oldest-first JSONL object has:

- immutable sequential `EXP-NNNNNN` ID;
- `reviewed_on`, UTC `recorded_at`, `recorded_by`, and `provenance`;
- structured `claim_ids`, optional `task_id`, and `gate_ids`;
- `title`, exact `question`, finite `method` list, and `finding`;
- one verdict: `advanced`, `failed`, `inconclusive`, or `parked`;
- `decision_reason`, honest `boundary`, and actionable `next_action`;
- located `evidence_refs` in `path#section-or-lines` form;
- optional backward-only `related` edges;
- structured `formal_refs` to results, negative records, and changelog events.

Free prose is never mined to invent relationships.  All graph associations
come only from the structured reference fields.

## 4. Immutability and correction

Use only:

```bash
python verification/scripts/exploration.py add --file record.json
python verification/scripts/exploration.py search --claim <ID>
python verification/scripts/exploration.py verify
```

There is deliberately no edit or delete command.  The verifier requires
canonical JSON, sequential unique IDs, resolvable structured references,
repository-contained evidence paths, and backward-only relations.  It also
compares the working ledger with `git show HEAD:explorations/log.jsonl`:
after CRLF/LF transport normalization, every committed byte must remain an
exact prefix, so only canonical lines may be appended.  A later correction is a new record with a `corrects` or
`supersedes` edge; the erroneous record remains visible.

Wall-clock provenance is corrected separately and append-only.  If a retained
`recorded_at` value is shown to postdate the authority that first contains its
line, add a canonical range to `explorations/temporal-corrections.jsonl`; never
rewrite the exploration.  For a listed ID the timestamp text remains visible
but its semantic value is `UNKNOWN`.  The immutable `EXP-NNNNNN` ordinal and
append order remain authoritative.  `check_exploration_time.py` verifies the
sidecar, its Git prefix, and that no uncorrected line exceeds its first-
containing commit (or current working-tree audit time) by the allowed skew.
This operation changes no question, finding, verdict, evidence, result,
negative, task, gate, or claim status and does not reconstruct an event time.

## 5. Historical coverage boundary

Prospective mandatory coverage begins on **2026-07-24**.  Historical backfill
is allowed only when the route and verdict are directly recoverable from
tracked notes, runs, changelog entries, or registries.  Such records use
`provenance: historical-backfill` and cite those sources.

Pre-2026-07-24 coverage is therefore explicitly partial.  Missing chat-only
deliberation is not reconstructed from memory or fabricated.  Existing formal
negative records remain complete in their own registry and need not be
duplicated merely to inflate exploration counts.

## 6. Projection and release enforcement

`verification/scripts/build_proof_evidence_map.py` projects every exploration
object into both generated evidence maps, including verdict counts, per-claim
links, unresolved/parked routes, chronological details, and structured graph
edges.  The JSONL source remains authoritative for the exploration record.

The shared release spine runs `exploration.py verify` before the proof-map
staleness check.  A malformed line, rewritten history, unresolved reference,
path escape, or omitted map projection blocks release.

## 7. Known failure modes

- under-recording a verdict communicated only in chat;
- over-recording trivial algebra until the ledger becomes unusable;
- treating `advanced` as proof or `failed` as a global no-go;
- duplicating formal registries instead of linking them;
- editing an old verdict rather than appending a correction;
- inferring associations from prose;
- claiming complete historical coverage without evidence;
- applying a current gate meaning retroactively to a retained historical ID;
- sorting a corrected-untrusted `recorded_at` value as if it were chronology;
- committing, rendering, or building PDFs once per exploration instead of
  batching at a proof checkpoint.
