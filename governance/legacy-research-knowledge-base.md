# Selective legacy research reference policy

**Status:** binding for legacy research intake after 2026-08-14. This policy
refines `governance/migration-plan.md` and changes no claim tier or lifecycle.

The rollout gate is
`LEGACY-SELECTIVE-INDEX-AND-ON-DEMAND-REVALIDATION`, owned by `T-057`.

## 1. Purpose and authority boundary

`E:/Dev/Contents` remains a separately maintained source corpus. TECT does not
copy or classify that complete tree merely to declare migration complete.
Instead, a live task, claim, gate, result, or negative-result question selects
the small source set worth preserving and reviewing. Sources accepted as
important to the main line receive readable repository copies.

Four levels remain distinct:

1. selected source metadata: relative Contents path, byte count, SHA-256, and
   any existing compatibility copy;
2. a reviewed assessment of legacy claims, assumptions, results, failures,
   contradictions, and reusable methods;
3. current-convention reproduction or independent revalidation;
4. explicit integration into a current claim, result, or negative authority.

Indexing, summarizing, or search ranking never promotes a claim.

## 2. Tracked structure

Existing files under `archive/legacy/notes/`, `scripts/`, and `artefacts/`
remain immutable compatibility and reproduction paths. They must not move
because current claim cards, code, and issued bundles cite them.

```text
archive/legacy/
  registry/sources/<source-id>.json   selected path/hash metadata
  registry/records/<record-id>.json   reviewed research assessments
  references/<origin-path>            readable copies of newly selected sources
  migration/events.jsonl              append-only intake decisions
  batches/<batch-id>/manifest.json    gate-linked selection contract
  batches/<batch-id>/source-set.json  exact selected path/hash set
  views/                               generated nonempty sector/claim/gate views
  RESEARCH-INDEX.md                    generated compact entry point
  CONTENTS-REFERENCE.md                dated planning context only
  .search/                             rebuildable local search cache, ignored
verification/legacy-research-index.json
```

TECT stores no duplicate raw-object vault and no tracked complete Contents
inventory. Existing compatibility copies remain in place; newly selected
important sources are copied once under `references/` using their readable
origin hierarchy. Unselected material remains only in Contents.

## 3. Source identity and integrity

- A source ID identifies one relative Contents path occurrence.
- SHA-256 pins the exact bytes reviewed at intake.
- Machine-specific absolute Contents paths are never tracked.
- `compatibility-copy` means an existing immutable archive file carries the
  same bytes and is verified during the release gate.
- `reference-copy` means a newly selected important source has a readable,
  hash-verified copy under `archive/legacy/references/`.
- A selected source containing Hangul or other bytes forbidden by the tracked
  English-only rule is stored as an ASCII `base64-json` wrapper beside its
  logical origin hierarchy. Validators and search decode the wrapper and check
  the original byte count and SHA-256; the source is preserved, not translated.
- `contents-reference` means Contents carries the bytes; the tracked record is
  metadata only and its preservation axis is `inventoried`; this is a triage
  state, not the final state for a source used by a reviewed main-line record.
- `verify-selected --source-root PATH` verifies only the selected references,
  not the complete source tree.

If Contents changes at a selected path, the old hash remains provenance. A new
assessment version or migration event must explain whether to re-pin, retain,
or reject the changed source.

## 4. Independent status axes

No scalar status may conflate copying with proof.

| Axis | Values |
|---|---|
| preservation | `inventoried`, `verified-copy`, `missing` |
| extraction | `pending`, `reviewed`, `needs-review` |
| revalidation | `not-run`, `pass`, `fail`, `waived`, `not-applicable` |
| integration | `unmapped`, `mapped`, `candidate`, `integrated`, `terminal` |

The assessment and evidence-role fields separately distinguish reusable
material, counterevidence, methods, provenance, dependencies, and context.

## 5. Assessment requirements

A reviewed research record names its exact source IDs and records:

- purpose, neutral legacy conclusion, and mapping to sectors, claims, and gates;
- assumptions, conventions, ensemble, regulator, domain, and limit order;
- achievements, negative or inconclusive findings, and contradictions;
- reusable mathematics, code, data, or method components;
- current assessment, evidence role, TSv2 ceiling, no-overclaim boundary, and
  next revalidation action.

Contradictions are retained, not silently resolved in favor of a preferred
route. Generated views are disposable navigation and never a second claim
registry.

## 6. Search policy

Local search may combine deterministic chunking, SQLite FTS5, hashed TF-IDF,
and an optional pinned multilingual embedding model. It resolves an existing
compatibility copy first, then an explicit source root, the
`TECT_LEGACY_SOURCE_ROOT` environment variable, or the sibling `Contents`
folder. Size and SHA-256 are checked before indexing or querying.
Raw and `base64-json` reference copies are decoded through the same verified
source interface, so encoded preservation does not reduce retrieval coverage.

Every hit returns source and line provenance and carries the warning
`legacy discovery result; not current proof`. Dense semantic search must be
reported as unavailable until a model ID, revision or file hash, tokenizer,
dimension, normalization, and build command are pinned.

## 7. Gate-linked workflow

1. Freeze the current task/claim/gate question.
2. Select only sources relevant to that question and its necessary dependency
   closure.
3. Pin paths and hashes and preserve important selected sources at readable
   repository paths.
4. Extract claims, assumptions, evidence, failures, and contradictions.
5. Re-run or independently audit under current conventions, or record an exact
   reasoned waiver.
6. Integrate survivors only through current claim/result/negative authorities.
7. Regenerate nonempty views and catalogs and run the release gate.

The first T-055 batch remains a useful source set: it separates BCC-selection
counterevidence from reusable truncated-octahedron Brillouin-zone methods. Its
intake does not establish a physical vacuum or close C6.

## 8. Completion criterion

T-057 closes when:

- material relevant to active proof gates is findable through selected source
  metadata and reviewed assessments;
- every load-bearing legacy import is revalidated, rejected, superseded, or
  explicitly waived before integration;
- unresolved `legacy:` claim pointers receive a current terminal disposition;
- search and generated views preserve provenance and no-overclaim boundaries.

There is no requirement to copy, assess, or terminally classify every Contents
file. The dated whole-corpus census is retained only as planning context.

## 9. Compatibility cutover

Migration batches 1--4 and their 66 archive payloads remain valid at their
recorded scope. The Markdown ledger and tag index remain compatibility
authorities for those batches. Later work uses selected source cards,
assessments, gate-linked batches, and append-only migration events without
changing existing archive bytes or paths.
