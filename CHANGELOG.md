# CHANGELOG — TECT (verification-first repository)

One entry per accepted change set. Newest first. Entries reference claim IDs,
not pillar counts.

---

## [Note-Form] Machine-enforced standard note form; PDFs live beside sources; build/ retired — 2026-06-05

- **Standard note form (binding, `naming-and-versioning.md` §3; authoring
  skeleton `verification/templates/note-skeleton.tex.txt`)**: banner fields
  `% Title:` (the PDF title is the proper human-readable title, never the
  filename), `% Claim:`, `% Version: vN.M -- first issued D1; this version
  issued D2` (rendered in the PDF date field as "first issued D1 · this
  version issued D2 · vN.M"), `% Status:`, cumulative revision history;
  mandatory sections Purpose-and-scope / content / Numerical-verification
  (when numbers) / Devil's-advocate / Result-footer-in-verbatim.
- **`build_note_pdf.py` v1.1.0 FORM-CHECK** enforces the form AND cross-checks
  banner version/dates against the two-date filename (mismatch refuses the
  build); compiles in a TEMPORARY directory; gates on zero Overfull-hbox;
  places the PDF **next to its source** (`claims/<ID>/notes/<stem>.pdf`;
  current version's PDF only — superseded PDFs removed, sources reproducible).
- **`build/` area retired repo-wide**: LaTeX intermediates never touch the
  repository; `build_wiki.py` v1.1.0 emits to a temp dir (`--out` override);
  `.gitignore` build/ entry removed; catalog v1.1.2 parses note-PDF filenames.
- Batch record re-issued v1.3 (standard-form banner; FORM-CHECK PASS;
  PDF title/date verified via text extraction) [A1-KERNEL-CONV,
  B2-PROPA-HLAYER]; v1.2 superseded, all versions kept.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Publication-Surfaces] Standard-LaTeX table rule; live-fetch website; wiki generator — 2026-06-05

- **Standard LaTeX + width-bounded tables (binding,
  `naming-and-versioning.md` §3)**: notes compile under the standard template
  alone (required/tools packages only; per-note preambles forbidden — extend
  the template); every table is `tabularx{\textwidth}` with wrapping `Y`
  columns; long paths use `\url{}`; acceptance = ZERO `Overfull \hbox`
  (`build_note_pdf.py` v1.0.2 prints the count and fails on nonzero).
  Proven [A1-KERNEL-CONV, B2-PROPA-HLAYER]: batch-1 record v1.1 built with 7
  overfull boxes → **v1.2 width-compliance re-issue builds with 0**
  (v1.1 superseded, kept).
- **Website rebuilt as LIVE-FETCH static shell** (`publish/website/`:
  index.html + app.js v1.0.1 + style.css; `publication-tiers.md` W1′/W2′):
  no content files exist — at view time the shell fetches `main` directly
  (catalog.json manifest → status.json cards, Markdown registries; marked +
  MathJax). Push = site current, by construction; owner/repo auto-detected
  from the Pages URL. Deployment workflow `.github/workflows/pages.yml`
  (Actions Pages) fully replaces the legacy website.
- **Wiki = the one generated snapshot channel**: `build_wiki.py` v1.0.1 emits
  8 pages to `build/wiki/` from the same sources, AUTO-GENERATED banners,
  hand-editing forbidden; publish command in the docstring.
- Defect caught in-session: `_TEMPLATE` counted as an 18th claim by the wiki
  generator (and would have been by the site) — fixed in build_wiki v1.0.1 /
  app.js v1.0.1. release_check v1.0.3 extends the English-only scan to
  .html/.js/.css.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Note-Format] Proof notes return to .tex.txt; PDF pipeline; SAME-REPO confirmed — 2026-06-05

- **Operator decisions**: (i) GitHub continuity = SAME-REPO option (legacy
  default branch → `legacy-archive`; this tree becomes the new `main`);
  (ii) the bootstrap `.md` choice for proof notes is REVISED — **working proof
  notes are `.tex.txt` LaTeX body fragments** (`naming-and-versioning.md` §3):
  full math fidelity (theorem envs, align, refs), uniformity with the ~440-note
  legacy corpus, and direct PDF builds. **Division of labour**: claim card
  (.md) = web-readable surface; note (.tex.txt) = formal document; synthesis
  documents stay .md until they transition to `publish/papers/`.
