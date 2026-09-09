# PAH-OMC-020 diagonal locality obstruction certificate

## Scope

`R-563` audits one precise upgrade route from the R-562 fixed-power locality
envelope.  The PAH-001 functional, rates, Gibbs state, carrier, comparison
map, normalization and external stochastic Markov time are unchanged.  No new
finite carrier or physical interpretation is introduced.

## Exact arithmetic statement

R-562 uses the frozen OMC-013 radius `r=2` and, for a finite-support cylinder
with maximum support column `s_f`, the sufficient threshold

`N_k(f) = max(2, s_f + 2 k + 1)`.

For every nonconstant cylinder `s_f >= 0` and every finite volume index `n`,
choose `k=n+1`.  Then

`s_f + 2 k + 1 >= 2(n+1)+1 > n`,

and therefore `n < N_k(f)`.  Hence

`sup_k N_k(f) = infinity`,

and there is no fixed finite `n` for which `n >= N_k(f)` holds for all powers
`k`.

The primary verifier re-derives radius two from the OMC-013 catalog and checks
the diagonal witness over representative support and volume inputs.  The
independent verifier rebuilds the two-row incidence geometry rather than
importing the primary implementation.  Lean proves the universal Nat
statements, not an analytic semigroup theorem.

## Route consequence

The R-562 conditional identities are therefore pointwise in fixed `k`.  They
cannot alone be used as an all-power identity at one fixed volume and then
inserted term-by-term into an exponential series.  The obstruction is to that
upgrade route only.  It does not rule out a separate uniform connected-word or
factorial estimate, cancellation argument, common path-space construction or
form/resolvent proof.

## Verification

Primary, independent, hostile and integrated replays, plus Lean 4.32.1, are
recorded under the R-563 run directory.  Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc020_diagonal_locality.py --check
python -X utf8 codes/foundations/pah_omc020_diagonal_locality_independent.py --check
python -X utf8 codes/foundations/pah_omc020_diagonal_locality_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_diagonal_locality_verify.py --check
Set-Location verification/lean; lake env lean Tect/PahOmc020DiagonalLocality.lean
```

The result is a scoped `NEGATIVE_RESULT` and auxiliary support.  It does not
change the active gate or the PAH-OMC-020 claim tier.  Uniform-in-`k` tail,
common realization, N2b/N2c/N4/N2d and R-512 identification remain open.

There is no claim here about physical Pre-A, spacetime, QFT, gravity,
Yang--Mills, continuum limits, mass gaps or TOE conclusions.

## Adversarial review

1. The diagonal witness is an obstruction to one route, not to every possible
   semigroup proof; independent uniform cancellation remains admissible.
2. The statement concerns nonconstant finite cylinders with `s_f>=0`; it does
   not silently extend to the constant cylinder.
3. The arithmetic uses the frozen radius-two source catalog; no radius,
   counterterm, rate or carrier is altered.
4. Fixed-`k` locality remains valid after its threshold; the result does not
   turn the R-562 conditional theorem into a contradiction.
5. External Markov time is not reinterpreted as quantum, proper or Lorentzian
   time.
