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

3. **Connect the collaborator to the `TECT` folder.** The canonical session
   protocol is `AGENTS.md`. `CLAUDE.md` is only a compatibility pointer for
   clients that discover that filename.

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

2. **Session-entry prelude** (`AGENTS.md` §1, performed automatically): run the
   host-native UTC date command first, then read `GOVERNANCE.md`, `CLAIMS.md`,
   and the bounded [`management/INDEX.md`](management/INDEX.md). Read the
   compact changelog and negative indexes, query the live task states, and open
   only ID-targeted portions of the large historical authorities. Emit
   `[ENTRY-OK] <date> | claims: <n> | top priority: <gate>`.

3. **Recover the main-proof continuity state** when working on Pre-A or
   Sector A. This is a pointer-only resume layer and does not replace any
   existing proof method:

   ```bash
   python verification/scripts/check_research_continuity.py
   ```

   Read `governance/research-continuity.md` and the machine checkpoint in
   `strategy/main-proof-program-v1.json`. A failure returns the programme to
   Research Phase `P0-R` before new proof work. After watcher drain and push,
   use `--strict-baseline` to verify the clean offsite baseline; that strict
   mode is intentionally not part of the pre-commit release gate.

4. **Pick up the work** — the live task ledger:

   ```bash
   python verification/scripts/todo.py list --status in_progress
   python verification/scripts/todo.py list --status next
   python verification/scripts/todo.py list --status blocked
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

5. **Operator only — start the commit daemon** (Windows PowerShell), so the
   AI's queued commits are recorded with the maintainer signature:

   ```powershell
   .\verification\scripts\commit_watcher.ps1            # leave running, or
   .\verification\scripts\commit_watcher.ps1 -Once      # drain once per turn
   ```

   The watcher (v1.2.0+) **batch-drains**: an accumulated queue is committed as
   ONE combined commit and empty-diff leftovers move to done/, so accumulation
   is safe. Draining per turn is still tidier (1:1 commit-to-message) but not
   required for correctness (`AGENTS.md` §4).

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
- **One substantive claim-card change per turn** (`AGENTS.md` §3); commit one
  logical change set at a time. This keeps parallel work mergeable.
- Status/tier/gate transitions are **operator-authorized** — do the work, record
  it as a dated ADVANCE in `claims/GATES.md`, and recommend the flip; the
  operator confirms it.
- All numerical claims ship a reproducible script + self-test asserts + JSON
  under `claims/<ID>/runs/` (`AGENTS.md` §3, §6). Anyone can re-run and verify.

---

## 5. Map of the workspace

| Path | Role |
|---|---|
| `AGENTS.md` | single binding session protocol |
| `CLAUDE.md` | compatibility pointer to `AGENTS.md` |
| `GOVERNANCE.md` | constitution: tiers, gates, registration rules |
| `management/INDEX.md` | bounded live task, gate, result, and reader dashboard |
| `governance/research-continuity.md` | binding pointer-only long-running research resume contract |
| `strategy/main-proof-program-v1.json` | machine phase, lane, stopped-loop, and next-action checkpoint |
| `CLAIMS.md` / `catalog/INDEX.md` | current generated ledgers (root `CATALOG.md` is frozen compatibility) |
| `ROADMAP.md` | long-form staged research narrative; use the management index for live priority |
| `theory/proof-evidence/INDEX.md` | compact proof-evidence entry and targeted lookup commands |
| `theory/proof-evidence-map.md` / `verification/proof-evidence-map.json` | complete compatibility maps for deep or issued-verifier lookups |
| `explorations/log.jsonl` | canonical append-only proof-route decisions; add/search/verify with `exploration.py` |
| `TODO.md` / `todo/todo.json` | live task ledger (this resume system) |
| `claims/<ID>/` | per-claim card + `status.json` + `notes/` + `runs/` + lineage |
| `claims/GATES-INDEX.md` / `claims/GATES.md` | compact current references / complete gate and hypothesis authority |
| `codes/` | numerical codes by domain (import `archive/legacy/scripts/`) |
| `verification/scripts/` | `doctor.py`, `lint_claims.py`, `build_*`, `todo.py`, `release_check.py`, `commit_watcher.ps1` |
| `governance/` | binding policies (incl. `CODE-DISCIPLINE.md`) |
| `negative-results/` | failed branches / retractions (trust assets) |
| `reviews/` | external adversarial-review archive |
| `internal/` | **gitignored** operator-side scratch (commit queue) — not portable via git, carried only by folder copy |

> Note: `internal/` is gitignored, so a `git clone` does **not** carry the
> commit queue (that is fine — it is operator-side scratch). A full **folder
> copy** carries everything.
