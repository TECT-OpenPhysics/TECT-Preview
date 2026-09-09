# PAH-OMC-020 stationary-modulus correction

## Decision

`HOLD_FOR_EVIDENCE` / `auxiliary_support` for `R-542`.  This successor does
not edit the immutable R-541 record.  It narrows the temporal promotion
boundary: the pinned source bounds prove a deterministic-time stationary
modulus, but they do not by themselves prove the bounded-stopping-time
estimate required by Aldous' criterion.

## Exact source scope

All inputs remain the original PAH-001 functional, directed rates, labelled
Gibbs stationary law, finite OMC-004 strip and external stochastic Markov
time.  The preregistered `j`-before-anchored-`n` order is unchanged.  R-490's
`C_sw=540` and R-522's `C2(A)<=60|A|` are retained as `pi`-weighted source
averages; neither is silently changed into a pointwise-in-configuration rate
bound.

For a bounded local cylinder with finite support `A` and root increments
`d_r=||f(r dot)-f||_infinity`, the finite martingale/drift decomposition gives
for a deterministic time `t`:

```text
E |f(X_(t+delta))-f(X_t)|^2
    <= 2 delta K_Gamma(f) + 2 delta^2 K_L(f),
K_Gamma(f) = 540 |A| max_r d_r^2,
K_L(f)     = 60 |A| sum_r d_r^2.
```

Stationarity justifies replacing the time integral by the stationary
`pi`-average for deterministic `t`.  It does not justify the same replacement
after an arbitrary stopping time, because the stopping time can select states
where the local rate is atypically large.

## Exact implication diagnostic

The distinction is exposed by an abstract reversible two-state chain (not a
PAH carrier or PAH counterexample).  Give `0->1` rate
`epsilon=1/M^2` and `1->0` rate `M`.  Its stationary weighted carré-du-champ
for the indicator of state `1` is

```text
2 M epsilon / (M + epsilon),
```

which and its deterministic scale after a `1/M` interval decrease as `M`
grows.  Once the chain has hit state `1`, however, an interval of length
`delta=log(2)/M` contains a jump with probability exactly `1/2`.  Thus a
stationary weighted average alone cannot supply a uniform conditional
stopping-time bound.  This diagnostic only blocks an inference; it does not
refute PAH-001.

## Reproduction and evidence

Source pins:

| source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json` | `8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69` |
| `strategy/pa-hyp/R490-certificate.md` | `80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a` |
| `strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json` | `87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |
| `strategy/pa-hyp/PAH-OMC-020-local-path-tightness-result-v1.json` | `90cf191edc5df6c05a7e7facaaa179e075c87129891d22456dfd36186994d27c` |

The primary replay passes 21/21, the non-importing independent replay passes
18/18, the hostile promotion controls pass 11/11, and the integrated replay
passes 27/27.  Lean 4.32.1 compiles five finite rational declarations,
including the rare-state stationary identity, its exact fixture and the
deterministic envelope.

```text
python -X utf8 verification/scripts/pah_omc020_stationary_modulus_correction.py --check
python -X utf8 codes/foundations/pah_omc020_stationary_modulus_correction_independent.py --check
python -X utf8 codes/foundations/pah_omc020_stationary_modulus_correction_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_stationary_modulus_correction_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Artefact pins:

| artefact | SHA-256 |
|---|---|
| primary run | `0b83118de06a617e21b471eb160e3272843d359a8d9116da9fa28994e52c8189` |
| independent run | `913f5cb9e64513d6d25d7075f6a0b6080cbdd90958b352cdc8ce2c6d6546c4ca` |
| hostile run | `ed26163a02e9e310befdc6fa42cc162f0a2903f4b401348c09803025fe75e066` |
| integrated run | `8e4bfe08cbe9b99f0efb8cfa3e8ab70e2b45f0aa61e331d77054e56460489195` |
| primary verifier | `dda176aec80a2196bf02c3259f319fbf51fd6c8d8cd281aa5eb5a17494d8483d` |
| independent verifier | `8d2fc4cefd997abc04857ba8e30f33037822d3ecdb59b6df32bd744f99375f84` |
| hostile verifier | `71fedddbc4bd7fb79c691da3e8cd4e2cbb18f3ab22787bccef4176800110a51a` |
| integrated verifier | `d0f2898af289846136d64db2e5a882a6988579dda73a4d0f7e902096e0e731b1` |
| Lean source | `aab2e60116ee9e4df69f364d7693703cc0f8cc60ccf04dcb4a5d943c27155fe5` |
| Lean registry | `60634137184b5d999be4928829eeb3d8856b9d83a6d313b88cce382c20cc3d52` |

## Remaining one-field contract

The next required input is a source-authorized uniform conditional
predictable-compensator estimate (or a pointwise local-rate bound) for every
bounded stopping time.  Only after that field is present can the deterministic
modulus be upgraded to Aldous tightness, followed by path-space construction,
non-explosion, martingale-problem identification, uniqueness and R-512
minimal-form semigroup comparison.

The hostile lane rejects pointwise substitutions, deterministic-to-Aldous
promotion, physical-time relabelling, and promotion of the abstract
diagnostic to a PAH negative result.  No physical Pre-A, spacetime, QFT,
gravity, continuum, Yang--Mills, mass-gap or TOE conclusion follows; external
Markov time is not physical time.
