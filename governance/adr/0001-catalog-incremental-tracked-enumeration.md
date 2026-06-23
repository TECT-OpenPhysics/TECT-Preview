# ADR-0001: catalog/release-check enumerate the tracked artefact set via git, with an incremental hash cache

## Status

Accepted — 2026-06-23. Implements the L1+L2 scope approved by the operator.
Supersedes the `rglob` + hand-maintained `SKIP_DIRS` enumeration in
`build_catalog.py` (≤ v1.1.3) and `release_check.py` (≤ v1.0.3).

## Context

`build_catalog.py` exceeded the 45 s sandbox execution cap and could not be run
sandbox-side; `regen_all.py` (which ends with `build_catalog`) therefore never
completed in the sandbox either, forcing every catalog refresh onto the
operator's Windows side. Profiling (not assumption) found the cause:

- `scan()` walked the **physical** tree (`Path.rglob("*")`) and read+`sha256`-ed
  **every file's full bytes**, filtered only by a hand-maintained
  `SKIP_DIRS = {.git, internal, __pycache__, .pytest_cache, build, .cache}` that
  **does not consult `.gitignore`**.
- Google Drive for Desktop leaves sync-temp files on disk (`.tmp.driveupload/*`),
  and — decisively — **8047 of those files (165 MB) had been committed by
  mistake** in an earlier `git add -A` before the ignore rule existed. They are
  tracked, in `HEAD`, and were being pushed to the public mirror.
- Measured read volume: **521 MB over the mount at 11–15 MB/s ⇒ 45.7 s**, of
  which only **69 MB / 1116 files** are real artefacts; the rest is gitignored
  junk (the 8047 committed temps + a live 215 MB untracked temp).
- `release_check.py` shared the same enumeration and read every file's bytes in
  **five** content passes, i.e. it read the junk ~5×.

Root cause (5 Whys): the tooling enumerated the **physical tree** rather than the
**tracked artefact set**, although the catalog's own definition is "every
*tracked* research artefact". Two independent growth pressures make this
non-optional going forward: (a) the legacy-corpus migration (≈440 notes + runs)
will keep enlarging the real set; (b) note re-issues add a ~300 KB PDF each.

## Options considered

1. **Increase the sandbox budget / always run Windows-side.** Treats the symptom,
   not the cause; regen stays O(total bytes) and degrades as the corpus grows.
   Rejected.
2. **Exclude junk with a longer hand-maintained `SKIP_DIRS`/denylist.** Duplicates
   `.gitignore` knowledge (two sources of ignore truth — a DRY violation that
   drifts). Rejected as the primary mechanism; kept only as a no-git fallback.
3. **Move the catalog into a database (source of truth).** Conflicts with the
   governance rule that the catalog is a *derived* index whose sources of truth
   are the files + `status.json` + git history (`verification-standard.md` §9),
   and puts a binary blob in git. Rejected. (A DB *cache* — like
   `changelog/.cache/changelog.db` — is acceptable; see Decision L2.)
4. **Shard `catalog.json` by kind + hash large binaries via the git blob id.**
   Reduces git diff-churn and cold-read cost, but does not by itself fix the
   junk-read or the O(total) re-hash. Deferred to a follow-up ADR (L3) — it is a
   diff-churn optimisation, not the bottleneck.

## Decision

**L0 (operator, prerequisite).** Untrack the committed Drive junk so it leaves
`HEAD` and the mirror:
`git rm -r --cached .tmp.driveupload .tmp.drivedownload` then commit. (The
working-tree files stay on disk; `.gitignore` keeps them out henceforth. Sandbox
cannot do this — `index.lock` + the unlink-on-mount constraint — so it is a
Windows-side step.)

**L1 (code).** A shared `verification/scripts/repo_inventory.py` enumerates the
real set via git: `git ls-files` ∪ `git ls-files --others --exclude-standard`,
minus `git check-ignore --no-index --stdin` (the `--no-index` flag is what makes
ignore rules apply to **committed-by-mistake** files, which plain
`check-ignore` skips). This honors `.gitignore` as the single source of
ignore-truth, excludes the junk by construction even before L0 lands, and
includes new untracked-not-ignored files so the catalog/gate still see
uncommitted work. A `rglob` + denylist fallback covers the no-git case.
`build_catalog.py` (v1.2.0) and `release_check.py` (v1.0.4) both consume it.

**L2 (code).** `repo_inventory.StatCache` caches each file's intrinsic catalog
fields keyed on `(size, mtime_ns)` in the gitignored `verification/.cache/`;
unchanged files are never re-read. This is the same staleness heuristic git's
index uses, and the same cache-as-derived-artefact pattern as the changelog DB.
Regen becomes **O(changed files)**, independent of corpus size. `claims` links
are re-attached every run (they depend on `status.json`, not the file), so claim
re-targeting is never staled by the cache. Delete `verification/.cache/` to
force a cold rebuild.

## Consequences

- **Positive.** `build_catalog` 45.7 s → **3.76 s**; `regen_all` now **completes
  in the sandbox (4.1 s)** for the first time; `release_check` no longer reads the
  junk in five passes (16 s, PASS). `catalog.json` shrinks from ~12 354 polluted
  entries to **1116 real artefacts** (0 Drive-temp). Future growth is absorbed at
  O(changed). `.gitignore` becomes the one ignore-source for the tooling.
- **Negative / trade-offs.** (i) The `(size, mtime_ns)` cache cannot observe a
  content change that preserves both — a non-issue for normal edits, mitigated by
  the deletable cache and the operator's authoritative Windows-side regen. (ii)
  The cache is environment-specific (mtimes differ sandbox vs Windows); each
  environment pays one cold build, which is acceptable (≤ 20 s even cold).
  (iii) L0 leaves the 8047 blobs in *history* (tip and mirror are clean); a full
  history purge (`git filter-repo`) is a separate, riskier operation, not done
  here. (iv) One-time large `catalog.json` diff as the junk entries drop out.
- **Neutral.** `SKIP_DIRS` is retained in both scripts but now only feeds the
  no-git fallback path.

## Verification

`build_catalog.py --check` PASS; full `release_check.py` PASS after `regen_all`;
StatCache 1116 hits / 12 misses on a warm second pass; 0 `tmp.driveupload`
entries leak into the catalog; the B4 migration note is catalogued at v1.0.
Follow-up (deferred): L3 (kind-sharded `catalog.json` + git-blob-id hashing for
PDFs) if diff-churn or cold-read time later warrants it.
