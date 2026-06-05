# archive/ — curated legacy migration area

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

Nothing here is edited — ever. Corrections happen in `theory/` notes or claim
cards that cite these files. Fresh re-validation artefacts live under
`runs/<claim-id>/`, never here.
