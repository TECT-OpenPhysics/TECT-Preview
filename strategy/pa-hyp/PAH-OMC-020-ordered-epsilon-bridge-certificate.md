# PAH-OMC-020 ordered-epsilon bridge

## Question and frozen scope

The registered PAH-OMC-020 route has the unchanged two-term bound

`err_(n,j) <= J_(n,j) + D_n`.

This checkpoint asks only whether the two antecedent epsilon controls imply the
exact registered order: first choose an anchored `N`, then for each `n >= N`
choose a fixed-`n` threshold `J(n)`, and finally take every `j >= J(n)`.  The
PAH-001 functional, directed rates, labelled Gibbs state, normalization and
external stochastic Markov time are hash-pinned and unchanged.

## Result

The abstract implication is `PASS_CONDITIONAL`.  The primary verifier passes
13/13 checks, the non-importing independent verifier passes 13/13 on a
different rational fixture, the hostile verifier rejects five contract-breaking
mutations, the integrated verifier passes 22/22, and Lean 4.32.1 compiles the
three registered declarations.  The exact conclusion is the nested
`j-before-n` epsilon statement; no diagonal or reversed order is used.

This does not instantiate the PAH-specific `J_(n,j)` or `D_n` estimates.  The
source-authorized common-space/path-space owner packet remains absent, so the
overall PAH-OMC-020 objective remains `HOLD_FOR_EVIDENCE` and the active gate is
unchanged.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_ordered_epsilon_bridge.py --check
python -X utf8 codes/foundations/pah_omc020_ordered_epsilon_bridge_independent.py --check
python -X utf8 codes/foundations/pah_omc020_ordered_epsilon_bridge_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_ordered_epsilon_bridge_verify.py --check
```

Lean is compiled from the canonical dependency environment:

```text
lake env lean Tect/PahOmc020OrderedEpsilon.lean
```

## Adversarial boundary

The bridge assumes the two limits; it does not prove either one.  It does not
create a common Hilbert space, path law, non-explosion theorem, N2c/N4 estimate,
R-512 identification, infinite-volume dynamics or semigroup convergence.  It
also makes no physical Pre-A, spacetime, QFT, gravity, Yang--Mills, continuum,
mass-gap or TOE claim.  Markov time remains external stochastic bookkeeping.

## Next single question

Can a source-authorized, hash-pinned owner packet supply both PAH-specific
antecedents under the unchanged common space, so this exact bridge can be
instantiated rather than assumed?
