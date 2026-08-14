# archive/ -- curated legacy research area

`archive/legacy/` holds verbatim copies of legacy-corpus files that have been
pulled in by claim demand (`governance/migration-plan.md`). Layout mirrors the
new repository's separation of concerns, grouped by legacy theory tag:

```
archive/legacy/
  notes/<TheoryTag>/      all versions of that tag's notes, together
                          (superseded versions keep their forward-pointer banner)
  scripts/                all migrated verification scripts, FLAT — they import
                          each other as siblings, so this directory is runnable
                          as-is: `cd archive/legacy/scripts && python <script>.py`
  artefacts/<TheoryTag>/  the run JSONs those scripts produced in the legacy repo
```

Originals' paths in the legacy repository are recorded per file in
`archive/MIGRATION-LEDGER.md` (traceability lives in the ledger, not in the
folder structure). `archive/legacy/INDEX.md` is the per-tag lookup table.

Nothing in the compatibility paths is edited. Corrections happen in reviewed
research records, current `theory/` notes, or claim cards that cite these files.
Fresh re-validation artefacts live under `claims/<ID>/runs/`, never in the raw
archive.

The selective knowledge layer introduced on 2026-08-14 adds:

```text
archive/legacy/registry/   selected source identities and reviewed records
archive/legacy/batches/    gate-linked source selections
archive/legacy/references/ readable copies of newly selected important sources
archive/legacy/views/      generated nonempty sector, claim, and gate views
archive/legacy/.search/    rebuildable local hybrid-search cache (gitignored)
```

`E:/Dev/Contents` remains the maintained full corpus. Selected records pin its
relative paths and hashes; important main-line sources receive readable copies
under `references/`. The
`notes/scripts/artefacts` paths remain compatibility copies. Sector and claim
organization is metadata and generated views, so one source can serve several
claims without copy drift. See
`governance/legacy-research-knowledge-base.md`.

If an original important source contains Hangul that cannot appear directly in
tracked files, it is preserved as an ASCII `base64-json` wrapper. The registry,
validator, and search tool decode and verify the exact original bytes.
