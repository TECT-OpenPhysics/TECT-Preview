# A5 T6 canonical baseline hash revalidation certificate

Status: claim-nonbearing provenance checkpoint, 2026-08-25.

## Question

Does the current A5 T6 conditional-composition verifier still reproduce the
published branch-aware package after the canonical synthesis manifest changed
during post-migration maintenance?

## Exact finding

The fresh pre-correction primary lane stopped at
`immutable_t5_manifest_and_bundle_manifest_are_unchanged` because the live T6
baseline expected
`449f090a9d6224b650b45d0e5e9336cf29580aa86a85b1e2eba88561d8699be5`, while the
current canonical synthesis manifest hashes to
`bb691258e0acbc9ba3473883cf5c83f54a830038bc9da2e289f7ab88d3052b5f`. The
published T5 bundle was not the source of the mismatch: its manifest hash is
`ff925591d0a7a110f951d3153dfd854257d7e807c0ace7ee42b34a2ae0789346` and its
recorded digest is
`0dc4a53052ac59d262842b847cb19e6af215f3a744b87049d7066051fa699a6c`.

The correction changed exactly one live expected hash in
`claims/A5-SECTOR-A-SYNTHESIS/conditional_composition_manifest.json`. No
published bundle, theorem source, component hash, or branch statement was
edited. A fresh rerun then produced:

| lane | assertions | result |
| --- | ---: | --- |
| primary | 22/22 | PASS |
| independent | 13/13 | PASS |
| integrated | 35/35 | `A5-T6-CONDITIONAL-COMPOSITION-INTEGRATED-PASS` |

Publication remains `T6-PUBLISHED-OPERATOR-CONFIRMED`.

## Adversarial boundary

- This resolves a current-tree hash/provenance mismatch; it is not a
  mathematical refutation or a new theorem.
- The immutable T5 bundle remains byte-for-byte authoritative history.
- The independent lane is a fresh non-importing audit, not a restatement of the
  primary result.
- A5 remains exactly its seven-hypothesis branch-aware conditional package;
  scalar and full-production mass anchors are not identified.
- Nothing here closes A6 counterterm/full-field concentration, A7, the Q3
  unbounded common-core or source/volume-uniform modular-history gates, common
  alpha, OS/KMS/GNS, the physical gap, continuum, C6, Sector A physical
  closure, Pre-A, or any Clay obligation.

## Reproduction

```text
python -X utf8 codes/foundations/a5_t6_conditional_verify.py
```

The append-only route record is `EXP-001093` in `explorations/log.jsonl`.
