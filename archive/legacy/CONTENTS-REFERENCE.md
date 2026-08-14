# Contents corpus planning reference

**Observed:** 2026-08-14
**Role:** historical planning context, not a migration denominator or proof authority

`E:/Dev/Contents` remains the separately maintained full legacy corpus. TECT
does not need a wholesale copy of that tree. The current repository retains
selected path/hash metadata, reviewed assessments, gate-linked source sets,
and readable copies of sources judged important to the main research line.

## One-time census

The 2026-08-14 read-only audit observed:

- 7,503 paths and 834,218,101 bytes in the complete Contents tree;
- 1,426 research-heavy files and 201,085,721 bytes under the principal
  `Docs/math`, `Docs/supplementary`, `Codes`, and `Runs` areas;
- 695 files under `Docs/math`;
- substantial duplication in Git, Website, Backup, merged-volume, VCS, and
  generated-output branches.

These counts are deliberately not tracked path by path and may drift as
Contents is maintained. They explain why indiscriminate migration would add
weight without improving proof quality.

## Retention rule

A legacy source enters the tracked selective index only when a live task,
claim, gate, result, or negative-result question names why it is useful. Its
relative Contents path and SHA-256 pin the reviewed bytes. Important selected
sources receive a readable copy under `archive/legacy/`; unselected material
stays only in Contents. This makes the eventual main line self-contained
without importing the entire corpus.

Search results and assessments are discovery aids. They cannot promote a
claim, close a gate, or replace current-convention revalidation.
