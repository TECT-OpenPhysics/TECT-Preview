# PAH-OMC-023 owner-authorized successor admission certificate

## Decision

`R-560` is `HOLD_FOR_EVIDENCE`. The current hash-pinned R-554 manifest has a
192-record candidate set but no `authorized_paths` and no `complete_paths`.
The previous v1.4 integrated replay mismatch is not a mathematical failure: it
was caused by absolute interpreter and output paths stored in replay metadata.
A new canonical-path intake replay now passes without changing the frozen child
artifacts or importing any successor model.

## Pinned scope

- `PAH-001-v1.json`: SHA-256
  `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`.
- R-554 snapshot: SHA-256
  `47b0879ff4c55fe3d60a11cd744d6920a3e3eb18bf923cdd4782fa7e7674b4e9`.
- R-554 result: SHA-256
  `54329df2a6d3ca766f6ca24fbcc628263e6c7e8c2c0e8c8eba545f3508d75df7`.
- PAH-OMC-023 contract: SHA-256
  `a21e6235bc68f7760c83ffa98657a787258d906b39e482c79a1646b2b6da107a`.

The displayed PAH functional, rates, Gibbs state, carrier, external stochastic
Markov time and j-before-n order remain unchanged. No finite witness, carrier,
root convention, refinement, counterterm or physical limit is introduced.

## Replay evidence

The current environment replays the three frozen R-554 child artifacts with
stable relative command descriptions. The independent lane recomputes the
candidate manifest and every candidate byte hash. The hostile lane rejects
status-only authorization, completion, provenance, manifest, byte-hash and
ordering mutations.

- primary: `29/29`
- independent: `783/783`
- hostile: `11/11`
- integrated: `24/24`

Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc023_owner_admission_verify.py --check
```

This resolves only the historical replay-path mismatch. It does not create or
admit an owner packet.

## Boundary and next question

The next required evidence is one source-authorized or explicitly owner-
authorized, hash-pinned packet containing root multiplicity and measure,
common realization, R-557 N1, N2b, N2c/N4, N2d, full-domain `J` and anchored
`D`, plus independent, hostile and Lean manifests. Until that packet exists,
the PAH-OMC-020 ordered convergence question remains open.

No R-512 convergence, infinite-volume, continuum, physical Pre-A, spacetime,
QFT, gravity, Yang--Mills, mass-gap or TOE conclusion is made.