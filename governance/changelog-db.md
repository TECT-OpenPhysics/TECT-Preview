# CHANGELOG database — JSONL source, generated view, query cache

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
| VIEW | `CHANGELOG.md` | generated, newest-first, `== render(log.jsonl)` | tracked (generated; never hand-edit) |
| CACHE | `changelog/.cache/changelog.db` | SQLite FTS5 full-text index, rebuildable | gitignored |

Identical in spirit to `status.json -> CLAIMS.md`, `catalog.json -> CATALOG.md`,
`todo/todo.json -> TODO.md`: a plaintext structured source, a generated human view,
and a rebuildable derived index. No binary artefact ever enters git.

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

`render()` concatenates `raw` (oldest-first reversed to newest-first) under a fixed
preamble. Losslessness rests on `raw`, not on metadata parsing; the migration
round-trip is byte-verified.

## 4. Workflow (binding)

- **NEVER hand-edit `CHANGELOG.md`.** It is generated.
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

  The command appends one line to `log.jsonl` and re-renders `CHANGELOG.md`.
- Query:

```
changelog.py search --claim B1-RH-ENUM --keyword sunset
changelog.py search --text "double-counted" --since 2026-06-01
changelog.py search --fts --text "screened AND tail"     # ranked FTS5
```

- Rebuild the cache (optional; `search --fts` auto-builds): `changelog.py build-db`.

## 5. Enforcement

`release_check.py` runs `changelog.py render --check` (the `[changelog]` gate):
the working `CHANGELOG.md` must equal `render(log.jsonl)`, exactly as CLAIMS /
CATALOG / TODO are sync-gated. A hand-edit not mirrored in `log.jsonl` fails the
gate. `english-only` now also scans `.jsonl`.

## 6. Migration

`changelog.py migrate` parsed the 131 legacy entries into `log.jsonl` with a
byte-verified lossless round-trip (`render == ` the pre-migration `CHANGELOG.md`).
The legacy hand-edited file became the generated view of its own structured source.

## 7. Sandbox note

SQLite cannot operate directly on some virtual mounts (`CREATE VIRTUAL TABLE`
raises `disk I/O error`). `build_db()` therefore builds on local disk and
byte-copies the finished file to the gitignored cache path; on local disk (the
operator side) the cache persists natively. The JSONL scan path (`search` without
`--fts`) needs no SQLite and always works.

## 8. Generalisation (follow-on)

The same JSONL-source + FTS-cache pattern extends to other append-only ledgers
(`negative-results/registry.md`, research logs) and to full-text search over note
footers (via `verification/catalog.json`). Tracked as a follow-on; this issue
covers `CHANGELOG`.
