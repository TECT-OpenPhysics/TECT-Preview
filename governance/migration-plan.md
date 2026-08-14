# Migration Plan -- legacy corpus to verification-first repository

**Issued:** 2026-06-05. **Revised:** 2026-08-14.
**Legacy source:** the separately maintained `E:/Dev/Contents` tree.

The detailed selective-index, assessment, search, and completion rules are in
`governance/legacy-research-knowledge-base.md`.

## 1. Principles

1. **Selective indexing.** A current task, claim, gate, result, or negative
   result selects the legacy sources worth recording. There is no bulk-copy or
   whole-corpus retirement target.
2. **Revalidation at the boundary.** Legacy material enters current proof only
   after its assumptions, conventions, scope, and evidence have been checked
   under TSv2 procedures. Migration itself never promotes a claim.
3. **Exact provenance.** Selected references carry a relative Contents path,
   byte count, SHA-256, assessment, and append-only intake event. Existing
   compatibility copies keep their issued paths.
4. **Negative results are assets.** Refuted or superseded routes are indexed so
   the main proof does not repeat them.
5. **Preserve important selections.** Sources accepted into a reviewed
   main-line batch receive readable repository copies. Unselected corpus
   material remains only in Contents.

## 2. Dispositions

| Disposition | Meaning |
|---|---|
| MIGRATED-VERBATIM | byte-exact compatibility copy under `archive/legacy/` |
| REWRITTEN | current-form note under a claim or theory authority; archive source retained |
| SUPERSEDED | replaced by a later result but retained as lineage |
| DROPPED | excluded with a recorded reason |
| COLD-ARCHIVE | retained in Contents, with no repository copy |

## 3. Workflow

- **M0 -- Maintain source.** Contents continues as the external legacy source;
  new current results land only in TECT.
- **M1 -- Gate-driven selection.** For a live question, freeze a batch and
  index the smallest relevant source and dependency set.
- **M2 -- Revalidate and reconcile.** Extract assumptions, results, failures,
  and contradiction boundaries; reproduce or independently audit as needed.
- **M3 -- Integrate or terminate.** Replace `legacy:` pointers with current
  evidence, a refutation, supersession, reasoned waiver, or terminal archive
  disposition. T7 requires migration-clean claim dependencies.

The process repeats on demand. It does not end by classifying every file in
Contents.

## 4. Priority

1. the active main-proof gate and its direct dependencies;
2. unresolved `legacy:` pointers on current claims;
3. evidence needed by a review or publication package;
4. reusable methods and counterevidence discovered during those audits.

The first post-cutover selection is the T-055 geometry, BCC-refutation,
empty-reference, and truncated-octahedron method set.

## 5. Material not copied by default

- mirrors, backups, merged compilations, VCS internals, and generated outputs;
- superseded process machinery and old website pipelines;
- third-party or licensed paper collections;
- session handoffs, credentials, private operator logs, and large arrays not
  required by a current reproduction package.

Their existence may be noted in planning context, but that is not evidence.

## 6. Quality gate per integrated item

Record the original relative path, disposition, target or source ID, consuming
claim/gate, convention comparison, revalidation evidence or reasoned waiver,
date, and required sign-off. A passing historical script alone is not an
analytic audit or a current physical conclusion.
