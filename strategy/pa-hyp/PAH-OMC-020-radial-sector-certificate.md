# PAH-OMC-020 amplitude-only radial-sector correlation certificate

This certificate isolates one exact invariant observable sector of the
PAH-OMC-020 target.  It uses the unchanged PAH-001 functional, moves, rates,
state, regulator order and external stochastic time.  It does not provide the
general anchored-`n` semigroup theorem.

## Frozen sources and scope

The source bytes are pinned as follows:

* `strategy/pa-hyp/PAH-001-v1.json`
  (`03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`);
* `strategy/pa-hyp/PAH-OMC-017-result-v1.json`
  (`4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb`);
* `strategy/pa-hyp/PAH-OMC-018-result-v1.json`
  (`d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65`);
* `strategy/pa-hyp/PAH-OMC-018-generator-certificate.md`
  (`18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264`);
* `strategy/pa-hyp/PAH-OMC-019-result-v1.json`
  (`82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd`);
* `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json`
  (`906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3`).

Let `D_rad` be the amplitude-only bounded globally amplitude-Lipschitz
finite-prefix cylinders in the registered R-511 domain.  The finite
correlation is the original

    C_nj(f,g;t) = <S_nj f, P_nj(t) S_nj g>_(mu_nj),

with `j -> infinity` at fixed `n`, followed by the original anchored `n`
state passage.  Markov time is external and unaccelerated.

## Radial-sector identity

The PAH-001 move set has phase, link, aperture and radial-transfer classes.
For `g in D_rad`, the phase, link and aperture maps leave `g` unchanged.  The
only nonzero finite-generator increment is therefore the original radial
`TR` part.  The pinned R-511 certificate gives, with `h_j=2^(-j)`,

    ||L_TR,nj S_nj g||_(L2(mu_nj)) <= 2 H_g L_g h_j.

No cancellation between endpoint directions is used.  Since the finite
stationary semigroup is an `L2` contraction, variation of constants yields

    ||P_nj(t)S_nj g - S_nj g||_2
      <= 2 t H_g L_g h_j.

For bounded `f`, the correlation error is consequently bounded uniformly on
`0 <= t <= T` by

    |C_nj(f,g;t) - <S_nj f,S_nj g>_(mu_nj)|
      <= 2 T ||f||_infinity H_g L_g h_j.                 (1)

The primary exact fixtures use `H_f=3/2`, `L_g=5/3`, `T=7/4`.  The coefficient
`2 H_f L_g` is `5`, and the bound at `j=10` is below `1/100`.  These are test
inputs for the inequality, not fitted PAH parameters.

## Ordered state and minimal-form passage

R-510 supplies fixed-prefix local state convergence for each cylinder pair,
so the static term in (1) converges as `j` tends to infinity to
`<f,g>_(nu_n)`, and then in the registered anchored state passage to
`<f,g>_H`.  R-512 places the closure of `D_rad` in `H_rad`, with zero form
energy and zero cross-energy.  Under the standard representation of the
nonnegative closed form by `K_min`, this means `K_min f=0` for `f in H_rad` and
`T_min(t)f=f`.  Thus, for `f,g in D_rad`, the ordered scalar correlations have
the conditional target

    lim_n lim_j sup_(0<=t<=T)
      |C_nj(f,g;t) - <f,T_min(t)g>_H| = 0.              (2)

This is a sector theorem: it uses local scalar state convergence rather than
a completed varying-space map.  It does not assert that the same argument
works for aperture- or label-dependent observables.

## Verification and adversarial review

The primary executable performs 31 source, residual, contraction, ordered-limit
and exact-rational checks.  The non-importing independent executable performs
23 independently reconstructed checks.  The hostile executable performs 21
checks rejecting a dropped factor of two, replacing `h_j` by `h_j^{-1}`,
omitting radial endpoint directions, promoting the radial sector to mixed
observables, and assigning physical meaning to Markov time.  The integrated
runner checks all three lanes, the Lean registry and a clean Lean 4.32.1
compile.  Lean formalizes the displayed rational identities and mesh decay
only; it does not formalize the measure-theoretic state limit or semigroup
representation.

The files and hashes are recorded in
`strategy/pa-hyp/PAH-OMC-020-radial-sector-result-v1.json` and the four run
JSON files under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-radial-sector/`.

## Boundary and next question

This result is `auxiliary_support`, conditional on the inherited R-510/R-511
state and residual estimates and the standard closed-form kernel implication.
It does not supply a common `U_n` for general cylinders, arbitrary-sequence
N2b liminf/recovery, N2c/N4 boundary escape for evolved mixed observables,
N2d minimal-form identification beyond this kernel sector, or the full
anchored-`n` semigroup convergence.

The next single question is:

> Can one non-radial local cylinder be compared to the R-512 minimal form by
>   a source-authorized common-space or terminal-square-compatible map,
>   without changing PAH-001?

There is no physical Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills,
mass-gap or TOE conclusion.  External Markov time is not quantum real time,
proper time or Lorentzian time.
