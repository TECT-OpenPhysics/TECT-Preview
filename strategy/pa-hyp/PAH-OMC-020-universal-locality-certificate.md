# PAH-OMC-020 universal finite-cylinder locality certificate

## Scope

`R-562` extends the `R-561` fixed-power locality envelope from the single
`ell_(0,0)` witness to arbitrary finite-support cylinders.  It keeps the
PAH-001 functional, rates, Gibbs state, carrier, root family, refinement map,
normalization and external stochastic Markov time byte-for-byte unchanged.
The only statement tested is conditional fixed-power locality; no exponential
series, `j`/`n` limit or R-512 identification is evaluated.

## Frozen inputs and geometry

| Input | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json` | `e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc` |
| `strategy/pa-hyp/PAH-OMC-020-iterate-locality-result-v1.json` | `f9cef0e147be1c9fc084392e34a02c41a1be1ae78ad31ec641123e719e0a9d8e` |

The OMC-013 root catalog is independently re-derived at levels 2 through 9;
its maximum core-to-support column radius is `r=2`.  For a cylinder `f`, let
`s_f` be the largest support column, with `s_f=-1` for the constant cylinder.
After `k` generator applications the conservative envelope is at most
`s_f+2k`, so

`N_k(f) = max(2, s_f + 2k + 1)`.

At `n >= N_k(f)` that envelope is strictly before the successor frontier
columns `{n,n+1}`.  The primary lane checks constant, vertex, separated,
face-generated and remote finite supports; the independent lane rebuilds the
strip and incidence rules without importing the primary implementation.

## Conditional conclusion

If the R-493 one-step identity holds on every recursively enlarged finite-
support cylinder in this envelope, induction gives

`L_(n+1)^k I_(n,n+1) f = I_(n,n+1) L_n^k f`

for each fixed finite `k` and `n >= N_k(f)`.  The threshold is observable- and
power-dependent.  Lean verifies the arithmetic separation and the generic
iterate induction, not the missing analytic hypotheses.

## Verification and limits

Primary `14/14`, independent `8/8`, hostile `8/8`, integrated `4/4`, and the
Lean 4.32.1 replay all pass.  Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc020_universal_locality.py --check
python -X utf8 codes/foundations/pah_omc020_universal_locality_independent.py --check
python -X utf8 codes/foundations/pah_omc020_universal_locality_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_universal_locality_verify.py --check
Set-Location verification/lean; lake env lean Tect/PahOmc020UniversalLocality.lean
```

This is `PASS_CONDITIONAL` auxiliary support.  It does not supply a uniform-
in-`k` factorial/word tail, a common `U_n` or path space, N2b/N2c/N4/N2d, or
R-512 minimal-form selection.  Therefore it does not prove semigroup
intertwining, ordered stationary-correlation convergence, infinite volume,
continuum, or any physical Pre-A, spacetime, QFT, gravity, Yang--Mills,
mass-gap or TOE statement.

## Adversarial review

1. A finite table through `k=5` is not a uniform-in-`k` bound; `N_k` grows.
2. The R-551 below-threshold defect is not a contradiction to the sufficient
   threshold and is not promoted to a universal no-go.
3. Fixed-power induction cannot sum the exponential without a common domain
   and factorial tail.
4. A remote support row does not establish all possible cylinders; the claim
   remains conditional on finite-support closure and the R-493 premise.
5. No stochastic Markov time is reinterpreted as quantum, proper or physical
   time.

The next single question is whether a source-authorized common realization can
supply the missing uniform tail and compatible comparison for summing powers.
