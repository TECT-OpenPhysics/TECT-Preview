# AGENTS.md — AI-Collaborator Protocol (TECT verification-first repository)

**Binding from**: 2026-06-05. Loaded by every AI session working in this
repository. Deliberately short: the constitution is `GOVERNANCE.md`; this file
is only the session protocol.

## 1. Session-entry sequence (read-only, bounded)

1. As the **first shell command**, capture the UTC date using the host-native
   equivalent: POSIX `date -u +"%Y-%m-%d (%A)"`; Windows PowerShell
   `(Get-Date).ToUniversalTime().ToString('yyyy-MM-dd (dddd)',
   [Globalization.CultureInfo]::InvariantCulture)`.
2. Read `GOVERNANCE.md` (constitution), `CLAIMS.md` (current claim state), and
   `management/INDEX.md` (bounded current research/task/gate dashboard).
3. Read `changelog/INDEX.md`, `negative-results/INDEX.md`, and only the latest
   few `explorations/log.jsonl` records relevant to the active task.
4. Query live tasks with `todo.py list --status in_progress`, then `--status
   next` and `--status blocked`. `TODO.md` and `ROADMAP.md` are detailed views;
   open only the relevant task/stage section rather than loading them as the
   priority source.

Emit one status line: `[ENTRY-OK] <date> | claims: <n> | top priority: <gate>`.

On a freshly copied workspace, run `python verification/scripts/doctor.py`
first (readiness gate) and follow `SESSION.md` to resume.

For cross-claim route planning, search `theory/proof-evidence-map.md` by the
relevant claim/result/failure/gate ID and open only the linked authorities.
Do not load the complete map when a narrow lookup is sufficient.

## 2. Write discipline

- All tracked files are **English-only**. Korean stays in chat.
- **Exact-byte provenance:** `.gitattributes` disables automatic Git newline
  conversion. Write new text as UTF-8 with explicit LF (`newline="\n"` in
  Python); preserve existing hash-pinned files byte for byte. Do not enable
  `text=auto`/`eol=lf` for research sources or replace expected hashes to hide
  a checkout mismatch. The frozen catalog exception is documented in
  `governance/enforcement-spine.md` section 7.
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
  RESULTS-LEDGER, TODO, SESSION, AGENTS.md, CLAUDE.md, requirements.txt,
  .gitattributes, .gitignore). `CLAUDE.md` is a compatibility pointer to
  `AGENTS.md`, not a
  second protocol.
- `catalog/INDEX.md`, `verification/catalog-summary.json`, and the manifest/shards
  under `verification/catalog/` are generated — never hand-edit. `CATALOG.md`
  and `verification/catalog.json` are frozen pre-cutover compatibility volumes
  and must not change. Regenerate current surfaces with
  `python verification/scripts/build_catalog.py` after any
  file add/move/version; CI checks sync.
- `theory/proof-evidence-map.md` + `verification/proof-evidence-map.json` are
  generated — never hand-edit. They project all current claims, accepted
  reusable results, proof explorations, failed routes, events, tasks, gates,
  and evidence paths.
  Regenerate with `python verification/scripts/build_proof_evidence_map.py`;
  policy: `governance/proof-evidence-map.md`.
- `management/INDEX.md`, `results/INDEX.md`, `negative-results/INDEX.md`,
  `claims/GATES-INDEX.md`, their locator JSONs, and
  `theory/proof-evidence/INDEX.md` are generated compact reader surfaces. Never
  hand-edit; regenerate with `build_management_indexes.py`.
- `explorations/log.jsonl` is append-only — never edit or delete an existing
  line. Add one record or a batch with `python verification/scripts/exploration.py
  add --file ...`; corrections are new records. Policy:
  `governance/proof-exploration-ledger.md`.
- `TODO.md` is generated from `todo/todo.json` — never hand-edit; manage with
  `python verification/scripts/todo.py {list,add,start,done,block,set,render}`.
- `changelog/log.jsonl` is append-only. `CHANGELOG.md` is its frozen pre-cutover
  compatibility volume; current generated readers are `changelog/INDEX.md`,
  `changelog/index.json`, and bounded pages under `changelog/pages/` — never
  hand-edit any of them. Add entries with `python verification/scripts/changelog.py
  add --title ... --date ... --claims ...` (body on stdin); search with
  `changelog.py search [--claim|--keyword|--text|--fts]`. The query cache
  `changelog/.cache/changelog.db` is gitignored/rebuildable. Policy:
  `governance/changelog-db.md`.

