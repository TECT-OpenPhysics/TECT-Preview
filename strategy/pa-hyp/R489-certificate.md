# R-489 certificate — PAH-OMC-009 uniform interaction-envelope obstruction

## Exact proposition

The separately versioned researcher-owned PAH-OMC-009 contract keeps the
displayed PAH-001 functional, move families, endpoint mobility and midpoint
rate unchanged.  It fixes the cofinal PAH-OMC-004 two-row strip family
`G_n`, `n >= 2`, the neutral geometric inclusions `J_(n,n+1)`, and the
geometric root-support weight `w(r)=1+|supp(r)|`.  The declared interaction
envelope is required to be finite uniformly in the PAH-001 local-state path
`R_max = R -> infinity` and in the strip level.

At `b=(1,0)`, which has degree four in every `G_n`, use the admissible
`Q=1` state with one radial quantum at `b`, aperture `s_b=1/2`, all other
apertures equal to one, neutral phases and links, and the aperture root
`r_b=AP(b,+1)`.  The exact unchanged PAH-001 energy increment is

```text
Delta F_n(omega_R,r_b) = -(7/24) R^2 - 5/8.
```

The endpoint-product mobility has square `1/2`, so the unchanged midpoint
rate is

```text
c_(r_b)(omega_R) = 2^(-1/2) exp(7 R^2 / 48 + 5/16).
```

Because `w(r_b) >= 1`, this one root gives a lower bound for the requested
interaction sum that diverges as `R -> infinity`, independently of the strip
level.  Therefore the declared regulator-independent envelope is false.

## Source pins

| source | SHA-256 |
|---|---|
| PAH-001 | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| PAH-OMC-004 | `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c` |
| PAH-OMC-008 | `b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a` |
| PAH-OMC-009 | `1c57e9c46e65c950104fdf6310ef82da4369c35c5617bcacabd6c41767dff6de` |
| PAH-OMC-009 manifest | `3992d7228cfeec5f229d701657673548b18576c31572546050ad06405838d555` |
| Lean R489 (normalized) | `c3dd7dfe1c8995df6e3b28ebf04aedb73611014078d665805310b3035479c18f` |

## Reproduction and outcome

```text
python codes/foundations/pah_omc009_uniform_envelope.py
python codes/foundations/pah_omc009_uniform_envelope_independent.py
python codes/foundations/pah_omc009_uniform_envelope_hostile.py
python verification/scripts/pah_omc009_uniform_envelope_verify.py
Set-Location verification/lean; lake env lean Tect/R489.lean
```

The primary lane passes 16/16 assertions, the non-importing independent lane
passes 13/13, hostile review rejects 6/6 invalid mutations, the integrated
verifier passes 21/21, and Lean R489 compiles.  The exact witness has degree
four, support
`{(0,0),(1,0),(1,1),(2,0),(2,1)}`, weight six, and rate exponent
quadratic coefficient `7/48`.

## Classification and boundary

This is a `NEGATIVE_RESULT` for the single declared PAH-OMC-009
cutoff-independent root-rate envelope target.  It is a T0 claim-nonbearing
researcher-owned model-level result.  The eventual generator-intertwining
question is deliberately `NOT_DECIDED_AFTER_ENVELOPE_FAILURE`; no new
boundary calculation or repair is used to decide it.

The result does not falsify PAH-001, R-488, every state-weighted or
energy-domain norm, or every future owner contract.  It does not establish a
source-owned production dynamics, a global common core, an infinite-volume
automorphism, an ordered limit, a continuum theorem, or any physical sector.
There is no physical Pre-A, spacetime, event-horizon, gravity, QFT,
Yang--Mills, mass-gap, cosmic-origin or TOE conclusion.  Markov time remains
external stochastic time.

## Next evidence contract

Reopen only with a separately hashed owner-authorized interaction norm that
states which PAH-001 cutoff parameters are held fixed, supplies a positive
state/root weight and common domain, and proves its own regulator scope
without counterterms, averaging or fitted rates.
