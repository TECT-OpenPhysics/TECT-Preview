# Naming and Versioning (binding)

**Issued**: 2026-06-05.

## 1. Repository root

Only these files may exist at root: `README.md`, `GOVERNANCE.md`, `ROADMAP.md`,
`REVIEWING.md`, `CLAIMS.md` (generated), `CATALOG.md` (generated),
`CHANGELOG.md`, `CLAUDE.md`, `.gitignore`. Everything else has a destination folder; when unsure, the
decision table in `governance/publication-tiers.md` applies.

## 2. Claim IDs

`<Sector><n>-<SLUG>`, immutable, never reused (see
`governance/claim-standard.md` §2).

## 3. Notes and synthesis documents

- **Human-readable naming rule (binding, 2026-06-05 operator directive)**:
  file and folder names lead with a DESCRIPTIVE English slug. Internal codes
  (claim IDs, gate IDs, migration-phase labels) are never the only identifying
  token of a filename, folder name, or document heading — codes belong to the
  registry layer (`claims/<ID>/`, `status.json`, `GATES.md`); a document's
  claim linkage comes from its location and its result footer, not its name.
  In document bodies, expand every code at first use — e.g. "migration batch 1
  (plan phase M1)" — after which the short code may be used.
- **Issue dates in the filename — two-date rule (binding)**: the first issue
  carries its first-issue date: `<slug>-<YYMMDD-first>-v1.0.md`. Every LATER
  version carries BOTH dates — the first-issue date (lineage anchor, never
  changes) and that version's own issue date:
  `<slug>-<YYMMDD-first>-<YYMMDD-this-version>-v<major>.<minor>.md`.
  Example: `beyond-layer-class-bound-260607-v1.0.tex.txt` → revised on
  2026-07-12 → `beyond-layer-class-bound-260607-260712-v1.1.tex.txt`. The filename thus shows at
  a glance when the document was born and how current the version is; the
  revision-history banner still records the full per-version date list.
- **Proof-note format: `.tex.txt` (binding, 2026-06-05 operator decision,
  revisits the bootstrap `.md` choice).** Working proof notes are LaTeX BODY
  FRAGMENTS (no `\documentclass`), extension `.tex.txt`. Rationale: (i) full
  math fidelity — theorem environments, `align`, labels/refs, macros — which
  GitHub's Markdown math cannot deliver for proof-grade content; (ii)
  uniformity with the legacy corpus (~440 `.tex.txt` notes, incl.
  `archive/legacy/notes/`); (iii) one-command PDF:
  `python verification/scripts/build_note_pdf.py <note>` validates the
  standard form, wraps with `verification/templates/note-preamble.tex`,
  compiles in a TEMPORARY directory (intermediates never touch the
  repository), and places the PDF **next to its source**
  (`claims/<ID>/notes/<stem>.pdf`). Only the current version's PDF is kept;
  superseded PDFs are removed on re-issue (sources remain, so every PDF is
  reproducible). **Web readability is the claim card's job**: the `.md` card
  carries the statement/scope/falsifier for browser reading; the note is the
  formal document.
- **Standard note form (binding, 2026-06-05; machine-enforced by
  `build_note_pdf.py` FORM-CHECK)** — authoring skeleton:
  `verification/templates/note-skeleton.tex.txt`.
  Banner fields (leading `%` block): `% Title:` (the proper human-readable
  title — the PDF title is NEVER the filename), `% Claim:` (primary claim ID
  first), `% Version: vN.M -- first issued YYYY-MM-DD; this version issued
  YYYY-MM-DD` (rendered in the PDF date field as
  "first issued D1 · this version issued D2 · vN.M"), `% Status:`, and the
  cumulative `% Revision history`. The builder CROSS-CHECKS banner
  version/dates against the two-date filename and refuses on mismatch.
  Mandatory sections: "Purpose and scope"; content sections (Statement /
  Setting and hypotheses / Proof for theorem notes; Procedure / Results for
  records); "Numerical verification" whenever the note contains numbers;
  "Devil's-advocate" (three objections minimum); "Result footer" in a
  `verbatim` block.
- **Working proof notes** live WITH their claim:
  `claims/<ID>/notes/<descriptive-slug>-<YYMMDD>-v<major>.<minor>.tex.txt`
  (e.g. `claims/B1-RH-ENUM/notes/beyond-layer-class-bound-260607-v1.0.tex.txt`).
  A note serving several claims lives under its primary claim with
  cross-references from the others.
- **Standard LaTeX only + width-bounded tables (binding, 2026-06-05)**:
  fragments must compile under the standard wrapper template alone
  (`verification/templates/note-preamble.tex`, which loads only TeX Live
  required/tools packages: amsmath/amssymb/amsthm, geometry, array, tabularx,
  booktabs, url, hyperref). Per-note preambles or exotic packages are
  forbidden — a note needing more EXTENDS THE TEMPLATE (one place, audited).
  **Every table is width-bounded**: `tabularx{\textwidth}` with the wrapping
  `Y` column type (or fixed `p{}` widths summing below `\textwidth`);
  unbounded `l/c/r` columns holding prose are forbidden. Long repository
  paths are set with `\url{}` (breaks at separators). Acceptance criterion:
  the PDF build log shows ZERO `Overfull \hbox` (`build_note_pdf.py` prints
  the count). Reference case: the batch-1 record v1.1 built with 7 overfull
  boxes; the v1.2 width-compliance re-issue builds with 0.
