# PAH-OMC-020 current-byte owner-search snapshot v1.3

## Question

After the R-545 mesh-to-uniform and R-546 direct two-term checkpoints, does
the current `strategy/pa-hyp` corpus contain a source-authorized and complete
owner packet for the anchored-`n` comparison with the R-512 minimal closed
form?

## Frozen scope

PAH-001, its original directed PH/LK/AP/TR rates, the labelled Gibbs state,
external stochastic Markov time and the preregistered `j`-before-anchored-`n`
order remain unchanged.  A fresh current-byte snapshot was created at
`2026-09-08T04:18:10Z` with snapshot id
`PAH-OMC-020-OWNER-SEARCH-SNAPSHOT-003`.  The marker-bearing corpus contains
164 candidate files and manifest SHA-256
`ee56276cb87bd1c95f3230ab581b38151c94b92e85f5897b328612a5a6c3ed30`.
The snapshot file SHA-256 is
`f2bea35647f54f305ac1fa3a3bc5bdf7e7078acb682cccb79da4e0eecd7d1638`.
Both `authorized_paths` and `complete_paths` are empty, and
`source_authorized_packet_present` is false.

The scan includes the later R-545 and R-546 conditional contracts,
certificates, results and replay tools.  Their presence is not source
authorization.  The snapshot is provenance evidence only and does not
construct `U_n`, a common Hilbert space, a path law or a semigroup.

## Finding and decision

The primary replay passes 847/847, the non-importing independent replay passes
667/667, the hostile mutation lane passes 10/10, and the integrated v1.3
verifier passes 21/21.  All lanes agree on 164 candidates, the manifest above,
zero authorized paths and zero complete paths.

The result is therefore `HOLD_FOR_EVIDENCE` / `auxiliary_support`.  This is a
fresh provenance checkpoint, not a universal nonexistence theorem and not an
analytic counterexample to PAH-OMC-020.

## Verification

```text
python -X utf8 verification/scripts/pah_omc020_owner_packet_snapshot.py --snapshot strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.3.json --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-snapshot-v1.3/primary.json --check
python -X utf8 codes/foundations/pah_omc020_owner_snapshot_v11_independent.py --snapshot strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.3.json --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-snapshot-v1.3/independent.json --check
python -X utf8 codes/foundations/pah_omc020_owner_snapshot_v11_hostile.py --snapshot strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.3.json --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-owner-snapshot-v1.3/hostile.json --check
python -X utf8 verification/scripts/pah_omc020_owner_snapshot_v13_verify.py --check
```

Lean is not applicable to this provenance-only manifest.  R-545 and R-546
remain separately scoped finite/conditional records and are not promoted by
this scan.

## Remaining contract

The next single question is whether a source owner supplies one versioned,
hash-pinned packet containing the common `H/U_n` comparison, anchored N2b
liminf and recovery, N2c/N4 boundary escape, and exact R-512 minimal-form
identification.  Until then, the stationary semigroup convergence objective
remains `HOLD_FOR_EVIDENCE`.

## Non-claims

This certificate does not prove an infinite-volume process, non-explosion,
uniqueness, N2b, N2c/N4, N2d, R-512 identification, ordered semigroup
convergence, or any physical Pre-A, spacetime, QFT, gravity, continuum,
Yang--Mills, mass-gap or TOE conclusion.  Markov time remains external
stochastic bookkeeping only.
