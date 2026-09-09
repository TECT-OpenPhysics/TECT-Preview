# PAH-OMC-020 / R-526 stable owner-inventory certificate

## Scope

R-526 is a provenance and replay-stability audit for the PAH-OMC-020 N2a/N2b
owner-packet intake. It does not alter PAH-001, the R-510/R-511/R-512 source
chain, the R-525 comparison candidate, any transition rate, the state, the
carrier, the external Markov time, or the declared j-before-n order.

The earlier owner-history JSON embedded the complete output of
`git fsck --unreachable`. That output depends on dangling objects in a dirty
proof worktree and therefore cannot serve as a stable byte-level replay input.
R-526 replaces that operational check only with a sorted reachable-history path
inventory and frozen source hashes. No mathematical inference is taken from
the absence of dangling objects.

## Frozen sources

| Source | SHA-256 | Role |
|---|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` | immutable PAH model |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` | temporal target |
| `strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json` | `638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a` | required owner payload |
| `strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json` | `dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e` | R-525 candidate |
| `strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json` | `0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2` | R-525 result |

## Finding

The intake remains `INTAKE_CONTRACT_ONLY` with
`source_authorized_packet_present=false`. R-525 remains
`RESEARCHER_OWNED_CANDIDATE_ONLY`, with no source authorization. The bounded
current inventory contains no JSON object declaring
`source_authorized_packet_present=true` and no completed owner status. The
reachable-history path inventory contains 772 paths under the declared proof
roots; its deterministic list hash is
`7ffdbc413f58f0270efda3afabd3e6b205f0e7de3c807aa3af18ce75019a3333`.

This is an evidence hold, not a universal nonexistence result. It only says
that the current and reachable repository inventory does not contain the
required owner packet.

## Verification

| Lane | Status | Assertions | Artifact SHA-256 |
|---|---|---:|---|
| primary | `PASS_STABLE_OWNER_INVENTORY` | 14/14 | `e4ed74bed72b1b30a13ea059e51fab87af540ce85bc45515da6384b0e2a2ecf2` |
| independent | `PASS_INDEPENDENT_STABLE_OWNER_INVENTORY` | 12/12 | `80e5d84f0cd24116e3a4bdb840e2bed2a1bbf383d9560c8ee9e9dc04b73c26ff` |
| hostile | `PASS_HOSTILE_STABLE_OWNER_INVENTORY_CONTROLS` | 8/8 | `6f94a3e775a7f42295742a9c9cd06c5a1e9f351fb4d1892e86623518ade85857` |
| integrated | `PASS_INTEGRATED_STABLE_OWNER_INVENTORY` | 22/22 | `11e8c9637001e701d6f72b86b7100b458634462504c754607b641bbff08db772` |
| N2b consumer | `PASS_SCOPED_N2B_AUDIT` | 22/22 | `b87a2d8d7b0009c9f5bd30695823cb442376939ff18c1d48f1d890ae430fe8c7` |

The hostile lane mutates the authorization and completion fields and confirms
that the inventory would detect either mutation. The integrated lane also
rechecks the R-525 integrated finite Lean cross-check; this audit introduces no
new analytic or physical Lean theorem. The N2b common-space consumer now pins
the stable inventory result rather than the workspace-dependent owner-history
JSON and replays its scoped `HOLD_FOR_EVIDENCE` audit at 22/22.

## Decision and next question

Decision: `HOLD_FOR_EVIDENCE`, classification `auxiliary_support`,
`claim_bearing=false`, `active_gate_change=false`, `physical_promotion=false`.

Next single question: can a source owner authorize the exact R-525 maximal-
prefix `U_n` and provide the PAH-specific energy intertwining required for
N2b, N2c/N4 and N2d without changing PAH-001?

Reopen only when a versioned signer/authority, SHA-256-pinned packet, common
measure/Hilbert realization, energy estimate, and independent/hostile/Lean
verification are supplied. Until then, do not repeat finite tables or promote
the candidate to a temporal, continuum, physical, QFT, gravity, Yang--Mills,
mass-gap, or TOE statement.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_owner_packet_inventory_stable.py --check
python -X utf8 codes/foundations/pah_omc020_owner_packet_inventory_stable_independent.py --check
python -X utf8 codes/foundations/pah_omc020_owner_packet_inventory_stable_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_owner_packet_inventory_stable_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
python -X utf8 verification/scripts/pah_omc020_n2b_common_space_audit.py --check
```
