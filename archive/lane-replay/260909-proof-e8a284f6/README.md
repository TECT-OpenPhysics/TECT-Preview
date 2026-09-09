# Fixed proof-checkpoint replay, 2026-09-09

This is integration provenance, not a new mathematical result or a new proof
review. It combines the already recorded proof checkpoint
`e8a284f65b92563bf12cd42fa3ad5d542f4a2c70` with canonical main
`cfca9f789759bc613fdf807058f6f361b485cd82`. Their common ancestor is
`0775b22a9e567c1ac426cc8ce29bea7b6bc55a78`.

## Identity and immutable evidence

The two lanes used different records under some identical `EXP` labels after
their common prefix. The existing canonical paper records retain their original
IDs and bytes. The proof source commit, source workspace, scientific artifacts,
and original exploration IDs are not rewritten.

`source-explorations.jsonl` retains exactly the incoming proof suffix, including
its original line endings. `source-temporal-corrections.jsonl` retains the exact
proof-side temporal sidecar. `crosswalk.json` supplies source commit, original
line hashes, canonical replay IDs, and file-preservation inventories.

An old `EXP` label in an unchanged proof certificate, run, script, task, or
changelog payload belongs to the qualified identity `(source commit, old ID)`.
It must not be resolved to the unrelated paper record solely by its bare label.
Use the crosswalk. New replay records use canonical IDs in structured `related`
edges and explicit exploration evidence locators. Other scientific prose and
the verdict are retained, not independently re-established by integration.

Replay records are marked `historical-backfill` and named `Checkpoint replay`.
Their current `recorded_at` and `reviewed_on` describe the integration event,
not the original proof review. Original review/timestamp/author/provenance text
and any `UNKNOWN` timestamp disposition remain in the qualified source metadata.
The original proof temporal corrections must not be applied to same-named paper
records; the canonical temporal sidecar is preserved unchanged.

These replay records are not additional independent scientific advances.
R-568 retains its fixed-H, conditional, auxiliary-support scope. No T-054/C6,
physical Pre-A, QFT, gravity, continuum or external-review promotion is made.
PAH-OMC-030 is not activated, and the separate paper1-submit request is excluded.

## Reproduce the preservation audit

From this checkout, with the fixed Git commits available:

```text
python -X utf8 archive/lane-replay/260909-proof-e8a284f6/verify.py --self-test --check
```

After the merge commit exists, add `--require-ancestry` to check that both source
heads are ancestors of `HEAD`. The audit checks exact source suffix/sidecar
bytes, original and replay identities, unchanged scientific payload fields,
backward edge translation, protected proof and main publication files, and
lossless changelog union. It is a snapshot audit, not an assertion that later
scientific revisions must keep these files permanently unchanged.

The canonical linter is retained: both branches implemented explicit LF output;
their remaining changes are local variable naming and diagnostic punctuation.
All conflicted generated surfaces are rebuilt from authorities, not text-merged.
No expected scientific hash or validation threshold is changed.

## Adversarial operational review

- Identity collision: source commit plus raw-line hash identifies the original;
  a colliding bare ID is never taken as evidence equality.
- Missing/changed proof content: payload and file-hash checks fail rather than
  rewriting old expectations. Tests change a finding and remove a record.
- Wrong reference translation: tests change a related edge and a located
  exploration reference; validation rejects both.
- False new-proof attribution: replay labels and qualified timestamp metadata
  are checked, and a fabricated fresh-review label is rejected.
- Main/proof ancestry: the final optional Git check requires both fixed heads;
  it does not use a moving worker index or permit a force push.

Independent operational review of this provenance mapping is invited. It is
not a substitute for mathematical or external referee review.