## 3. Claim-first discipline

- **File-write-before-claim**: no status assertion in chat ("proved",
  "certified", "falsified", tier changes) unless the corresponding claim card
  / registry entry is already written to disk in the same response.
- One substantive claim-card change per turn; atomic set per accepted result:
  claim card + a `changelog.py add` entry (-> `changelog/log.jsonl` + regenerated
  compact index/page) + regenerated `CLAIMS.md` (+ `negative-results/` entry if a gate
  fired) in one commit.
- Tier changes require the devil's-advocate self-test in the claim card
  (≥3 concrete objections, each DISMISSED/VALID-with-mitigation/UPHELD) and
  respect for the T7 prohibition list (GOVERNANCE.md §5).
- Every numerical claim needs a reproducible script + self-test asserts + JSON
  artefact under `claims/<ID>/runs/` before it is cited as evidence.
- **PDF economy, without weakening the release gate:** during active proof
  development, keep intermediate evidence in the exploration ledger, manifest,
  strategy certificate, and reproducible run JSON; do not create or reissue a
  proof-note PDF for each lemma, audit, or route decision.  `build_note_pdf.py
  --no-compile` is permitted for source-form validation.  At one logical
  gate-level checkpoint, issue or update one synthesis note, build its PDF,
  and render-review it before commit.  The commit-time fresh-PDF requirement
  remains unchanged.
- **File-write-before-route-verdict:** before reporting a substantive proof
  route as advanced, failed, inconclusive, parked, repaired, or superseded,
  append the researcher-reusable decision to `explorations/log.jsonl` in the
  same response. Capture the exact question, finite checks, finding, reason,
  boundary, evidence, and next/revisit condition — not private token-by-token
  reasoning or trivial algebra. Formal successes and failures must still be
  promoted to their existing proof/result/negative authorities. Accumulate
  exploration entries during a proof-first batch and perform formal notes,
  PDFs, regeneration, verification, commit, and push once at the next logical
  checkpoint rather than once per entry.

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
watcher (v1.2.0+) **BATCH-DRAINS**: an accumulated queue is committed as ONE
commit with a combined numbered message, and empty-diff leftovers are moved to
done/ -- so accumulation no longer strands JSONs or scrambles attribution (the
recurring 2026-06-06/07 failure, now fixed systemically). The watcher (v1.3.0+) also **gates every commit on `release_check.py`** (gate list single-sourced in `gates.py`): a stale or broken tree is refused with the queue left intact; `regen_all.py` clears staleness. See `governance/enforcement-spine.md`. Draining per turn
still gives a cleaner 1:1 commit-to-message mapping but is not required for
correctness. The
queue is inside `internal/` (P0 — never reaches history). FALLBACK: if the
watcher is not running, the AI additionally prints the equivalent one-line
CLI block. DEFAULT (2026-07-23 operator directive, replacing manual push):
after the watcher creates a release-gated commit, the AI pushes the current
branch to its configured push remote and verifies that the remote branch head
equals local `HEAD`. Never force-push, create a tag/release, or change remote
configuration without a separate explicit instruction. Authentication or
branch-protection failures are reported with the commit preserved locally.
This closes both the skipped-commit and skipped-offsite-backup gaps.

## 5. Honesty contract

State multi-turn needs upfront. Label prototype code as prototype. If a proof
does not close, write the partial result at its honest tier and register the
obstruction as a named gate — never claim closure that does not hold.

## 6. Code discipline (binding from 2026-06-07)

Full policy: `governance/CODE-DISCIPLINE.md`. Every script under `codes/` and
`verification/scripts/`:

- **No hardcoded derived numbers** — compute them from the single upstream
  source; only INPUTS, clearly-labelled test oracles, and tooling thresholds may
  be literals. (Canonical failure: `MARGIN = 0.00432` pasted instead of
  recomputed.)
- **Mandatory adversarial review** before its numbers are cited — sign, factor/
  convention, units, convergence, hardcode-masking, limit cases — written into
  the supporting note's devil's-advocate section; invite external review.
  (Canonical failure: `M' = -J(0)` where the truth is `-J(0)/2`.)
- **Reproducible + reported** — self-test asserts covering every numerical claim,
  a JSON artefact under `claims/<ID>/runs/`, standalone `python … ` exits 0, and
  a chat report stating the file, what it computes, the run command, and the key
  asserted results so the operator can execute and verify directly.
