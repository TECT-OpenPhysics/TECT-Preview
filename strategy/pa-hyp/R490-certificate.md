# R-490 certificate — PAH-OMC-010 Gibbs-state-weighted local interaction envelope

## Exact proposition

PAH-OMC-010 is a separately versioned researcher-owned norm contract.  It
keeps the PAH-001 functional, move families, mobility and midpoint rate
unchanged, and uses the cofinal PAH-OMC-004 two-row strip family `G_n`,
`n >= 2`.  The only uniform regulator coordinate newly tested is
`R_max=R` over positive integers; `K=2`, `M_s=M_psi=1`, `Q=1`,
`epsilon=1/2`, `beta=nu=1`, and all displayed couplings are fixed to the
declared unit values.

The positive state weight is the normalized finite PAH-001 Gibbs state

```text
W_(n,R)(omega) = Z_(n,R)^(-1) exp(-F_(rho_R)(omega)).
```

For a directed root `r`, the source inverse-pair rule and midpoint rate give

```text
W(omega)c_r(omega)
  = Z^(-1) m_r exp(-(F(omega)+F(r omega))/2).
```

Writing the two square-root Gibbs factors as `a` and `b`, the exact identity
`(a^2+b^2)/2-a b=(a-b)^2/2 >= 0` bounds the conductance sum over each root
domain by one.  The declared geometric support rule is rebuilt for every
directed phase, aperture, radial-transfer and link root.  The family-wide
constants are

```text
S_geom = 8,
N_geom = 60,
C_sw   = N_geom (1+S_geom) = 540.
```

Consequently
`I_(n,R)(x) <= 540` for every `n >= 2`, every positive integer `R`, and every
vertex `x`.  This is a uniform state-weighted local-form coefficient; it is
not a claim that the generators already intertwine under refinement.

The R-488 cylinder remains nonzero in this norm.  At `G_2`, `R=1`, explicit
finite witnesses give
`(ell_a,ell_d,H_0,H_1)=(1,1,-1,-1)` with finite energies
`(29/12,35/12,77/12,77/12)`.  Every finite PAH state has strictly positive
Gibbs weight because the state space is finite and `epsilon>0`, so each
witness gives a strictly positive weighted squared norm.

## Source pins

| source | SHA-256 |
|---|---|
| PAH-001 | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| PAH-OMC-004 | `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c` |
| PAH-OMC-008 | `b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a` |
| PAH-OMC-009 | `1c57e9c46e65c950104fdf6310ef82da4369c35c5617bcacabd6c41767dff6de` |
| PAH-OMC-010 contract | `8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69` |
| PAH-OMC-010 manifest | `97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3` |
| Lean R490 (normalized) | `2f67655840eba25982976be1505320fbaa51dc89826bc33d447b6e2a46944b23` |

## Evidence and reproduction

```text
python codes/foundations/pah_omc010_state_weighted_envelope.py
python codes/foundations/pah_omc010_state_weighted_envelope_independent.py
python codes/foundations/pah_omc010_state_weighted_envelope_hostile.py
python verification/scripts/pah_omc010_state_weighted_envelope_verify.py
Set-Location verification/lean
lake env lean Tect/R490.lean
```

The primary lane passes 18/18 assertions, the non-importing independent lane
passes 13/13, hostile review rejects 9/9 invalid mutations, the integrated
verifier passes 16/16, and Lean R490 compiles.  The integrated artefact is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/integrated.json`.

## Classification and boundary

This is a T0 claim-nonbearing `MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE`
result recorded as `R-490 / EXP-001438`.  It supplies a finite,
family-uniform state-weighted local-form coefficient that may be used as an
input to common-core refinement only after a separate rootwise and eventual
generator-intertwining proof.

It does not prove that intertwining, an infinite-volume automorphism, an
ordered limit, or uniformity in omitted cutoff parameters.  It does not repair
the R-489 unweighted sup-state divergence.  No physical Pre-A, Sector-A,
physical vacuum, spacetime, event horizon, gravity, QFT, Yang--Mills,
continuum, mass-gap, cosmic-origin or TOE conclusion follows.  Markov time
remains external stochastic time.

## Next evidence contract

Create a separately hashed rootwise/eventual cylinder-intertwining packet that
uses the same PAH-001 functional, directed root labels, neutral inclusions,
and the Gibbs-weighted common norm.  Keep the active Stage 2 gate
`HOLD_FOR_EVIDENCE` until that packet is independently verified.
