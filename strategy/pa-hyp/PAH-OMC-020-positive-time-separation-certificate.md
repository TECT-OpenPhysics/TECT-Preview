# PAH-OMC-020 positive-time separation certificate (R-553)

## Contract

Question: does the frozen R-527 source-multiplicity witness separate the two
source-compatible finite semigroup correlation orbits at some positive Markov
time, rather than only at the generator derivative at time zero?

The audit keeps PAH-001, PAH-OMC-004, the temporal preregistration, the
displayed functional, rates, labelled Gibbs state, external stochastic Markov
time, carrier, regulator, normalization and j-before-n order unchanged.

## Exact finite implication

R-552 supplies one gauge-invariant closed-face cylinder with the same initial
value for the two completions and derivatives

    u_A'(0) = 2 exp(-2),    u_B'(0) = exp(-2).

The gap is exp(-2) > 0. The ordinary first-order derivative definition gives
an existential delta > 0 for which the remainder is less than half the gap
times |t|. For every 0 < t < delta this implies

    u_A(t) > u_B(t).

The result is existential only: no numeric delta is claimed because the full
finite generator norm/remainder bound is not source-owned.

## Evidence

- Primary: `pah_omc020_positive_time_separation.py`, 23/23.
- Independent: `pah_omc020_positive_time_separation_independent.py`, 13/13.
- Hostile: `pah_omc020_positive_time_separation_hostile.py`, 8/8.
- Integrated: `pah_omc020_positive_time_separation_verify.py`, 16/16.
- Lean 4.32.1: `PahOmc020PositiveTimeSeparation.lean`, three declarations.

## Classification

`HOLD_FOR_EVIDENCE`, `auxiliary_support`, `claim_bearing=false`.
This is a finite source-definition separation result. It is not a universal
no-go for an owner-fixed completion and it does not close the PAH-OMC-020
anchored-n comparison.

## Missing inputs and non-claims

The source-owner packet must still fix root multiplicity, invalid-move
behavior, root measure, common U_n/Hilbert realization, N2b liminf and
recovery, N2c/N4 boundary escape, and R-512 minimal-form identification.

There is no claim about physical Pre-A, spacetime, QFT, gravity, continuum,
mass gap, Yang-Mills or TOE. External Markov time is not physical time.
