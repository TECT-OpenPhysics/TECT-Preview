# Legacy research registry

- `sources/` contains one JSON record per selected Contents path occurrence.
- `records/` contains reviewed research-unit assessments.
- `schema.json` defines the required machine contract.

Contents remains the maintained full corpus. Existing compatibility copies and
new readable reference copies are verified locally; selected origins can also
be checked against Contents with
`legacy_research.py verify-selected --source-root PATH`.
Source selection, assessment, revalidation, and current-proof integration are
independent states. Generated documents under `../views/` and
`../RESEARCH-INDEX.md` must not be hand-edited.
