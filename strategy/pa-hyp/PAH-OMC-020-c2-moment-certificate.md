# PAH-OMC-020 C2(A) source-owned local second-rate-moment certificate

## Decision

`PASS` at a scoped auxiliary checkpoint (`R-522`).  The unchanged PAH-001
midpoint rates and normalized Gibbs state give a source-owned local
second-rate-moment bound on the registered PAH-OMC-010 path.  The bound is an
input to a temporal proof; it does not close the temporal route.

## Frozen source and scope

The following source bytes were pinned before the audit:

| source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json` | `8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69` |
| `strategy/pa-hyp/R490-certificate.md` | `80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |

The functional, directed move set, mobility, labelled Gibbs state, OMC-004
strip, `K=2`, `M_s=M_psi=1`, `Q=1`, `epsilon=1/2`, `beta=nu=1`, unit
couplings, `n>=2`, `R_max=R>=1`, external stochastic time and `j`-before-
anchored-`n` order are unchanged.  No counterterm, averaging, rate fitting,
new carrier or new physical interpretation is introduced.

## Exact calculation

For a directed PAH root `r`,

```text
c_r(x) = m_r(x) exp[-beta(F(r x)-F(x))/2],
pi(x)  = Z^(-1) exp[-beta F(x)].
```

Therefore, on the partial-bijection domain of `r`,

```text
pi(x)c_r(x)^2
  = Z^(-1) exp[-beta F(x)] m_r(x)^2
             exp[-beta(F(r x)-F(x))]
  = Z^(-1) m_r(x)^2 exp[-beta F(r x)].
```

The source aperture range is `0<s<=1` and the registered path has `nu=1`.
Thus the exact squared mobility is at most one for every source move:

```text
phase:    m^2 = s_v^2 <= 1,
transfer: m^2 = s_v s_w <= 1,
aperture: m^2 = s_before s_after <= 1.
```

The inverse-root map is injective from its domain to its image, so

```text
sum_(x in dom(r)) pi(x)c_r(x)^2
  <= Z^(-1) sum_(y in image(r)) exp[-beta F(y)]
  <= 1.
```

R-490 supplies the source-derived geometric incidence constant
`N_geom=60`: at most 60 directed roots have a support containing any one
vertex, uniformly in the strip level.  For a finite local support `A`,

```text
C2(A) = sup_(n,R) sum_(r:supp(r) intersects A)
             sum_(x in dom(r)) pi_(n,R)(x)c_r(x)^2
       <= N_geom |A| = 60 |A|.
```

If `D_r f(x)=f(r x)-f(x)` and `f` is a bounded local cylinder with support
`A`, pointwise Cauchy--Schwarz followed by the preceding bound gives the
usable local estimate

```text
||L f||_(L2(pi))^2
  <= C2(A) sum_(r:supp(r) intersects A) ||D_r f||_infinity^2.
```

This is a genuine second-rate-moment estimate, not a reuse of the R-490 first
moment `C_sw=540`.  R-489's unweighted `R_max` divergence is a different norm
target and remains unchanged.

## Verification

Primary, non-importing independent and hostile lanes, plus Lean, were run:

```text
python -X utf8 verification/scripts/pah_omc020_c2_moment.py --check
python -X utf8 codes/foundations/pah_omc020_c2_moment_independent.py --check
python -X utf8 codes/foundations/pah_omc020_c2_moment_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_c2_moment_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

The primary lane passes 40 checks, the independent lane 31, the hostile lane
17, and the integrated verifier 25.  Lean 4.32.1 compiles six declarations in
`verification/lean/Tect/PahOmc020C2.lean`; the registry entry is hash-pinned.
The persisted run artefacts are:

| artefact | SHA-256 |
|---|---|
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-c2-moment/primary.json` | `70875a114b40c8b9beeec469bdd7f9680c8bd7db4e6a69268b07c800cd6d957b` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-c2-moment/independent.json` | `2e8fbbb466822d3148a49f2055763c522a261b12f5356876d0bd6871d210cb5f` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-c2-moment/hostile.json` | `d27bf349d3217f8444af342184f8eac2a1ff3490e35607b3db98bf6429292253` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-c2-moment/integrated.json` | `942e4db0942c029c050e20ea16a3daaa2e6a0ed0457e2561ee2bf99a16deea44` |

Lean source SHA-256 is
`d4e522977ac7581990f826805198d292478f52e3c6cfb59e9ab20b0092cacdce`.

## Adversarial review

* **Mobility cap.**  A hypothetical `m>1` would invalidate the per-root
  bound; the hostile lane rejects this as a source-rate mutation.  The
  registered PAH aperture, transfer and phase mobilities obey `m<=1`.
* **Gibbs cancellation.**  Replacing the target weight by the source weight
  would lose the exact square cancellation; the proof keeps the inverse-root
  image and the normalized partition sum explicitly.
* **Volume dependence.**  `N_geom=60` is a per-vertex support-incidence bound,
  not a total root count.  The estimate is only for finite `A`, as required.
* **First versus second moment.**  `C_sw=540` controls `sum pi*c`; this
  certificate separately proves `sum pi*c^2<=1` from the midpoint rate.
* **Promotion.**  The local estimate does not provide a path-space law,
  non-explosion, N2b/N2c/N4, R-512 identification or anchored-`n` limit.

## Remaining boundary

`R-522` is `auxiliary_support`, `claim_bearing=false` and leaves the active
T-054 gate unchanged.  The next single question is whether this C2 estimate
can be combined with a source-authorized path-space/non-explosion argument and
the missing N2b, N2c/N4 and N2d identifications.  Until those are supplied,
PAH-OMC-020 remains `HOLD_FOR_EVIDENCE`.

There is no physical Pre-A, spacetime, event-horizon, QFT, gravity,
Yang--Mills, continuum, mass-gap or TOE conclusion.  Markov time remains
external stochastic bookkeeping.
