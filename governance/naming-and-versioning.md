# Naming and Versioning (binding)

**Issued**: 2026-06-05.

## 1. Repository root

Only these files may exist at root: `README.md`, `GOVERNANCE.md`, `ROADMAP.md`,
`REVIEWING.md`, `CLAIMS.md` (generated), `CHANGELOG.md`, `CLAUDE.md`,
`.gitignore`. Everything else has a destination folder; when unsure, the
decision table in `governance/publication-tiers.md` applies.

## 2. Claim IDs

`<Sector><n>-<SLUG>`, immutable, never reused (see
`governance/claim-standard.md` §2).

## 3. Theory notes (Markdown + LaTeX)

- Path: `theory/sector-<X>-<name>/<claimID>-<slug>-v<major>.<minor>.md`
  (e.g. `theory/sector-B-vacuum/B1-RH-ENUM-step5b-bound-v1.0.md`).
- New notes start at `v1.0` explicitly.
- **Versioned re-issue, not patch layering**: a revision is a new file at the
  bumped version carrying a cumulative revision-history banner; the superseded
  file gets exactly one forward-pointer line at the top
  (`> SUPERSEDED by <file>`) and is otherwise immutable.
- Minor bump = corrections/audit patches; major bump = consolidation re-issue.
- Unversioned citations mean the latest version; papers pin versions.
- Math display: GitHub-renderable `$...$` / `$$...$$`. Full LaTeX sources
  belong to `publish/papers/`.

## 4. Gates

Gate IDs are uppercase slugs registered in `claims/GATES.md`
(e.g. `STEP-5B`, `G3PB-III`, `GAP-2`). A gate referenced by any card must
exist in the registry.

## 5. Codes and scripts

- Domain codes: `codes/<domain>/<name>.py` with module docstring stating
  purpose, claim IDs served, and reproduction role.
- Verification harness: `verification/scripts/`, tests in
  `verification/tests/` (`pytest` discoverable, `test_*.py`).
- Every code change that affects a claim's evidence updates the claim card in
  the same commit.

## 6. Runs

`runs/<claim-id>/<YYMMDD>-<tag>/result.json` (+ git-ignored bulk files).
The folder name's claim ID must exist.

## 7. Papers

`publish/papers/<paper-id>/` where `<paper-id>` is a short slug
(e.g. `P1-vacuum-selection`). Repository tags `paper/<paper-id>/v<N>` freeze
cited claim sets.

## 8. Migration artefacts

Legacy files keep their original filenames under `archive/legacy/<original
relative path>` for traceability; rewritten/modernised versions live in
`theory/` under the new scheme with the archive copy cross-referenced.

## 9. Commits

- Signature: `git -c user.email="jtkor@outlook.com" -c user.name="Jusang Lee"`.
- Message style: `<area>: <imperative summary> [<claim IDs>]`.
- One logical change set per commit; the claim-standard atomic set (card +
  changelog + regenerated ledger) never splits across commits.
- Milestones (packet releases, paper freezes, stage closures) get annotated
  tags.
