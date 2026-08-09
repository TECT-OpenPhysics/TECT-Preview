# ADR-0002: freeze legacy aggregate volumes and use bounded current indexes

## Status

Accepted — 2026-08-10. Applies to the changelog, catalog, and bounded reader
indexes for the other management authorities. Full authority migrations remain
separate compatibility-controlled phases.

## Context

The canonical research corpus is healthy, but two reader projections became
unbounded:

- `CHANGELOG.md`: 568 full events, about 681 KiB;
- `CATALOG.md`: about 3,668 full table rows, about 688 KiB.

The same content was then reloaded into machine projections and the website.
The website discovered claim cards through every catalog path, including frozen
bundle copies, and consequently displayed 68 cards instead of the 49 live
top-level cards. It also constructed all catalog rows in one DOM operation.

Deleting or replacing the root Markdown files immediately is unsafe. At the
cutover, 68 Python files referenced `CHANGELOG.md` and 43 referenced
`CATALOG.md`; most are issued historical verifiers that search exact evidence
phrases or paths. They do not follow redirects or links.

## Decision

1. Canonical authorities do not change:
   `changelog/log.jsonl`, tracked artefacts, claim cards, notes, runs, and Git
   history remain the sources of truth.
2. Root `CHANGELOG.md` is frozen through record 568 and commit `4db22f4e`.
   Root `CATALOG.md` is frozen at the same commit and protected by canonical
   LF-normalized SHA-256
   `121625b81a42e3650eb46327bee84f0dfd9ed821f7d71ecc85077c606ea97d47`.
3. Current changelog navigation lives in `changelog/INDEX.md` and
   `changelog/index.json`. Stable ID locators are split into 100-record shards
   under `changelog/locators/`. Post-cutover full bodies occur exactly once in
   50-record pages under `changelog/pages/`.
4. Current catalog navigation lives in `catalog/INDEX.md` and
   `verification/catalog-summary.json`. Current machine data is a thin
   `verification/catalog/index.json` manifest plus one kind shard under
   `verification/catalog/kinds/`. The former full `verification/catalog.json`
   is frozen for issued verifier compatibility.
5. UTF-8 catalog inputs are LF-normalized before size/hash calculation. Binary
   and non-UTF-8 files retain byte-exact hashing.
6. New code may not directly consume the frozen root volumes.
   `check_aggregate_consumers.py` derives the legacy allowlist from the cutover
   commit and fails the release gate on any new consumer.
7. The website bootstraps from `catalog-summary.json`, whose claim paths must
   match only `claims/<ID>/status.json`. It fetches the full catalog only on the
   Catalog route and renders at most 100 rows per page. The Changelog route uses
   the compact index.
8. GitHub Pages deploys only after the full repository release gate passes.
9. `management/INDEX.md`, `results/INDEX.md`, `negative-results/INDEX.md`,
   `claims/GATES-INDEX.md`, and `theory/proof-evidence/INDEX.md` are bounded
   generated entry points with thin locator JSON where appropriate. They never
   repeat full result, failure, gate, or exploration bodies.
10. `RESULTS-LEDGER.md`, `negative-results/registry.md`, `claims/GATES.md`,
    `ROADMAP.md`, and the complete proof maps remain compatibility authorities;
    GitHub, the website, the Wiki, and session/review instructions route through
    the bounded entries by default.

## Non-duplication invariant

- No append-only record, proof note, run, PDF, or negative/result authority is
  removed or summarized away.
- Pre-cutover changelog bodies exist in the frozen compatibility volume;
  post-cutover bodies exist in one bounded page. The index contains metadata,
  not duplicated bodies.
- Catalog indexes contain counts and locators, not another full path table.
- Frozen bundle claim cards are retained as evidence but excluded from the live
  top-level website registry.
- The proof-map JSON no longer materializes a second `event_by_id` object copy;
  consumers build that lookup from its single event list.

## Consequences

Positive:

- the human current changelog is about 7 KiB and the catalog landing about 2 KiB;
- future root aggregate diffs are bounded;
- overview claim discovery uses 49 exact paths instead of 68 mixed live/bundle
  paths;
- catalog browser DOM work is bounded to 100 rows;
- Windows/Linux catalog regeneration produces the same text sizes and hashes.

Trade-offs:

- the two legacy root files remain in the repository until their historical
  consumers reach zero;
- the frozen `verification/catalog.json` remains until its historical direct
  consumers reach zero;
- a frozen volume is not the current reader entry point, so entry documentation
  must consistently route to `changelog/INDEX.md` and `catalog/INDEX.md`.

## Verification

- changelog source parses, event IDs are unique, the cutover volume reconstructs
  exactly, and all post-cutover pages/locators are complete with no orphan page;
- catalog cutover hash, compact index, summary, and full JSON all pass `--check`;
- exactly the top-level status paths are published in `claim_status_paths`;
- the aggregate-consumer gate reports no new direct readers;
- two consecutive regeneration passes are byte-identical;
- `release_check.py` passes before commit and Pages deployment.

## Deferred work

Further normalize/shard the proof-evidence map and migrate the remaining direct
`verification/catalog.json` consumers to the current manifest API before
removing the frozen volume. Authoritative result, negative, and gate ledgers
require their own ID-preserving JSONL/page migration because many issued
verifiers search their historical monoliths directly. Until those consumers
move to shared parsers, compact indexes solve reader and web growth without
silently dropping provenance.

At this cutover, 18 tracked code readers consume the complete proof-map JSON;
17 are issued proof-package verifiers. A later schema-v2 thinning must preserve
their referenced-ID/evidence tokens, update the field-level map test, and rerun
all 17 packages before any rich authority projection is removed.
