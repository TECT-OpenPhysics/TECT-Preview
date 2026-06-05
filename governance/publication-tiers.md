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
    JSON (`claims/<ID>/runs/result.json`) plus the script that regenerates it.
  - `CLAIMS.md` and any future generated index are derived files; their
    generators are in `verification/scripts/`; hand-editing is a defect.

## P2 — `publish/` (curated outward publication)

P2 is **derived** from P1. Two channels, separate folders, separate rules:

### `publish/website/` — LIVE-FETCH architecture (binding, 2026-06-05)

- Audience: general/scientific public. The website is a **static shell only**
  (`index.html`, `app.js`, `style.css`): at view time the JavaScript fetches
  the repository's `main` branch directly
  (`raw.githubusercontent.com/<owner>/<repo>/main/...`) — the manifest is
  `verification/catalog.json`, claims render from `claims/*/status.json`,
  registries/roadmap render from their Markdown sources (marked + MathJax,
  CDN). **There are no content files in `publish/website/` at all**, hence
  nothing to regenerate and nothing that can go stale: push = the site is
  current, by construction (the strongest possible form of the old W1/W2
  single-source rules).
- Rule W1′: the shell may not embed any fact, count, tier, or status as a
  literal — everything displayed is fetched. Shell changes are layout only.
- Rule W2′: the shell auto-detects `<owner>/<repo>` from the GitHub Pages URL
  (override: `?repo=owner/name`); it carries no hard-coded repository name.
- Deployment: `.github/workflows/pages.yml` uploads `publish/website/` via
  GitHub Actions Pages on every push to `main` (Settings → Pages → Source =
  GitHub Actions). This fully replaces the legacy website.

### GitHub Wiki — generated snapshot channel

- Wikis cannot fetch at view time, so the wiki is the one surface that is
  GENERATED: `python verification/scripts/build_wiki.py --repo <owner>/<repo>`
  emits the pages into a temporary directory (printed; `--out` to choose) (Home, Claims-Ledger, Gate-Registry, Roadmap,
  Negative-Results, Predictions, Reviewing, Catalog-Summary) from the same
  sources as everything else. Every page carries an AUTO-GENERATED banner.
- Hand-editing the wiki is forbidden; regenerate and re-push (publish command
  in the script docstring). Regenerate whenever the cited sources change —
  the wiki is a convenience snapshot; the repository and the live site are
  canonical.

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

## GitHub release procedure (decided 2026-06-05)

**This repository is the public repository.** No curation script copies
content into the legacy public repo — a one-direction mirror script would
re-create the legacy mirror-drift failure class (4 mirror trees, snapshot
discipline, repeated postmortems) that this architecture was built to remove.
Push = publish.

**Continuity with the legacy public repository — two sanctioned options:**

- **Option SAME-REPO (recommended when repo identity matters — URL, stars,
  watchers, issues):** on GitHub, rename the legacy default branch to
  `legacy-archive` (Settings → Branches, or push the old tree to that branch),
  then push this repository's `main` as the new default branch. The two
  histories coexist as branches of one repo; the legacy era stays browsable;
  no mirror machinery exists.
- **Option NEW-REPO (clean separation):** create a fresh public repository
  for this tree; the legacy repo gets a final commit with a README banner
  ("superseded by <new repo>; frozen as legacy archive") and is set to
  GitHub Archive (read-only). Old links keep working and point forward.

Either way the legacy public repo is never written to again except for the
archival banner.

**Mandatory pre-push gate:** every push to the public remote is preceded by

```bash
python verification/scripts/release_check.py
```

(exit 0 required) which verifies: ledger + catalog sync, the P0 fence (no
file under `internal/` cited from public surfaces), English-only policy,
no-overclaim phrase scan, P2-cites-migration-clean-claims rule, and file
hygiene (NUL/JSON/AST/oversize). CI re-runs the same gate on every push.

**Website continuity:** the legacy website stays frozen with the archival
banner until `publish/website/` has its generator; the new site then deploys
from this repository (GitHub Pages), and the old URL gets a forward link.

## Decision table

| Content | Destination |
|---|---|
| Claim card, proof note, code, run JSON, policy | P1 (normal tree) |
| AI session log, scratch derivation, private note | P0 `internal/` |
| Website page/data | P2 `publish/website/` (generated) |
| Paper manuscript and submission record | P2 `publish/papers/<id>/` |
| Legacy file being migrated | `archive/legacy/...` (P1) + ledger row |
| Failed/retracted claim | stays P1: `negative-results/` (never deleted) |
