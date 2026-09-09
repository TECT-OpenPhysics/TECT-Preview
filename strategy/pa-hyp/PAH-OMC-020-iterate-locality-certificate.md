# PAH-OMC-020 fixed-power locality certificate

## Scope

This checkpoint records `R-561`, a conditional finite operator-algebra bridge
for the unchanged PAH-001 and PAH-OMC-013 definitions. It asks only whether
the registered one-step local-generator identity can be iterated for a fixed
power after the observable support has been enlarged by the frozen root
catalog. The stochastic time remains the external Markov time in PAH-001.

No carrier, rate, state, projection, counterterm, regulator, time
interpretation, comparison map, or limit order is changed. The result does not
claim a single threshold for all powers, a summed exponential semigroup, an
anchored-n limit, or an ordered stationary-correlation theorem.

## Frozen inputs

| Input | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json` | `e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc` |
| `strategy/pa-hyp/PAH-OMC-020-finite-semigroup-lift-result-v1.json` | `a3e24dc96e3ca6fb01f991ab7d1062da06af82b3252100148f365c094b03c35c` |
| `strategy/pa-hyp/PAH-OMC-020-second-order-defect-result-v1.json` | `c0bb72f9cbb409c4474d3adc3b0754f10cc0825378443f9a61ad162a7febe134` |

The comparison is the original pointwise pullback `I_(n,n+1)` and the same
finite backward generators used by R-493. The one-step premise is conditional:
it must hold for every finite-support function in the recursively enlarged
cylinder class.

## Support calculation

The frozen OMC-013 root catalog has core-to-support column radius two. Starting
from the cylinder support `{(0,0)}`, the conservative closure has maximum
column `2k` after `k` applications. The sufficient threshold is therefore
`N_k(f)=max(2,2k+1)` for this witness.

| fixed power `k` | maximum closure column | sufficient `N_k` | closure size |
|---:|---:|---:|---:|
| 0 | 0 | 2 | 1 |
| 1 | 2 | 3 | 6 |
| 2 | 4 | 5 | 10 |
| 3 | 6 | 7 | 14 |
| 4 | 8 | 9 | 18 |
| 5 | 10 | 11 | 22 |

At each fixed `k`, the boundary-root labels active on level `n` agree with
those on level `n+1` after `n >= N_k`. Under the conditional one-step premise,
induction gives

`L_(n+1)^k I_(n,n+1) f = I_(n,n+1) L_n^k f`.

The existing R-551 second-order witness at `n=3` lies below `N_2=5`, so its
nonzero defect is a boundary diagnostic rather than a contradiction to this
fixed-power statement. Replaying the same frozen sample at `n=5` gives zero
second-order defect, consistent with the threshold; this is not a universal
proof by itself.

## Verification

The primary replay passes `13/13`, the independently rebuilt strip geometry
passes `8/8`, the hostile scope controls pass `8/8`, and the integrated replay
passes `4/4` including the existing Lean file
`verification/lean/Tect/PahOmc020FiniteSemigroup.lean`.

Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc020_iterate_locality.py --check
python -X utf8 codes/foundations/pah_omc020_iterate_locality_independent.py --check
python -X utf8 codes/foundations/pah_omc020_iterate_locality_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_iterate_locality_verify.py --check
Set-Location verification/lean; lake env lean Tect/PahOmc020FiniteSemigroup.lean
```

## Decision and boundary

`R-561` is `PASS_CONDITIONAL` and `auxiliary_support`. It closes only the
fixed-`k` finite locality bridge. It does not close PAH-OMC-020, change the
active gate, or promote any claim tier.

The missing next inputs are a source-authorized common invariant cylinder or
common path-space realization, a uniform-in-`k` connected-word or factorial
tail bound, the N2b/N2c/N4/N2d obligations, and a proof that the fixed-power
identities can be summed in the original unaccelerated Markov time.

Next question: can a source-authorized common realization supply a uniform
factorial tail and compatible `U_n`/path comparison so that these fixed-power
identities can be summed without exchanging `k` and `n`?

There is no claim here about physical Pre-A, spacetime, QFT, gravity,
Yang--Mills, continuum limits, mass gaps, or TOE conclusions.
