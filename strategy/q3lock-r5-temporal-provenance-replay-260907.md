# Q3LOCK temporal-provenance correction and replay r5

Date: 2026-09-07. Exploration: EXP-001630. Task: T-054.
Status: T0, claim_bearing=false, provenance and reproducibility checkpoint only.
The sole Q3LOCK authority remains EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
No analytic theorem tier, publication status, or PDF status changes.

## Temporal provenance correction

The append-only temporal-correction sidecar records that EXP-001629 was
registered with an untrusted future timestamp and must not be used as
contemporaneous timing evidence.  Record `TC-0033` preserves the original
exploration line byte-for-byte while marking that timestamp as unknown.  The
sidecar is provenance metadata only; it changes no mathematical statement,
source file, claim tier, or audit payload.

Because the sidecar is part of the frozen authority manifest, its expected
SHA-256 was corrected to the current byte hash.  The manifest correction is
itself provenance bookkeeping, not an analytic result.  The replay entrypoint
now admits exactly this one temporal-sidecar hash change and the corresponding
manifest source-hash leaf, while fail-closing on every other authority change.

## Replay r5

The non-overwriting replay writer produced:

`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-paper-readonly-replay-r5/result.json`

The result passes seven canonical finite diagnostic groups, seven manuscript
groups, 19 protected historical records, 46 non-importing algebra checks, and
the six replay-safety guard fixtures.  Its provenance payload records only the
temporal-correction path and the manifest source-hash correction.  The prior
replay remains historical and was not overwritten.

These checks establish a reproducible internal package state.  They do not
certify the unbounded loop, DLR, infrared, collective, cusp, or source-tangent
arguments; they do not replace signed mathematics or specialist literature
review; and they do not close content freeze, hash freeze, or the final-PDF
gate.  The paper PDF count remains zero.

## Next gate

Update the reader-facing package to point to the next immutable integrated
replay after the remaining documentation changes, create a fresh audit
checkpoint under a new absent label, and rerun the complete Q3LOCK test and
release gates.  Keep the first PDF deferred until the content, notation,
bibliography, nonclaims, independent reviews, and source hashes are frozen.
