# PAH-OMC-022 source-level stationary-semigroup well-posedness certificate

## Decision

`R-559` is a scoped `NEGATIVE_RESULT`. The immutable `PAH-001-v1.json` source
contains source-compatible finite root-multiplicity completions with distinct
stationary-semigroup derivatives. `R-553` shows that the resulting finite
correlation orbits separate at positive external Markov time. `R-558` shows that
the available finite successor is not source-authorized, so it cannot silently
select the original source semigroup.

This closes only the source-level formulation question: the original
PAH-001 stationary-semigroup proposition is not one uniquely well-posed theorem
under its current bytes. It does not refute every explicitly owner-fixed
successor model.

## Pinned scope

- `PAH-001-v1.json`: SHA-256
  `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`.
- R-552 result: SHA-256
  `44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee`.
- R-553 result: SHA-256
  `381869f9637341dd6f55514f87ca1849831e9ca910a27cf4e601882cd5de9fc8`.
- R-558 result: SHA-256
  `12d80d1a9acde9c73971109ad49776a628c0c3b31e00e419382f15d05146c804`.

No PAH function, transition rate, Gibbs state, external Markov time, carrier,
comparison map, counterterm or limit order was changed. No refinement,
volume, regulator, beta, observation-time, continuum or physical limit was
taken.

## Proof chain and review

1. R-552 gives exact finite derivatives `2 exp(-2)` and `exp(-2)` on the same
gauge-invariant cylinder under two source-compatible root multiplicity
completions.
2. R-553 propagates the derivative gap to positive-time separation on a
punctured right Markov-time interval.
3. R-558 classifies the separately versioned finite successor as
`SOURCE_OWNER_INELIGIBLE`, so importing it would define a new model rather than
repair the original source.

Primary `15/15`, independent `12/12`, hostile `9/9`, integrated `22/22`, and
Lean 4.32.1 compilation of four declarations all pass. Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc022_source_level_semigroup_wellposedness.py --check
python -X utf8 codes/foundations/pah_omc022_source_level_semigroup_wellposedness_independent.py --check
python -X utf8 codes/foundations/pah_omc022_source_level_semigroup_wellposedness_hostile.py --check
python -X utf8 verification/scripts/pah_omc022_source_level_semigroup_wellposedness_verify.py --check
lake env lean Tect/PahOmc022SourceLevelSemigroupWellposedness.lean
```

The independent and hostile lanes do not import the primary verifier's
assertions. The Lean declarations formalize the finite derivative contradiction
and the scope firewall separating a source-level negative from a universal
successor no-go.

## Boundary and next question

The remaining input is one owner-authorized, hash-pinned source or successor
packet that fixes root multiplicity and supplies the R-557 common realization,
N1, N2b, N2c/N4, N2d, full-domain J and anchored D fields. Until then the
PAH-OMC-020 ordered stationary-semigroup convergence question remains open for
any separately admitted model.

No physical Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills, mass-gap or
TOE conclusion is made.