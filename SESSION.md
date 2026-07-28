# SESSION.md — resuming TECT on any machine

This repository is a **self-contained, portable research workspace**. Copying
the `TECT` folder to another computer (or `git clone`) and connecting cowork is
enough to continue all research exactly where it left off. Nothing about the
research state lives in the cowork app; it all lives in tracked files here.

> One-line goal: *folder copy + connect cowork + `doctor.py` → resume.*

---

## 1. First time on a new machine (once)

1. **Install the interpreter and verification dependencies.** Python >= 3.10,
   then, preferably in an external sibling venv such as `TECT.venv`:

   ```bash
   pip install -r requirements.txt
   ```

   The requirements include `sympy` and `python-flint`; the latter supplies
   outward-rounded Arb balls for fail-closed interval certificates. Install
   either a venv-local `tectonic` executable or a TeX distribution
   providing `pdflatex`. Proof-note PDF generation is part of the readiness
   gate, so `doctor.py` reports NOT READY when neither engine is available.

2. **Copy the WHOLE folder.** The numerical codes in `codes/` import constants
   from `archive/legacy/scripts/`; a partial copy of only `claims/` will not run.
   `doctor.py` checks this explicitly.

3. **Connect cowork to the `TECT` folder.** The AI session auto-loads
   `CLAUDE.md` (the session protocol) as project instructions.

---

## 2. Every session (the resume ritual)

1. **Readiness check** — confirm the copy is intact and all ledgers are in sync:

   ```bash
   python verification/scripts/doctor.py        # prints READY / NOT READY + fixes
   ```

   If it reports a stale generated surface, refresh every one in a single
   command (the commit watcher enforces the same gate before every commit):

   ```bash
   python verification/scripts/regen_all.py     # or: doctor.py --fix
   ```

2. **Session-entry prelude** (CLAUDE.md §1, the AI does this automatically):
   read `GOVERNANCE.md` → `CLAIMS.md` → `ROADMAP.md` → `CHANGELOG.md` (top) →
   `negative-results/registry.md` → `explorations/log.jsonl` (latest) →
   **`TODO.md`**, run `date -u`, and emit
   `[ENTRY-OK] <date> | claims: <n> | top priority: <gate>`.

3. **Pick up the work** — the live task ledger:

   ```bash
   python verification/scripts/todo.py list
   ```

   `TODO.md` is the human-readable view; `todo/todo.json` is the source. Manage
   it with `todo.py add/start/done/block/set` (never hand-edit `TODO.md`).

   For a cross-claim proof route, search the generated evidence map without
   loading it in full:

   ```bash
   rg -n "<claim-or-gate-id>" theory/proof-evidence-map.md
   ```

   It links accepted results, failed routes and reasons, current gates/tasks,
   proof explorations, lineages, and reproduction entrypoints. The linked
   source remains authoritative. For a precise prior route verdict:

   ```bash
   python verification/scripts/exploration.py search --claim <ID>
   ```

4. **Operator only — start the commit daemon** (Windows PowerShell), so the
   AI's queued commits are recorded with the maintainer signature:

   ```powershell
   .\verification\scripts\commit_watcher.ps1            # leave running, or
   .\verification\scripts\commit_watcher.ps1 -Once      # drain once per turn
   ```

   The watcher (v1.2.0+) **batch-drains**: an accumulated queue is committed as
   ONE combined commit and empty-diff leftovers move to done/, so accumulation
   is safe. Draining per turn is still tidier (1:1 commit-to-message) but not
   required for correctness (CLAUDE.md §4).

---

## 3. Before ending a session

```bash
python verification/scripts/release_check.py     # must reach exit 0
```

`release_check` runs the ledger/catalog/lineage/**todo**/exploration-integrity/
proof-evidence-map checks, the English-only and no-overclaim scans, and file hygiene. A session
may not end with it failing.

---

## 4. Working as a team (dividing research)

- The task ledger (`TODO.md` / `todo.json`) carries `owner` and `status` per
  task. Claim a task with `todo.py set T-0NN --owner <name> --status in_progress`.
- **One substantive claim-card change per turn** (CLAUDE.md §3); commit one
  logical change set at a time. This keeps parallel work mergeable.
- Status/tier/gate transitions are **operator-authorized** — do the work, record
  it as a dated ADVANCE in `claims/GATES.md`, and recommend the flip; the
  operator confirms it.
- All numerical claims ship a reproducible script + self-test asserts + JSON
  under `claims/<ID>/runs/` (CLAUDE.md §3, §6). Anyone can re-run and verify.

---

## 5. Map of the workspace

| Path | Role |
|---|---|
| `CLAUDE.md` | session protocol (auto-loaded) |
| `GOVERNANCE.md` | constitution: tiers, gates, registration rules |
| `CLAIMS.md` / `CATALOG.md` | generated ledgers (start reading at `CLAIMS.md`) |
| `ROADMAP.md` | 6-stage roadmap + current status |
| `theory/proof-evidence-map.md` / `verification/proof-evidence-map.json` | generated human/machine map of proof advances, explorations, failures, gates, tasks, and evidence paths |
| `explorations/log.jsonl` | canonical append-only proof-route decisions; add/search/verify with `exploration.py` |
| `TODO.md` / `todo/todo.json` | live task ledger (this resume system) |
| `claims/<ID>/` | per-claim card + `status.json` + `notes/` + `runs/` + lineage |
| `claims/GATES.md` | open gates / hypotheses registry |
| `codes/` | numerical codes by domain (import `archive/legacy/scripts/`) |
| `verification/scripts/` | `doctor.py`, `lint_claims.py`, `build_*`, `todo.py`, `release_check.py`, `commit_watcher.ps1` |
| `governance/` | binding policies (incl. `CODE-DISCIPLINE.md`) |
| `negative-results/` | failed branches / retractions (trust assets) |
| `reviews/` | external adversarial-review archive |
| `internal/` | **gitignored** operator-side scratch (commit queue) — not portable via git, carried only by folder copy |

> Note: `internal/` is gitignored, so a `git clone` does **not** carry the
> commit queue (that is fine — it is operator-side scratch). A full **folder
> copy** carries everything.
