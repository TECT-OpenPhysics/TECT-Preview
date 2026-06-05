# Publication Tiers — P0 / P1 / P2 (binding)

**Issued**: 2026-06-05. Defines what leaves this machine, what reaches GitHub,
and what is published outward. Designed so that the legacy repository's
four-mirror-tree drift failure class cannot recur: there is exactly **one**
tracked tree, and publication boundaries are enforced by `.gitignore` and by
derivation rules — never by parallel copies.

## P0 — `internal/` (local-only)

- Never tracked, never pushed: `internal/` is in `.gitignore`.
- Contents: session handoffs and AI working notes (`internal/sessions/`),
  scratch drafts (`internal/drafts/`), operator-private notes
  (`internal/operator/`).
- Nothing in P1/P2 may cite a P0 path. (Legacy lesson: the SESSION-HANDOFF
  cite ban.) If P0 content matters, it is rewritten into a P1 artefact.
- P0 has no version control by design; anything worth keeping is promoted.

## P1 — the repository (public verification surface)

- Everything tracked by git is P1 and will be public when the GitHub remote is
  connected. **Write every P1 file as if a hostile referee reads it today.**
- P1 invariants:
  - English-only.
  - No claim text stronger than its registered tier.
  - Large binaries excluded by `.gitignore`; numerical evidence is preserved as
    JSON (`runs/<claim-id>/result.json`) plus the script that regenerates it.
  - `CLAIMS.md` and any future generated index are derived files; their
    generators are in `verification/scripts/`; hand-editing is a defect.

## P2 — `publish/` (curated outward publication)

P2 is **derived** from P1. Two channels, separate folders, separate rules:

### `publish/website/`

- Audience: general/scientific public; rendered website content and data.
- Rule W1: every statement on the website maps to a claim ID at its registered
  tier; website data files are generated from `claims/*/status.json`
  (generator to be added under `verification/scripts/`), single direction
  P1 → P2. Manual website edits are limited to layout/narrative wrappers.
- Rule W2: no website page may show a tier, count, or status not present in
  the generated data.

### `publish/papers/`

- Audience: journals / arXiv. One folder per paper:
  `publish/papers/<paper-id>/` containing `manuscript.tex`, `claims-cited.md`
  (the list of claim IDs the paper rests on, with tiers at submission time),
  figures, and the submission/version history.
- Rule M1: paper prose is **manual-only** — never auto-drafted by AI sessions
  without explicit operator instruction (carried over from legacy §9).
- Rule M2: at submission, the cited claim set is frozen: tag the repository
  (`paper/<paper-id>/v<N>`), record the commit hash in `claims-cited.md`.
- Rule M3: a paper may not cite a claim above its registered tier; the
  linter's render output at the tagged commit is the arbiter.
- Lifecycle states per paper: `draft → internal-review → submitted →
  in-revision → published` recorded in the paper folder's `STATUS.md`.

## GitHub synchronisation

- Single repo, single remote, no curated mirror copies. `git push` is the
  entire sync mechanism; what is public is exactly P1 + P2 (tracked files).
- Before the remote is connected, the publication boundary is already enforced
  locally by `.gitignore`; connecting the remote later requires no
  restructuring.
- Recommended (when remote goes live): protected `main`, CI gate on
  `lint_claims.py`, release tags for Minimal Review Packets and paper freezes;
  Zenodo DOI snapshot per release tag.

## Decision table

| Content | Destination |
|---|---|
| Claim card, proof note, code, run JSON, policy | P1 (normal tree) |
| AI session log, scratch derivation, private note | P0 `internal/` |
| Website page/data | P2 `publish/website/` (generated) |
| Paper manuscript and submission record | P2 `publish/papers/<id>/` |
| Legacy file being migrated | `archive/legacy/...` (P1) + ledger row |
| Failed/retracted claim | stays P1: `negative-results/` (never deleted) |
