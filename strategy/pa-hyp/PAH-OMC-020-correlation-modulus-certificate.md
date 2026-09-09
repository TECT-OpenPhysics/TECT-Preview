# PAH-OMC-020 deterministic correlation modulus

## Decision

`PASS` / `auxiliary_support` for `R-543`.  This is a conditional finite
equicontinuity input for deterministic external Markov time.  It does not
advance the active T-054 gate and does not identify the anchored limit.

## Frozen statement

Keep PAH-001, its original PH/LK/AP/TR rates, the labelled Gibbs state, the
OMC-004 strip, the `j`-before-anchored-`n` order and the sampled observable
`S_(n,j)` unchanged.  For a local cylinder `f`, let `D_f` and `H_f` be the
source root-count bounds in R-511, and let `M_f` and `L_f` be its declared
supremum and amplitude-l1 Lipschitz constants.  The R-511 energy estimate is

```text
E_(n,j)(S_(n,j)f,S_(n,j)f) <= B_f,
B_f = 2 D_f M_f^2 + 2 H_f L_f^2,
```

for every `n >= N(f)` and every `j`.  For the finite reversible generator,
`K_(n,j)=-L_(n,j)` is nonnegative and its spectral semigroup satisfies form
contraction.  Hence, for deterministic `s,t` and local `f,g`,

```text
|C_(n,j)(f,g;t)-C_(n,j)(f,g;s)|
    <= |t-s| sqrt(B_f B_g).
```

The constant is independent of the retained finite indices `n,j` once the
local supports have stabilized.  The derivation uses the form-energy identity
and Cauchy--Schwarz, not a pointwise total exit-rate bound.

## What was checked

The primary lane reconstructs `D_f <= 4|V_f|+2|E_f|` and
`H_f <= 2 d_max |V_f|` from the R-511 record, with `d_max=5`, then computes
the budget and squared modulus using exact rational test fixtures.  The
independent lane uses different support and Lipschitz fixtures without
importing the primary script.  The hostile lane rejects removal of the radial
term, sign reversal, replacement of form energy by a full generator norm,
and any deterministic-to-stopping-time or finite-to-infinite promotion.

Primary `27/27`, independent `20/20`, hostile `12/12`, integrated `28/28`;
Lean 4.32.1 compiles five rational declarations.  Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc020_correlation_modulus.py --check
python -X utf8 codes/foundations/pah_omc020_correlation_modulus_independent.py --check
python -X utf8 codes/foundations/pah_omc020_correlation_modulus_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_correlation_modulus_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

## Adversarial review

1. **A form-energy bound is a pointwise rate bound.**  Rejected.  The
   source identity controls the quadratic form in the stationary norm; the
   proof never bounds the supremum of the total exit rate.
2. **The derivative estimate applies at arbitrary stopping times.**  Rejected.
   This record only quantifies deterministic `s,t`; R-542's stopping-time
   boundary remains open.
3. **The modulus identifies the R-512 semigroup.**  Rejected.  It gives
   equicontinuity of finite correlations, not a common-space comparison,
   N2b/N2c/N2d, uniqueness, or target identification.
4. **The finite uniformity is an infinite-volume result.**  Rejected.  The
   bound is uniform in the retained finite indices for each fixed local pair;
   the anchored `n` passage is not taken here.
5. **External Markov time is physical time.**  Rejected.  The time variable
   remains stochastic bookkeeping only.

## Remaining gates

The next required input is a source-authorized common-space or path-space
packet that identifies the anchored-`n` limit of these equicontinuous
correlations with the R-512 minimal-form semigroup.  R-542 still blocks the
unjustified bounded-stopping-time upgrade.  No PAH-001 functional, rate,
state, carrier, regulator, normalization or limit order was changed, and no
Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills, mass-gap or TOE claim
is made.
