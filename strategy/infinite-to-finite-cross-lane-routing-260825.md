# Infinite-to-finite cross-lane routing note v0.1

**Status:** reference-only strategy transfer
**Evidence role:** T0 route guidance; no claim or tier change
**Date:** 2026-08-25

## Decision

Use an infinite-to-finite formulation as a top-down compatibility and
necessary-condition lane, not as a substitute for constructing the infinite
theory. The proof-bearing direction remains a controlled finite-to-infinite
limit with explicit uniform estimates.

## Main TECT/Q3 lane

Use a proposed infinite theory only to derive tests for finite Q3 regulators:

1. project the proposed dynamics, state, locality and symmetry to finite
   volume and oscillator cutoffs;
2. test both signs, source choices, orientations and support-local weights;
3. require bounds independent of volume, source, inverse temperature and
   regulator before treating the projection as a bridge;
4. prove common-core/domain transfer, full-versus-cutoff convergence and
   exhaustion independence before common-alpha or OS/KMS/GNS promotion.

An infinite ansatz that supplies only finite projections is a reference
constraint. It cannot establish existence, CCR transfer, a KMS state, a gap,
or a continuum limit by itself.

## TECT--Yang--Mills hybrid lane

Apply the same top-down requirements to choose and falsify finite hybrid
models, while preserving the existing owner boundary `HYB-TECT-YM-DYN-0001`:

- exact gauge-off/zero-coupling recovery of the hash-pinned TECT parent;
- exact frozen/decoupled recovery of the declared regulated gauge parent;
- one physical gauge-invariant observable map and a declared real-time
  reconstruction;
- reflection positivity or its explicitly justified replacement;
- regulator, volume and temperature limits with constants independent of the
  finite regulator.

Finite hybrid success remains `candidate_only`; it does not promote A13,
Sector A, Pre-A, OS/KMS, continuum or Yang--Mills mass-gap claims.

## Yang--Mills owner lane

The Yang--Mills repository remains authoritative for its own obligations. This
repository supplies only the pointer
`E:/Dev/YangMills/research_db/records/interfaces.jsonl#IF-TECT-YM-0001` and the
hybrid handoff. No Yang--Mills source, claim, or obligation is copied or
mutated here. The owner-side use is limited to checking whether the proposed
finite projections satisfy the gauge, physical-sector, OS and uniform-limit
requirements.

## Stop conditions

Stop and register a route-local obstruction if the infinite-to-finite map
requires dropping unmatched terms, silently identifies Euclidean or stochastic
time with physical time, loses gauge-invariant observables, or has no uniform
bound for the reverse limit. Do not promote a finite pass on the basis of the
top-down ansatz alone.

## Next gate

For the main Q3 route, prove or refute the source/volume-uniform modular
history and the truncated-CCR common-core tail condition. For the hybrid lane,
keep HYB-00--HYB-04 finite and require the parent-limit and observable-map
crosswalk before any HYB-05 or continuum work.
