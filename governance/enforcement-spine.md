# Enforcement spine — portable, forget-proof verification

**Binding from 2026-06-09.** Answers the operator question: *if the repo is moved
to another computer, is the discipline systemically enforced, or does it rely on
remembering?* The spine makes the generated-surface invariants self-enforcing and
portable — every component is a tracked file; nothing lives in `.git/hooks`, which
a clone does not carry.

## 1. Single source of truth for the gates

`verification/scripts/gates.py` defines `SYNC_GATES` (the `--check` sync gates) and
`REGEN_ORDER` (the write order, `build_catalog` LAST) ONCE. `doctor.py`,
`release_check.py`, and `regen_all.py` all import it, so the gate list can never
drift between them. The 2026-06-09 divergence — `release_check` gained
index/changelog/dossier gates that `doctor.py` lacked — is the failure mode this
prevents.

Gates (7): ledger, catalog, lineage, index, todo, changelog, dossier.

## 2. Three enforcement points

| Point | Command | Guarantee |
|---|---|---|
| Readiness (new machine, each session) | `doctor.py` | every generated surface in sync; interpreter / dependency / canonical files present |
| Commit (every commit) | `commit_watcher.ps1` → `release_check.py` | a stale or broken tree CANNOT be committed; the queue is left intact on failure |
| Recovery (one command) | `regen_all.py` / `doctor.py --fix` | refresh every generated surface in dependency order |

## 3. Portability

Folder copy / `git clone` + `pip install -r requirements.txt` + `doctor.py` is the
full bootstrap (`SESSION.md`). The commit gate is the WATCHER — a tracked file, not
a git hook — so it is carried by the copy and enforced on every machine with no
per-machine install step. The gitignored query cache (`changelog/.cache/`) is
rebuilt on demand.

## 4. Enforced vs. still-discipline (honest scope)

ENFORCED (a gate fails the commit): generated surface stale; broken JSON / Python;
Hangul in a publishable file; no-overclaim phrase on a claim/theory/publish
surface; P0 fence; catalog drift.

STILL DISCIPLINE (not yet gated): COMPLETENESS — e.g. "every accepted claim change
carries a CHANGELOG entry / the full atomic set". The spine guarantees that what IS
written is consistent and in sync; it does not yet prove that nothing was OMITTED.
A completeness linter (claim-card change vs. changelog reference) is the next
hardening step if required.

## 5. Cross-OS determinism (generators)

Generators must produce byte-identical output on every OS. Sort keys must be
OS-independent: sort by `.name` (or `.as_posix()`), NEVER a bare `Path` object —
`WindowsPath` compares case-insensitively while `PosixPath` is case-sensitive, which
silently reorders mixed-case folders. This was the 2026-06-09 `build_index` cross-OS
`[index] STALE` incident: B1-RH-ENUM's five mixed-case sub-proof folders ordered
differently on Windows vs Linux. The commit-time gate caught the symptom; this rule
(enforced by code review of every generator) prevents the cause.

## 6. Note-PDF enforcement (binding from 2026-06-10)

Every CURRENT Math note (`claims/**/notes/*.tex.txt` whose first line is not
`% SUPERSEDED`) MUST have a sibling `.pdf` at least as new as its source.
`verification/scripts/verify_note_pdfs.py` checks this (`--check`/`--strict`) and
builds missing/stale PDFs (`--build`). ENFORCEMENT is at the commit boundary:
`commit_watcher.ps1` v1.4.0 runs `--build` before staging, so no note enters
history without a fresh PDF (operator-side, no sandbox 44s timeout). `release_check`
and `doctor` report missing PDFs as an advisory `[note-pdf]`. This closes the
recurring missing-PDF defect the same way the sync gates close stale generated
surfaces.
