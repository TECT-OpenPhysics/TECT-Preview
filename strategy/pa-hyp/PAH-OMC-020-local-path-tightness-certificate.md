# PAH-OMC-020 local path-tightness checkpoint

## Decision

`HOLD_FOR_EVIDENCE` / `auxiliary_support` for result `R-541`.  The bounded
finite calculation establishes a uniform local-observable stopped-time
increment envelope from already registered source bounds.  It does not close
the PAH-OMC-020 temporal limit or change the active T-054 gate.

## Frozen source and scope

The calculation uses exactly the original PAH-001 finite continuous-time
Markov chain, its labelled Gibbs stationary law, and the original external
stochastic Markov time.  The registered `j`-before-anchored-`n` order is
unchanged.  No functional, rate, state, carrier, regulator, normalization,
time convention or comparison map is introduced.

The source pins are:

| source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json` | `8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69` |
| `strategy/pa-hyp/R490-certificate.md` | `80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a` |
| `strategy/pa-hyp/PAH-OMC-020-c2-moment-result-v1.json` | `87dd9a7225203cdfa84456e446983c573cabc6c50a902a85ea12e28ccbc5b379` |
| `strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json` | `12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |

R-490 supplies the source-derived Gibbs conductance incidence constant
`C_sw=540`; R-522 supplies the source-derived squared-rate bound
`C2(A)<=60|A|`.  For a bounded local cylinder with finite root support `A`
and root increments `d_r=||f(r dot)-f||_infinity`, define

```text
K_Gamma(f) = 540 |A| max_r d_r^2,
K_L(f)     = 60 |A| sum_r d_r^2.
```

For every finite stationary process, stopping time `tau<=T`, and `delta>=0`,
the generator-martingale plus integrated-drift decomposition and
`|a+b|^2 <= 2a^2+2b^2` give the registered conditional envelope

```text
E |f(X_(tau+delta))-f(X_tau)|^2
    <= 2 delta K_Gamma(f) + 2 delta^2 K_L(f).
```

The Markov quotient of this envelope by `epsilon^2` tends to zero with
`delta`, uniformly in the finite level and radial cutoff.  This is the local
real-valued Aldous tightness input recorded by the contract.  The primary
replay uses support size `|A|=2`, 120 admitted roots and `d_r=1/4`, giving
`K_Gamma=135/2`, `K_L=900`, and envelope `171/1250` at `delta=1/1000`.
The independent replay uses `|A|=3`, 180 roots and `d_r=3/10`, giving
`K_Gamma=729/5` and `K_L=2916`.

## Verification

The primary lane passes 25/25 checks, the non-importing independent lane
passes 20/20, the hostile lane rejects 9/9 invalid mutations, and the
integrated lane passes 27/27.  The six finite rational Lean declarations in
`verification/lean/Tect/PahOmc020PathTightness.lean` compile with Lean 4.32.1:
the two-square inequality, nonnegative envelope, nonnegative Markov quotient,
delta monotonicity, source constants, and the registered fixture.

Reproduce the checkpoint with:

```text
python -X utf8 verification/scripts/pah_omc020_local_path_tightness.py --check
python -X utf8 codes/foundations/pah_omc020_local_path_tightness_independent.py --check
python -X utf8 codes/foundations/pah_omc020_local_path_tightness_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_local_path_tightness_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Run artefacts:

| artefact | SHA-256 |
|---|---|
| primary JSON | `df7ac3fa59a2ccae55ac6081c0a1447cf120b7a4ad688c3bdd63001fdadb9b80` |
| independent JSON | `254c0e7c9fc45adcb1143c24ced9096e9b6cb3f994f8d1f2663f94d37d174cc5` |
| hostile JSON | `ea5e612151b680837edef6058991de77826ec7dcc6ff933173cb05073364824f` |
| integrated JSON | `e852fcae6aca223e2db5e6391d55f6a18b7a0ed4433c3442097361dac4bc1a6d` |

Tooling and formal pins:

| file | SHA-256 |
|---|---|
| primary verifier | `992a7ccab7ee5ab1f047d68058c7633539e6384eb82b7e37219293947822ca30` |
| independent verifier | `43c4c80f2b03ae1e707af2db6f0214c6bcab7e4e61d614272ef22fc707aea058` |
| hostile verifier | `343bd5d5092da1df50105d10515a5bc3da9bd8c308aec059255ff18d7b6f1835` |
| integrated verifier | `2d526ad6ecf8e184aeebe8010e9f7fe672b3b5c592144eff69f09b7ae29cd432` |
| Lean file | `6a1bd86d5c5ea87acb0fc735de67c5a4030542ca6733290f7171e2e3aa5496eb` |
| Lean registry | `70825043392c7f64078ea2d71bd170c886116a3b4eb444ea9f6b2214654c6052` |

## Adversarial boundary

The hostile lane detects omission of the martingale term, omission of either
factor two, a delta-independent bound, substitution of `C_sw` for `C2`,
physical-time relabelling, and promotion of the path-space bridge to a
process theorem.  These controls support the stated finite envelope but do
not prove that the bound is attained by a limiting process.

The remaining single evidence question is:

> Can a source-authorized martingale-problem/path-space construction with
> non-explosion and uniqueness identify every subsequential local path limit
> with the R-512 minimal-form semigroup in the frozen `j`-before-anchored-`n`
> order?

Until that owner packet exists, N2b/N2c/N4, R-512 identification and ordered
semigroup convergence remain open.  No physical Pre-A, spacetime, QFT,
gravity, continuum, Yang--Mills, mass-gap or TOE conclusion follows; external
Markov time is not quantum, proper or Lorentzian time.