- **Markdown stays the format for web surfaces**: claim cards, registries,
  policies, READMEs, and Layer-2 synthesis documents
  (`theory/sector-<X>-<name>/<descriptive-slug>-synthesis-<YYMMDD>-v<major>.<minor>.md`)
  — light math, browser-first. When a synthesis matures toward publication it
  transitions to LaTeX under `publish/papers/`.
- Both kinds: new files start at `v1.0` explicitly.
- **Versioned re-issue, not patch layering**: a revision is a new file at the
  bumped version carrying a cumulative revision-history banner; the superseded
  file gets exactly one forward-pointer line at the top
  (`> SUPERSEDED by <file>`) and is otherwise immutable. All versions are kept.
- Minor bump = corrections/audit patches; major bump = consolidation re-issue.
- Unversioned citations mean the latest version; papers pin versions.
- Math display: GitHub-renderable `$...$` / `$$...$$`. Full LaTeX sources
  belong to `publish/papers/`.

## 4. Gates

Gate IDs are uppercase slugs registered in `claims/GATES.md`
(e.g. `STEP-5B`, `G3PB-III`, `GAP-2`). A gate referenced by any card must
exist in the registry.

## 5. Codes and scripts — versioned IN PLACE, never by filename re-issue

Code carries the same date+version management as documents, but through a
different mechanism, because code is imported and executed:

- **No filename re-issue for code (binding).** A dated/versioned copy
  (`solver-260605-v1.1.py`) would break every importer and reproduction
  command on each bump, and side-by-side copies let stale physics keep
  running — the legacy corrected-convention cascade (Math426/G6) is the
  canonical example of the stale-copy failure class. Code evolves in place;
  git holds the full line-level version history.
- **Mandatory version header** on every new or edited script under `codes/`
  and `verification/`:

  ```python
  __version__ = "1.0.0"
  __first_issued__ = "2026-06-05"
  __version_issued__ = "2026-06-05"
  __claims__ = ["B1-RH-ENUM"]   # claim IDs served (optional)
  ```

  Any behaviour-affecting change bumps `__version__` + `__version_issued__`
  and adds a line to the module-docstring changelog. `__first_issued__` is the
  lineage anchor and never changes (same semantics as the document two-date
  rule).
- **Results are immutable**: a run is never edited — a new run gets a new
  `claims/<ID>/runs/<YYMMDD>-<descriptive-tag>/` folder. Every artefact records
  the producing scripts' `__version__` values (and git commit when available),
  so result → code-version → code-history is a complete provenance chain
  (`governance/verification-standard.md` §4).
- **Uniform visibility**: `build_catalog.py` parses these headers (and run
  artefact dates), so documents, code, and results all show first-issue /
  version-issue / version columns in `CATALOG.md` in the same way.
- Archive scripts (`archive/legacy/scripts/`) are verbatim-immutable: no
  headers are added; their dates live in the migration ledger.
- Domain codes: `codes/<domain>/<name>.py`; harness: `verification/scripts/`;
  tests: `verification/tests/test_*.py`. Every code change that affects a
  claim's evidence updates the claim card in the same commit.

## 6. Runs

`claims/<ID>/runs/<YYMMDD>-<descriptive-tag>/result.json` (+ git-ignored bulk
files). The folder name's claim ID must exist; the tag is descriptive English
words (e.g. `260605-migration-revalidation`), never a bare internal code.

## 7. Papers

`publish/papers/<paper-id>/` where `<paper-id>` is a short slug
(e.g. `P1-vacuum-selection`). Repository tags `paper/<paper-id>/v<N>` freeze
cited claim sets.

## 8. Migration artefacts

Legacy files keep their original filenames and live in the per-tag layout
`archive/legacy/{notes/<TheoryTag>/, scripts/, artefacts/<TheoryTag>/}`;
the original legacy path is recorded in `archive/MIGRATION-LEDGER.md` (that is
where traceability lives), and `archive/legacy/INDEX.md` maps tags to files
and consuming claims. Rewritten/modernised versions live in
`claims/<ID>/notes/` under the new scheme with the archive copy cross-referenced.

## 9. Commits

- Signature: `git -c user.email="jtkor@outlook.com" -c user.name="Jusang Lee"`.
- Message style: `<area>: <imperative summary> [<claim IDs>]`.
- One logical change set per commit; the claim-standard atomic set (card +
  changelog + regenerated ledger) never splits across commits.
- Milestones (packet releases, paper freezes, stage closures) get annotated
  tags.
