# CLAUDE.md — AI-Collaborator Protocol (TECT verification-first repository)

**Binding from**: 2026-06-05. Loaded by every AI session working in this
repository. Deliberately short: the constitution is `GOVERNANCE.md`; this file
is only the session protocol.

## 1. Session-entry sequence (read-only, in order)

1. `GOVERNANCE.md` (constitution)
2. `CLAIMS.md` (current ledger state)
3. `ROADMAP.md` (priority queue)
4. `CHANGELOG.md` (top entry)
5. `negative-results/registry.md` (top entries)

Then run `date -u +"%Y-%m-%d (%A)"` as the first shell command and emit one
status line: `[ENTRY-OK] <date> | claims: <n> | top priority: <gate>`.

## 2. Write discipline

- All tracked files are **English-only**. Korean stays in chat.
- `CLAIMS.md` is generated — never hand-edit. Regenerate with
  `python verification/scripts/lint_claims.py --render`.
- After any change under `claims/`, run the linter; a session may not end with
  a failing linter.
- New files: single-shot full-content writes. Edits to existing tracked files:
  **full-file rewrite via the shell (heredoc), never tool-layer in-place
  edits** — on 2026-06-05 three tool-layer edits/overwrites of existing files
  produced stale/truncated filesystem views (GATES.md, CHANGELOG.md,
  MIGRATION-LEDGER.md; same defect class as the legacy §11.5.2 truncation
  incidents). After writing, verify from the shell: file size + tail + linter
  (`python -c "import json,..."` for JSON).
- **Subagent / autonomous-dispatch guard (binding from 2026-06-06)**: never
  dispatch a subagent to mutate tracked files unless it has shell access for
  atomic writes (`tempfile.mkstemp` + `os.replace`). A subagent without shell
  falls back to tool-layer Write/Edit, which truncates — on 2026-06-06 an
  autonomous dispatch truncated all three Sector-B `status.json` cards
  mid-string. The linter is the backstop (it caught the corruption); the
  parent session restores from `git show HEAD:...` + re-applies verified
  field values. If a subagent lacks shell, it MUST return content for the
  parent to write, not write tracked files itself.
- Never create files at the repository root beyond the canonical set
  (README, GOVERNANCE, ROADMAP, REVIEWING, CLAIMS, CATALOG, CHANGELOG,
  CLAUDE.md, .gitignore).
- `CATALOG.md` + `verification/catalog.json` are generated — never hand-edit.
  Regenerate with `python verification/scripts/build_catalog.py` after any
  file add/move/version; CI checks sync.

## 3. Claim-first discipline

- **File-write-before-claim**: no status assertion in chat ("proved",
  "certified", "falsified", tier changes) unless the corresponding claim card
  / registry entry is already written to disk in the same response.
- One substantive claim-card change per turn; atomic set per accepted result:
  claim card + `CHANGELOG.md` entry + regenerated `CLAIMS.md` (+
  `negative-results/` entry if a gate fired) in one commit.
- Tier changes require the devil's-advocate self-test in the claim card
  (≥3 concrete objections, each DISMISSED/VALID-with-mitigation/UPHELD) and
  respect for the T7 prohibition list (GOVERNANCE.md §5).
- Every numerical claim needs a reproducible script + self-test asserts + JSON
  artefact under `claims/<ID>/runs/` before it is cited as evidence.

## 4. Commit discipline

```
git -c user.email="jtkor@outlook.com" -c user.name="Jusang Lee" commit ...
```

One logical change set per commit; the commit message references claim IDs.
Git runs on the operator's Windows side only (the sandbox mount blocks the
unlink operations git requires). DEFAULT (2026-06-05 operator directive,
replacing the manual CLI handoff): the AI writes a commit-request JSON to
`internal/commit-queue/` at the end of every turn that changes tracked
files, and the operator-side daemon `verification/scripts/commit_watcher.ps1`
(run once per session: `.\verification\scripts\commit_watcher.ps1`, or
`-Once` to drain) performs the commit with the maintainer signature. The
queue is inside `internal/` (P0 — never reaches history). FALLBACK: if the
watcher is not running, the AI additionally prints the equivalent one-line
CLI block. Push remains a manual operator action. This closes the
skipped-commit gap (code version bumps were occasionally left unrecorded
when manual paste was skipped).

## 5. Honesty contract

State multi-turn needs upfront. Label prototype code as prototype. If a proof
does not close, write the partial result at its honest tier and register the
obstruction as a named gate — never claim closure that does not hold.
