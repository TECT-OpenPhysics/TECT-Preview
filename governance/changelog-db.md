# CHANGELOG database — append-only source, bounded views, query cache

**Binding from 2026-06-09.** Operator-authorised: DB-ize the unbounded CHANGELOG so
theory development is searchable by claim and keyword, git-backed. This document is
the design and the binding workflow.

## 1. Problem

`CHANGELOG.md` grows without bound (131 entries / ~190 kB at issue) and was
hand-edited. Two failure modes: (a) hand-edit truncation / merge risk on an
ever-larger file; (b) no structured query — "every change to `B1-RH-ENUM`
mentioning sunset" required a manual scan. A binary database (SQLite committed to
git) was rejected: it breaks the repository's plaintext clone-and-read trust model
(binary diffs, merge conflicts, opaque to reviewers).

## 2. Design — three tiers (the repo's single-source-of-truth pattern)

| Tier | Path | Role | Git |
|---|---|---|---|
| SOURCE | `changelog/log.jsonl` | append-only, one JSON object per line, oldest-first; new entries appended at EOF | tracked (plaintext, line-diff, merge-safe) |
| COMPATIBILITY | `CHANGELOG.md` | frozen through record 568 / commit `4db22f4e`; preserves issued verifier prose searches | tracked; never grows or hand-edits |
| CURRENT VIEW | `changelog/INDEX.md` | compact latest-event and page index | tracked; generated |
| BODY PAGES | `changelog/pages/NNNNNN-NNNNNN.md` | post-cutover bodies, 50 records per page; each body occurs once | tracked; generated |
| LOCATOR | `changelog/index.json` + `changelog/locators/*.json` | thin manifest/recent metadata plus 100-record stable locator shards | tracked; generated |
| CACHE | `changelog/.cache/changelog.db` | SQLite FTS5 full-text index, rebuildable | gitignored |

This keeps one full-detail authority and bounded generated readers. Pre-cutover
bodies remain once in the frozen compatibility volume; post-cutover bodies remain
once in their bounded page. The index repeats metadata only. No binary artefact
ever enters git.

## 3. Record schema (one JSON object per line)

```
id          slug (date + header)
date        YYYY-MM-DD
header      display header (tag + description + date), the verbatim first line
claim_ids   [ ... ]   auto-extracted; powers claim-scoped queries
keywords    [ ... ]   optional, author-supplied
neg_results [ ... ]   auto-extracted R-/F-/NG-/AUDIT- tags
notes       [ ... ]   supporting note IDs
scripts     [ ... ]   supporting script paths
raw         the verbatim Markdown block (header + body)
```

Losslessness rests on `raw`, not on metadata parsing. The generator reconstructs
the frozen compatibility volume from the first 568 records and projects later
records into exactly one bounded page.

## 4. Workflow (binding)

- **NEVER hand-edit any changelog projection.** Add only to `log.jsonl` through
  `changelog.py add`.
- Add an entry (body on stdin):

```
python verification/scripts/changelog.py add \
    --title "RES-5 tail-budget closure ..." --date 2026-06-09 \
    --claims B1-RH-ENUM --neg R-... AUDIT-... \
    --notes res5-... --scripts codes/vacuum/res5_....py <<'BODY'
- **headline** ...
- ...
BODY
```

  The command appends one line to `log.jsonl`, leaves the frozen compatibility
  volume unchanged, and refreshes `changelog/INDEX.md`, the thin manifest,
  locator shards, and the current bounded page.
- Query:

```
changelog.py search --claim B1-RH-ENUM --keyword sunset
changelog.py search --text "double-counted" --since 2026-06-01
changelog.py search --fts --text "screened AND tail"     # ranked FTS5
```

- Rebuild the cache (optional; `search --fts` auto-builds): `changelog.py build-db`.

## 5. Enforcement

`release_check.py` runs `changelog.py render --check` and `changelog.py verify`.
The first 568 records must reconstruct the frozen `CHANGELOG.md` exactly; every
later record must have one locator and one generated body page; stale/orphan
pages and duplicate event IDs fail. The aggregate-consumer gate also forbids new
code from reading the frozen root volume directly. `english-only` scans `.jsonl`.

## 6. Migrations

`changelog.py migrate` parsed the 131 legacy entries into `log.jsonl` with a
byte-verified lossless round-trip (`render == ` the pre-migration `CHANGELOG.md`).
The legacy hand-edited file first became the generated view of its own structured
source. At the 2026-08-10 growth cutover it became a frozen compatibility volume;
the migration command is now retired. See ADR-0002.

## 7. Sandbox note

SQLite cannot operate directly on some virtual mounts (`CREATE VIRTUAL TABLE`
raises `disk I/O error`). `build_db()` therefore builds on local disk and
byte-copies the finished file to the gitignored cache path; on local disk (the
operator side) the cache persists natively. The JSONL scan path (`search` without
`--fts`) needs no SQLite and always works.

## 8. Generalisation (follow-on)

The same JSONL-source + FTS-cache pattern extends to other append-only ledgers
(`negative-results/registry.md`, research logs) and to full-text search over note
footers (via `verification/catalog/index.json`). Tracked as a follow-on; this issue
covers `CHANGELOG`.
