# PAH-OMC-020 direct two-term route

## Decision

`PASS` / `auxiliary_support` for `R-546`.  The registered R-514 fixed-`n`
passage and the R-536 target defect use the same post-`j` stationary
correlation `c_n`.  Consequently, once one complete source-authorized R-536
form or path route is admitted, the full ordered compact-time error has the
direct bound

```text
sup_(0<=t<=T)|C_(n,j)(t)-c_star(t)| <= J_(n,j)(T) + D_n(T).
```

Here `J_(n,j)` is the R-514 fixed-`n` error and `D_n` is exactly the R-536
anchored target-process/R-512 defect.  The result removes the need for a
separate `K_(n,m)` intermediate only after `D_n` is directly established.  No
R-536 owner route is currently present, so this is a conditional reduction and
does not advance the active gate.

## Frozen source crosswalk

The source bytes are hash-pinned in the result card.  R-514 keeps the original
PAH-001 finite functional, rates, labelled state, external Markov time and
`j`-before-anchored-`n` order, and defines `c_n` as the post-`j` finite-label
correlation.  R-536 defines

```text
D_n(f,g;T) = sup_(0<=t<=T)|c_n(f,g;t)-<f,T_min(t)g>|.
```

The identical `c_n` is the key compatibility condition.  If, for a given
`epsilon`, the ordered hypotheses give `J_(n,j)<epsilon/2` and
`D_n<epsilon/2`, then the triangle gives the desired error `<epsilon`.
The conclusion is literal in the registered order: first `j` at fixed `n`,
then anchored `n`.  No diagonal, reversed or joint limit is used.

R-534 remains valid with its three-term `J+K+D` budget.  R-546 does not claim
that `K` is source-authorized; it observes only that a complete direct R-536
route would make a separate `K` construction unnecessary.

## Verification

The primary lane checks all source hashes, the two exact definitions, the
order, the missing-owner status, the scalar triangle and an epsilon split.  The
independent lane reconstructs the crosswalk with a different rational fixture.
The hostile lane rejects dropping either error term, renaming the intermediate,
admitting a partial R-536 route, reversing or diagonalizing the order, and
physical promotion.  Lean 4.32.1 formalizes only the finite rational triangle,
epsilon split and two fixtures.

```text
python -X utf8 verification/scripts/pah_omc020_two_term_route.py --check
python -X utf8 codes/foundations/pah_omc020_two_term_route_independent.py --check
python -X utf8 codes/foundations/pah_omc020_two_term_route_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_two_term_route_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Primary `22/22`, independent `14/14`, hostile `14/14`, integrated `32/32`.

## Adversarial review

1. **R-514 fixed-`n` convergence already identifies R-512.**  Rejected.  R-514
   ends at `c_n`/`Q_n`; R-536's `D_n` target identification is separate.
2. **The `K_(n,m)` term can always be dropped.**  Rejected.  It can be
   omitted only when a complete direct R-536 route proves the displayed `D_n`
   convergence with the same `c_n`; the current route is absent.
3. **A partial form or path packet is enough for `D_n`.**  Rejected.  R-536
   requires all five fields of one complete route, with source authorization and
   anchored compact-time quantifiers.
4. **The two-term triangle proves the owner packet.**  Rejected.  It is an
   implication and constructs neither `U_n`, a common Hilbert space, nor a path
   law.
5. **Compact external Markov time is physical time.**  Rejected.  The time
   variable remains stochastic bookkeeping only.

## Remaining question

Can one source-authorized, hash-pinned complete R-536 form or path route prove
`D_n(T)->0` for every declared local pair while preserving R-514's `c_n` and
the original PAH-001 order?  Until then, the full PAH-OMC-020 objective remains
open.  No physical Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills,
mass-gap or TOE conclusion is made.
