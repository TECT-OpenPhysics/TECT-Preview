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

## 3. Notes and synthesis documents (Markdown + LaTeX)

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
  Example: `beyond-layer-class-bound-260607-v1.0.md` → revised on 2026-07-12 →
  `beyond-layer-class-bound-260607-260712-v1.1.md`. The filename thus shows at
  a glance when the document was born and how current the version is; the
  revision-history banner still records the full per-version date list.
- **Working proof notes** (successor of legacy Math notes) live WITH their
  claim: `claims/<ID>/notes/<descriptive-slug>-<YYMMDD>-v<major>.<minor>.md`
  (e.g. `claims/B1-RH-ENUM/notes/beyond-layer-class-bound-260607-v1.0.md`).
  A note serving several claims lives under its primary claim with
  cross-references from the others.
- **Theory synthesis documents** (Layer 2, `theory/README.md`):
  `theory/sector-<X>-<name>/<descriptive-slug>-synthesis-<YYMMDD>-v<major>.<minor>.md`
  — consolidated exposition citing only claim IDs at registered tiers.
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
  `runs/<claim-id>/<YYMMDD>-<descriptive-tag>/` folder. Every artefact records
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

`runs/<claim-id>/<YYMMDD>-<descriptive-tag>/result.json` (+ git-ignored bulk
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
