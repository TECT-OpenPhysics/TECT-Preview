# PAH-OMC-014 Q=0 component push-forward obstruction

**Status:** route-local `NEGATIVE_RESULT`; no claim-tier or active-gate change  
**Date:** 2026-09-05  
**Task:** T-054  
**Negative authority:** `AUDIT-2026-09-05-PAH-OMC-014-Q0-COMPONENT-PUSHFORWARD`  
**Exploration:** `EXP-001535` (append-only ledger)

## Question and exact scope

The PAH-OMC-014 projective-kernel obligation asks whether a fine component
Gibbs state can push forward through a normalized grade kernel to the coarse
component states.  This note tests the one component where the grade kernel is
forced, rather than chosen:

```text
G_3 -> G_2,  K=2,  M_s=M_psi=1,  epsilon=1/2,
beta=1, nu=1, R_max=1, m2=0,
lambda_s=lambda_4=eta_6=g=kappa_s=kappa_D=kappa_g=1, theta=0, Q_f=0.
```

The carrier is the two-row PAH-OMC-004 strip.  The map retains the old column,
drops the new column and its diagonal link, and recomputes the coarse grade as
specified by PAH-OMC-012.  The test observable is the bounded grade-blind
aperture cylinder

```text
f(omega) = indicator(s_(0,0)=1).
```

No new carrier, rate, counterterm, weight, projection, or physical
interpretation is introduced.

## Hash-pinned sources

| source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-004-v1.json` | `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c` |
| `strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json` | `180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72` |

The PAH-001 functional is used exactly as displayed:

```text
F_rho = sum_v lambda_s(s_v-1)^2/2 + ...
      + kappa_s sum_e(s_v-s_w)^2/2
      + kappa_D sum_e J_e(s)|psi_w-U_e psi_v|^2/2
      + kappa_g sum_p J_p(s)(1-Re U_p),
J_e(s)=2/(s_v+s_w),  J_p=average_boundary J_e.
```

At `Q=0`, all nonnegative radial occupations vanish, so `psi=0`; vertex
phases have a constant multiplicity within each normalized expectation and
cancel.  For `K=2`, the link variables reduce exactly to `Z_2` face fluxes.
The G2 strip has 12 edges and 5 faces, with flux rank 5 and fibre multiplicity
`2^(12-5)=128`; G3 has 16 edges and 7 faces, with rank 7 and multiplicity
`2^(16-7)=512`.

## Exact witness

Let `Z_2` and `N_2` be the coarse partition and the partition weighted by
`f`, and let `Z_3` and `N_3` be the corresponding fine quantities after the
neutral restriction.  Every quantity is represented as an integer map

```text
sum_e c_e exp(-e),   e in Q,
```

after summing the exact binary apertures and exact `Z_2` flux fibres.  The
projective equality for the forced `Q_f=0 -> Q_c=0` kernel would require

```text
N_3/Z_3 = N_2/Z_2,
equivalently  Delta = N_3 Z_2 - N_2 Z_3 = 0.
```

The primary exact-Fraction lane and the non-importing direct link-enumeration
lane both produce a nonempty `Delta` map with:

```text
terms = 2784
SHA-256(map) = b66044e590399d959ab2947edf22f3aa2aeea4405473b88c4327da24058ebb93
leading term = 131072 exp(-1)
```

The coefficient map is over distinct rational (hence algebraic) exponents and
has integer coefficients.  Lindemann--Weierstrass linear independence of
exponentials of distinct algebraic numbers therefore makes this a proof of
exact nonvanishing; the 80-digit decimal diagnostic
`297525.4187029326484250953987116556947054782145018590174323755216922584` is
not used as the proof.

Since all dropped occupations are nonnegative, `Q_f=0` forces `Q_c=0`, so any
normalized grade-transition kernel on this component is the point mass
`K(Q_c|Q_f=0)=delta_(Q_c,0)`.  The nonzero `Delta` therefore rejects the
componentwise push-forward identity and its deterministic-grade kernel
factorization.

## Verification package

| lane | file | result |
|---|---|---|
| primary | `codes/foundations/pah_omc014_q0_projective_obstruction.py` | PASS 9/9, `NEGATIVE_RESULT` |
| independent | `codes/foundations/pah_omc014_q0_projective_obstruction_independent.py` | PASS 7/7, `NEGATIVE_RESULT`; exact map identical |
| hostile | `codes/foundations/pah_omc014_q0_projective_obstruction_hostile.py` | PASS 16/16, all mutations rejected |
| integrated | `verification/scripts/pah_omc014_q0_projective_obstruction_verify.py` | PASS 11/11, `NEGATIVE_RESULT` |

Run the package from the repository root:

```powershell
python -X utf8 codes/foundations/pah_omc014_q0_projective_obstruction.py
python -X utf8 codes/foundations/pah_omc014_q0_projective_obstruction_independent.py
python -X utf8 codes/foundations/pah_omc014_q0_projective_obstruction_hostile.py
python -X utf8 verification/scripts/pah_omc014_q0_projective_obstruction_verify.py
```

The canonical run files are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-q0-projective-obstruction/`:

```text
primary.json      7a2cae9367f917d6f2a96779d794bd9276bd33a4187faa377bf948a70a8df83b
independent.json  26db0d08095724ce0de9856dd6822ed5768a14157267609c387c12e13cdeb506
hostile.json      9535824cce7a27a0a052f488e717058977744c7da6741108f2ced6185b7d37d8
integrated.json   3938987009c2ccf1a81272655277f1fa21dbfddc47fd49e2497975dc86e7f6fe
```

The integrated lane records Lean as `NOT_APPLICABLE`: the current Lean bridge
does not formalize the transcendence step.  The finite algebra and exact map
are nevertheless reproduced independently, and the hostile lane rejects
Wilson-term removal, projection changes, fitted weights, counterterms,
decimal-only reasoning, and overclaiming.

## Boundary and next evidence contract

This is not a no-go for every full-Q law.  It does **not** exclude a global
cross-Q mixture in which other components cancel this component mismatch; it
does not define `w_(n,R,Q)`, a global normalized Gibbs state, a weak cylinder
limit, a Cauchy estimate, or stationarity.  The R-484 boundary and the
domination-only role of `C_sw=540` are unchanged.  There is no infinite-volume,
continuum, physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or
TOE conclusion, and Markov time remains external stochastic time.

The one next question is:

> Can a separately source-owned normalized cross-Q kernel and weight recursion
> establish full-mixture projectivity despite the Q_f=0 component mismatch,
> without fitted weights or any parent-model change?

Until that packet exists, PAH-OMC-014 remains `HOLD_FOR_EVIDENCE` at the
global level; this route-local negative only retires the deterministic-grade
component shortcut.