- **PDF pipeline shipped and proven**: `verification/templates/note-preamble.tex`
  + `verification/scripts/build_note_pdf.py` (v1.0.1) wrap a fragment and
  compile into git-ignored `build/` — the batch-1 record built to PDF (157 KB)
  in-session.
- **First versioned re-issue executed end-to-end** [A1-KERNEL-CONV,
  B2-PROPA-HLAYER]: batch-1 record re-issued as
  `proposition-a-migration-revalidation-260605-260605-v1.1.tex.txt` (two-date
  filename); v1.0 `.md` carries the SUPERSEDED forward pointer and is kept;
  catalog auto-detects the supersession (now 4 superseded versions tracked).
- Housekeeping: `build_catalog.py` v1.1.1 + `release_check.py` v1.0.2 skip the
  git-ignored `build/` area; ledger/card references updated; release gate PASS.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Release-Gate] Publication procedure decided + pre-push gate script — 2026-06-05

- **Decision** (`governance/publication-tiers.md` §GitHub release procedure):
  this repository IS the public repository — push = publish; **no curation
  script into the legacy public repo** (a one-direction mirror would re-create
  the legacy mirror-drift failure class). Continuity options sanctioned:
  SAME-REPO (legacy default branch renamed `legacy-archive`, this tree pushed
  as the new `main`; keeps URL/stars/issues) or NEW-REPO (fresh repo; legacy
  repo archived with a forward banner). Legacy public repo is never written
  again except the archival banner.
- **New gate** `verification/scripts/release_check.py` v1.0.1 (mandatory
  before every push; also a CI step): ledger+catalog sync, P0 fence (no file
  under `internal/` cited from public surfaces), English-only scan,
  no-overclaim phrase scan, P2-cites-migration-clean-claims rule, hygiene
  (NUL/JSON/AST/oversize). First run caught 3 genuine self-defects (stale
  catalog; over-broad fence; Hangul literal in own regex) — fixed in v1.0.1;
  gate now PASS.
- No tier changes; all generated surfaces in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Code-Versioning] Uniform date+version management extended to code and results — 2026-06-05

- **Operator directive**: everything — documents, code, scripts, results —
  carries date+version management. **Mechanism differs by artefact class**
  (`governance/naming-and-versioning.md` §5, binding):
  documents = filename two-date re-issue (citable immutable artefacts);
  **code = in-place evolution under git + mandatory version header**
  (`__version__`, `__first_issued__`, `__version_issued__`, optional
  `__claims__`, docstring changelog) — filename re-issue of code is FORBIDDEN
  (breaks imports/reproduction; side-by-side copies = the stale-physics drift
  class behind the legacy corrected-convention cascade);
  **results = immutable run folders** (new run = new
  `runs/<claim>/<YYMMDD>-<descriptive-tag>/`), artefacts record producing-code
  versions (+ git commit when available) — `verification-standard.md` §4.
- **Catalog upgraded** (`build_catalog.py` v1.1.0): parses python version
  headers and run-artefact dates, so code and results now show the same
  first-issue / version-issue / version columns as documents in `CATALOG.md`
  — uniform visibility without uniform mechanism. Harness scripts carry their
  headers (lint_claims v1.2.0, build_catalog v1.1.0).
- Archive scripts stay verbatim-immutable (no headers; dates in the ledger).
- No tier changes; linter PASS; catalog + ledger views in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Catalog] Derived artefact catalog — database capability without a database — 2026-06-05

- **Binding rule** (`governance/verification-standard.md` §8): the repository
  gets database-grade indexing as a DERIVED, disposable index only — the files,
  `claims/*/status.json`, and git history remain the sole sources of truth;
  authoritative stores beside them are forbidden (same single-source principle
  as `CLAIMS.md`/`BY-CLAIM.md`; kills the legacy mirror-drift class).
- **New generator** `verification/scripts/build_catalog.py` → `CATALOG.md`
  (human view, by artefact kind) + `verification/catalog.json` (machine twin):
  path, kind, claim links, theory tag, two-date fields, version, lifecycle
  (SUPERSEDED auto-detected from banners — currently 3), size, sha256/12.
  105 artefacts at first issue. CI `--check` step + smoke test added;
  `CATALOG.md` joins the root canonical set.
