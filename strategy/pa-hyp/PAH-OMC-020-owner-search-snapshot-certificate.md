# PAH-OMC-020 / R-528 fixed owner-search snapshot certificate

## Question and scope

This checkpoint repairs the replay boundary exposed by EXP-001646. The
earlier R-526 inventory and v1.0 N2a intake read a changing proof worktree;
later R-527 files therefore changed their computed parent inventories. R-528
freezes a candidate manifest and byte hash instead of rewriting either
historical record.

The scientific target remains the unchanged PAH-OMC-020 ordered stationary
semigroup question. PAH-001, its functional, directed transition rates,
labelled Gibbs state, external Markov time, carriers, regulators and j-before-n
order are unchanged. The snapshot is a repository provenance instrument only.

## Frozen parents

| Parent | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |
| `strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json` | `638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json` | `b87a2d8d7b0009c9f5bd30695823cb442376939ff18c1d48f1d890ae430fe8c7` |
| `strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json` | `dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e` |
| `strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json` | `0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2` |
| `strategy/pa-hyp/PAH-OMC-020-owner-inventory-stable-result-v1.json` | `cfe872fac4517f468061cd5d644cf931e6a7e7294d66ca6a8b2faa6977d37325` |
| `strategy/pa-hyp/PAH-OMC-020-source-multiplicity-underdetermination-result-v1.json` | `89e5239a6817c7046de55d4d9ba934a284ada7b1a7850035bbf63b8f14909c77` |

The fixed snapshot itself is
`strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json` with SHA-256
`86246c253273f5dc1fc630c37c70e7b7b2e3aefcf1fc3d81ae5ad2b0f56cdc35`.
It contains 84 marker-bearing candidate files, manifest digest
`cc3ffdd7f91e2a312c65447a9cf395b8ebfeddb237fc72a643d1f2f7c2f72b36`, and
zero authorized or complete owner markers.

## Replay method

`--check` verifies the frozen 84-path manifest, every candidate byte hash, all
parent hashes, marker bits and the empty authorization/completion sets. It does
not rescan a changing directory. `--detect-new` is a separate explicit scan;
any added, removed or changed candidate requires a new snapshot version.

The v1.1 N2a intake successor pins the current N2b bytes and the snapshot. It
retains the nine required owner-payload fields but remains
`INTAKE_CONTRACT_ONLY` with all claim, gate and physical-promotion firewalls
false.

## Verification

| Lane | Result |
|---|---|
| Primary fixed snapshot | 447/447 PASS |
| Non-importing independent replay | 263/263 PASS |
| Hostile mutation controls | 10/10 PASS |
| N2a successor intake | 23/23 PASS |
| Integrated replay | 20/20 PASS |

The hostile lane rejects injected authorization, completion, source flags,
manifest changes, candidate-byte changes and parent-pin changes. Hashing and
filesystem provenance have no meaningful analytic Lean proposition, so Lean is
explicitly `NOT_APPLICABLE_PROVENANCE_HASHING_ONLY`; no Lean theorem is
claimed here.

## Decision and boundary

Decision: `HOLD_FOR_EVIDENCE`, classification `auxiliary_support`,
`claim_bearing=false`, `active_gate_change=false`, `physical_promotion=false`.

The snapshot establishes a replay-stable, snapshot-time absence of a
source-authorized PAH-OMC-020 owner packet. It does not prove that an abstract
or future owner packet cannot exist. R-526, the v1.0 N2a contract and R-527
remain immutable historical records.

The next question is whether a source owner supplies a versioned packet with
all nine N2a--N2d fields: root-label/multiplicity convention, measurable
common space and `U_n`, local recovery, arbitrary-sequence liminf, recovery
limsup, compact-time boundary escape, R-512 minimal identification and the
independent/hostile verification manifests. Only then can the ordered
stationary semigroup correlation passage be tested.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_owner_packet_snapshot.py --check
python -X utf8 codes/foundations/pah_omc020_owner_packet_snapshot_independent.py --check
python -X utf8 codes/foundations/pah_omc020_owner_packet_snapshot_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_n2a_owner_packet_successor_check.py --check
python -X utf8 verification/scripts/pah_omc020_owner_packet_snapshot_verify.py --check
```

No PAH-OMC-020 temporal convergence, infinite-volume dynamics, physical
Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE
conclusion follows.
