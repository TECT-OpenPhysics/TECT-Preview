# PAH-OMC-020 N2b energy-intertwining contract

## Status

This is a researcher-owned conditional checkpoint for the unchanged
PAH-OMC-020 model.  Its verdict is `HOLD_FOR_EVIDENCE`.  It does not add a
functional, transition rate, state, carrier, regulator or time variable, and
it does not change the active T-054 gate.

## Exact question

Does the R-525 maximal-prefix conditional-expectation candidate supply the
root-wise dynamic information needed to compare the finite reversible forms
`E_n` with the R-512 minimal-form target?  The required datum is a
conductance-compatible root correspondence with either

    Delta_infty,r(U_n f) = kappa_(n,r) Delta_n,r(f)

and `w_infty,r*kappa_(n,r)^2 <= w_n,r`, or an explicitly bounded residual whose
sum is uniform in the anchored `n` exhaustion.  The terminal unsplit square
and split-cell boundary must use the same correspondence.

Under that datum, the directed-half root contribution obeys

    E_infty,r(U_n f) <= E_n,r(f),

and a uniformly summable residual gives the recovery-side estimate needed by
N2b.  This is an implication contract, not a proof that the datum exists.

## What is actually supplied

R-525 supplies a static maximal-prefix coupling and a positive unital
conditional-expectation `L2` contraction with local N1 recovery.  R-528's
fixed owner snapshot contains no source-authorized or complete owner packet.
The exact source pins are recorded in the contract and in the primary run.
The candidate contains no root-wise `kappa`, dynamic difference intertwiner,
conductance comparison, uniform defect, or terminal-boundary packet.

## Diagnostic insufficiency witness

For an abstract two-state reversible oracle with stationary marginal
`(1/2,1/2)`, observable `(0,1)`, identity static coupling, source rate `1`
and target rate `2`, the two `L2` norms are equal, while the directed-half
energies are respectively `1/2` and `1`.  Thus static `L2` contraction and
matching Gibbs marginals do not imply form contraction without dynamic root
data.  This oracle is explicitly not a PAH carrier and is not a PAH negative
result.

## Verification

Primary, independent and hostile lanes all replay successfully:

    python -X utf8 verification/scripts/pah_omc020_energy_intertwining_contract.py --check
    python -X utf8 codes/foundations/pah_omc020_energy_intertwining_independent.py --check
    python -X utf8 codes/foundations/pah_omc020_energy_intertwining_hostile.py --check
    python -X utf8 verification/scripts/pah_omc020_energy_intertwining_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
    lean verification/lean/Tect/PahOmc020Energy.lean

The primary, independent, hostile and integrated runs report 37, 28, 19 and
30 checks, respectively.  Lean 4.32.1 proves the weighted one-root transfer
implication and the exact two-state arithmetic witness in six declarations.

## Decision and next evidence

The conditional implication is verified, but no source-authorized dynamic
intertwining or uniform form defect is present.  The route therefore remains
`HOLD_FOR_EVIDENCE` and `auxiliary_support`.  The one next question is:

> Can a source owner provide a versioned root-wise conductance-compatible
> dynamic intertwining, including the terminal-square correspondence, for the
> exact R-525 `U_n`, or a uniform vanishing form defect, without changing
> PAH-001?

Until that packet exists, do not repeat static coupling fixtures and do not
claim N2b, N2c/N4, N2d or the ordered PAH-OMC-020 semigroup limit.

There is no physical Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills,
mass-gap or TOE conclusion.  The time variable remains external stochastic
bookkeeping.