- No tier changes; linter PASS; all generated files in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Naming] Human-readable filenames + first-issue-date convention — 2026-06-05

- **Binding naming rules added** (operator directive;
  `governance/naming-and-versioning.md` §3): (i) file/folder names and document
  headings lead with DESCRIPTIVE English slugs — internal codes (claim IDs,
  gate IDs, migration-phase labels) are never the sole identifying token
  outside the registry layer, and every code is expanded at first use in
  document bodies; (ii) two-date rule (refined same
  day by operator): first issue carries `-<YYMMDD-first>-v1.0`; every later
  version carries BOTH the first-issue date and its own issue date —
  `<slug>-<YYMMDD-first>-<YYMMDD-current>-vN.M.md` — so the filename shows the
  document's birth date and the currency of the version at a glance.
- **Renames applied**: batch-1 record note →
  `claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-v1.0.md`;
  run folders → `runs/<claim>/260605-migration-revalidation/`; all references
  swept (ledger, index, cards, note body); older CHANGELOG entries left
  untouched as historical record.
- Future claim IDs use fully descriptive slugs (`claim-standard.md` §2);
  seeded IDs grandfathered. Run-folder tags must be descriptive words
  (`naming-and-versioning.md` §6). Synthesis-document pattern now
  `<descriptive-slug>-synthesis-<YYMMDD>-vN.M.md`.
- No tier changes; linter PASS; generated files in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Layers] Three-layer architecture: claim packages, synthesis theory/, BY-CLAIM view — 2026-06-05

- **Layer model formalised** (operator design): L1 proof system (`claims/` +
  `archive/` + `codes/` + `runs/` + `verification/` + ledgers) → L2 theory
  synthesis (`theory/`, consolidated sector expositions citing only claim IDs
  at registered tiers) → L3 publication (`publish/`). Documented in
  `theory/README.md`; sector READMEs updated.
- **Working proof notes now live with their claim**:
  `claims/<ID>/notes/<claimID>-<slug>-vN.M.md` (claim folder = complete
  verification package: card + state + notes). The batch-1 record moved to
  `claims/B2-PROPA-HLAYER/notes/B2-PROPA-HLAYER-m1-revalidation-v1.0.md`;
  all references updated. Policies: `naming-and-versioning.md` §3/§8,
  `claim-standard.md` §1, `migration-plan.md` §2.
- **Per-claim archive view is GENERATED, not physical**: archive stays in the
  per-tag layout (one legacy file can serve several claims; scripts must stay
  co-located to remain runnable; archive keyed by immutable theory tags, not
  mutable claim structure). New generated reverse-lookup
  `archive/legacy/BY-CLAIM.md` (claim → migrated files + reproduction command
  + unresolved `legacy:` debt), emitted and sync-checked by
  `lint_claims.py --render [--check]`.
- Housekeeping: orphan `pytest-cache-files-*/` + `.pytest_cache/` (from the
  sandbox pytest cacheprovider crash) moved out of the tree and gitignored.
- No tier changes; linter PASS; generated files in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [M1/Reorg] Archive per-tag layout + first TSv2 theory note — 2026-06-05

- **Archive reorganised** (operator request): `archive/legacy/` moved from the
  flat original-path mirror to the per-tag layout `notes/<TheoryTag>/` (all
  versions of a tag together, superseded banners intact), `scripts/` (flat,
  runnable as-is — sibling imports preserved; re-verified 10/10 post-move),
  `artefacts/<TheoryTag>/`. Original legacy paths remain recorded per file in
  `archive/MIGRATION-LEDGER.md`; new lookup table `archive/legacy/INDEX.md`;
  layout documented in `archive/README.md` and reflected in
  `governance/migration-plan.md` §1/§2 and `governance/naming-and-versioning.md` §8.
- **All evidence paths updated** [A1-KERNEL-CONV, B1-RH-ENUM, B2-PROPA-HLAYER]:
  status.json + claim.md + runs summaries + GATES.md source pointers now cite
  the per-tag paths; reproduction commands now `cd archive/legacy/scripts`.
