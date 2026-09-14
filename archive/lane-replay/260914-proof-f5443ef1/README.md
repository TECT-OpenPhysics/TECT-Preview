# Fixed follow-up proof replay, 2026-09-14

This archive records integration provenance only, not a new scientific result
or a mathematical review. It integrates fixed source checkpoint
`f5443ef1c489a445d648dabebcdb2b05c6dfc799` into canonical main
`9885cad4aa25635f05e9f5dadf391f4c3aac751f`.

## Scope and predecessor

Only the source suffix after `e8a284f65b92563bf12cd42fa3ad5d542f4a2c70`
is imported. That predecessor was already integrated with source-qualified
replay in `archive/lane-replay/260909-proof-e8a284f6/`.
The previous crosswalk is preserved byte-for-byte and hash-pinned here.
Its identity map is inherited for references to earlier source records; only
the new suffix receives new sequential canonical IDs. This does not replay
the earlier checkpoint again or renumber any existing canonical record.

The original source workspace and commit are not modified. All canonical
publication files are retained. The separate paper1-submit request is excluded.
R-574 retains its source DISPROVED verdict, negative_result classification and
claim_bearing true, limited to the fixed PAH-v2 counting-Gibbs / Markov-time /
CRT-map target. Its active_gate_change, host_claim_promoted and
physical_promotion remain false. No additional research, successor or goal is
activated by this integration. External referee review and submission to a
journal are not asserted.

## Exact-byte provenance

`source-explorations.jsonl` is the exact incoming source suffix.
`source-temporal-corrections.jsonl` preserves the full source time sidecar.
`crosswalk.json` records source commit, original ID, raw-line SHA-256,
fresh canonical replay ID, inherited mappings and protected-file hashes.

Bare EXP labels in unchanged proof artifacts and changelog payloads remain
source-qualified identities, not references to unrelated canonical paper
records with the same labels. Structured related edges and explicit exploration
locators in replay records use both the inherited and new mappings.
Scientific fields and proof bytes are not rewritten.

Replay records are historical-backfill imports, labelled Checkpoint replay.
Their import date is not a new scientific review date. Original metadata and
any UNKNOWN timestamp disposition remain in qualified provenance.
The canonical temporal sidecar is retained unchanged.

## Reproduce

```text
python -X utf8 archive/lane-replay/260914-proof-f5443ef1/verify.py --self-test --check
```

After the integration commit exists, add `--require-ancestry`.
The audit verifies source and canonical prefixes against fixed Git objects,
the predecessor crosswalk and mapping, exact original lines and temporal
sidecars, translated references, protected scientific/publication bytes and
the lossless changelog union. It is a snapshot preservation audit, not a
requirement that future scientific revisions keep every authority unchanged.
Release and strict current-note PDF checks remain separate mandatory gates.

## Adversarial operational review

- Identity collision: source commit and original line hash disambiguate labels.
  Existing canonical identities are never renumbered.
- Predecessor reference: the inherited map is checked against the immutable
  prior crosswalk, not rebuilt from colliding current labels.
- Missing or modified science: tests change a finding and remove a record;
  payload and fixed-Git-object byte checks reject them.
- Reference corruption: tests change an evidence locator and related edge;
  both must fail validation.
- False fresh-review attribution: a contemporaneous provenance mutation is
  rejected. Import metadata is not independent scientific evidence.
- Ancestry and concurrency: both fixed parent heads must remain ancestors;
  canonical promotion rechecks its base and clean index under the release lock.

Independent operational review is invited. Passing this audit does not replace
external mathematical review, establish novelty or promote a physical claim.