- **First TSv2 theory note issued**:
  `theory/sector-B-vacuum/B2-PROPA-HLAYER-m1-revalidation-v1.0.md` — the
  permanent batch-1 record (re-validation table, STALE-ARTEFACT finding F-1,
  hypothesis transcription, devil's-advocate α/β/γ, §6 result footer),
  demonstrating the versioned-re-issue scheme (`-v<major>.<minor>.md`, full
  revision banner, all versions kept).
- No tier changes; linter PASS.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [M1/Migration] Sector-B evidence chain migrated + re-validated (277/277 asserts) — 2026-06-05

- **Batch 1 of pull-based migration** (`governance/migration-plan.md` §4 priority 1):
  23 legacy files (11 notes: Math426+AddA/AddB, Math435 v1.0–v1.1, Math437
  v1.0–v1.2, Math440, Math441, Math442; 7 scripts incl. 3 import dependencies;
  5 run JSONs) copied MIGRATED-VERBATIM to `archive/legacy/` at original paths.
- **Re-validation**: all four verification scripts re-run in a fresh
  environment — 10/10 (Math426), 101/101 (Math435), 91/91 (Math437),
  75/75 (Math440) self-test asserts PASS; regenerated JSONs identical to
  archived artefacts within rel_tol 1e-9. Artefacts:
  `runs/A1-KERNEL-CONV/260605-m1-reval/`, `runs/B2-PROPA-HLAYER/260605-m1-reval/`.
- **Finding (STALE-ARTEFACT)**: archived Math437 `step5_class_closure.json`
  predates the R1 repair (v1.0-era verdict string; numerics identical). Fresh
  artefact under `runs/` is canonical for TSv2 citation.
- **Claim updates** [A1-KERNEL-CONV, B1-RH-ENUM, B2-PROPA-HLAYER]: A1 and B2
  are migration-clean with reproduction **AVAILABLE** (two-script commands +
  expected outputs on the cards); B1 partially resolved (Math431-HEX chain
  still `legacy:` — next M1 batch). No tier changes.
- **H-LAYER / H-A0 transcribed verbatim** into `claims/GATES.md` from Math437
  v1.2 §Hypotheses (the H-LAYER beyond-layer residual is exactly STEP-5B).
- Migration ledger: 23 rows added; B2-feeding rows flagged
  **operator sign-off PENDING** per migration-plan §6.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Bootstrap] Repository structure, governance v2.0, seeded claim ledger — 2026-06-05

- Created the P0/P1/P2 three-tier repository layout (`internal/` local-only,
  repository = public verification surface, `publish/{website,papers}` curated).
- Issued `GOVERNANCE.md` v2.0 integrating the "TOE Proof Governance v1.0" and
  "Verification-First" drafts: Master Theorem + sectors A–F + GAP gates +
  TSv2 tier scale + evidence grades + claim-registration rule + no-overclaim +
  competition-closure + negative-result duty.
- Issued detailed policies under `governance/`: publication tiers, tier system
  (with legacy→TSv2 translation table), claim standard, verification standard,
  naming/versioning, migration plan.
- Seeded 17 claim cards (sectors A–F) translated conservatively from the legacy
  `TOE-FACT-SHEET.md` snapshot of 2026-06-05 (last theory tag Math442):
  Reading-H T5 estimator-grade; Prop-A T6 certified on {H-layer, H-A0};
  legacy-PROVED pillars enter as T6 with T7-candidate flags pending
  verification packages (no auto-T7 rule).
- Seeded `claims/GATES.md` (Step-5b gateway, G3'-b(iii), GAP-1..4 and named
  sub-gates), `predictions/prediction-ledger.md` (all OPEN/SCAFFOLD),
  `negative-results/registry.md` (six seeded entries incl. the Math245
  rollback and the eight failed classical-ħ routes).
- Built `verification/scripts/lint_claims.py` (schema + DAG acyclicity +
  tier-monotonicity/hypothesis rule + `--render` generator for `CLAIMS.md`);
  CI workflow at `.github/workflows/verify.yml`.
- `CLAIMS.md` is generated; hand-editing forbidden.

Maintainer: Jusang Lee <jtkor@outlook.com>
