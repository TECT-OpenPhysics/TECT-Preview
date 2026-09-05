# Q3LOCK collective dictionary and limit-order audit

**Status:** T0 independent normalization and limit-order audit; no gate closure  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Companion proof text:** `strategy/q3lock-p06-p09-independent-proof-audit-round2-260905.md`  
**PDF:** deferred until content freeze and external review

## 1. Question and boundary

This audit independently recomputes the source, beta, component-count and
volume factors in the inserted collective-source subsection.  It also checks
that the finite trace, time-grid, spatial-volume, source and DLR limits occur
in a legal order.  The audit is a paper-local crosswalk.  It does not certify
the EXP-000780 theorem, the P-06/P-09 loop passages, a cusp, or DLR
multiplicity.

## 2. Finite energy-source calculation

Let `V=L^3`, let `u=(1,...,1)/sqrt(8)`, and write `Q_y=u dot q_y`.  The
EXP-000780 finite pressure is

```text
pi_(beta,L)(J)=(1/(8V))*log Z_(beta,L)(J),
P_(beta,L)(J)=pi_(beta,L)(J)/beta.
```

On the collective line `J=h*u`,
`H_L(h)=H_L(0)-h*sum_y Q_y`.  Defining the per-cell quantities

```text
p_col(beta,L,h)=(1/V)*log Z_(beta,L)(h*u),
P_col(beta,L,h)=p_col(beta,L,h)/(8*beta),
```

gives, identically,

```text
p_col=8*pi_(beta,L)(h*u),
P_col=P_(beta,L)(h*u).
```

The trace derivative is obtained from the finite-dimensional Duhamel formula
for the energy source:

```text
p_col'(h)=(beta/V)*<sum_y Q_y>_(L,h),
P_col'(h)=(1/(8V))*<sum_y Q_y>_(L,h)
           =(1/8)*<Q_0>_(L,h),
```

where the last equality uses the declared periodic translation invariance.
No componentwise sign symmetry is needed.

## 3. Euclidean and Duhamel calculation

The periodic Feynman--Kac formula for the same energy source is

```text
Z_(beta,L)(h*u)/Z_(beta,L)(0)
  = E_(L,0) exp(h*X_L),
X_L=sum_y integral_0^beta Q_y(tau) d tau.
```

Therefore

```text
(1/V)*log E_(L,0) exp(h*X_L)
  = p_col(beta,L,h)-p_col(beta,L,0)
  = 8*beta*(P_col(beta,L,h)-P_col(beta,L,0)),
```

and its derivative is
`E_(L,h)[X_L]/V=8*beta*P_col'(h)`.  Thus the Euclidean exponential uses `h`,
not `beta*h`; beta enters when the pressure is divided by `8*beta`.

At zero source, global parity makes the collective mean zero.  With

```text
C_(yz)(tau)=Cov(Q_y(tau),Q_z(0)),
D_L=(1/beta)*integral_0^beta C(tau) d tau,
```

time translation gives

```text
Var(X_L(a))=beta^2*<a,D_L a>.
```

The KKK convention is the double-integral covariance, so a unit collective
projection satisfies `D_KKK^u=beta^2 D_L`.  This agrees with the choices
`U_L=X_L` and `M_L=V` in the endpoint-interval Griffiths application.  The
factor eight belongs to `p_col=8*pi`, not to `M_L`.

## 4. Limit-order audit

The only order justified by the current proof spine is:

1. Fix beta, a finite periodic volume and a source `h` in the common compact
   source window.
2. Establish the finite trace identity and pass the time mesh to the
   continuous loop law at fixed spatial volume, using the P-06/P-09 tightness
   and source-uniform-integrability obligations.
3. Take the declared even periodic spatial-volume pressure limit on compact
   vector-source sets and restrict it to `J=h*u`.
4. Use convexity to obtain one-sided pressure derivatives at positive sources;
   use the KKK endpoint interval with `U_L=X_L`, `M_L=V` only after the
   pressure limit and its log-MGF hypotheses are available.
5. Compose the positive-source tangent states with the separate EXP-000781
   source-to-zero specification-continuity argument.

The audit does not commute the source-to-zero limit with the spatial limit and
does not use the zero-mode Poisson inverse at `p=0`.  The collective line is a
restriction of the vector source theorem, not a new pressure theorem.

## 5. Adversarial checks

| Check | Disposition | Boundary |
|---|---|---|
| Replace `J=h*u` by `J_e=h` in every component | **UPHELD AS FALSE** | The normalized line has `J_e=h/sqrt(8)` and `|J|=|h|`. |
| Put `beta*h` in `exp(beta*h*X_L)` | **UPHELD AS FALSE** | `h` is an energy source; the time integral supplies the beta in the derivative conversion. |
| Use `8V` as the KKK normalization scale | **UPHELD AS FALSE** | KKK uses the coarse-cell count `M_L=V`; the fine count is already in `pi`. |
| Apply the source-to-zero DLR limit before the pressure limit | **UPHELD AS FALSE** | The current composition requires a common compact source window and specification continuity; no interchange is claimed. |
| Treat the collective restriction as Q3/O(8) rotational symmetry | **UPHELD AS FALSE** | The Q3LOCK onsite law remains nonradial; only the source is restricted. |
| Read this audit as a strict cusp or phase result | **UPHELD AS FALSE** | P-06/P-09, zero-mode, endpoint slope and DLR multiplicity remain open. |

## 6. Disposition and next gate

The inserted proof-text dictionary is algebraically and dimensionally
consistent with the declared EXP-000780 source and with the KKK Duhamel
convention.  The limit-order ledger is explicit and does not hide a joint
limit.  This is an **advanced T0 normalization audit**, not an external
mathematical sign-off.  The next gate is independent line-by-line review of
the P-06/P-09 estimates, the finite trace/form-domain hypotheses, and the
pressure-limit composition.

## 7. Explicit nonclaims

This audit does not assert a strict source cusp, positive zero-mode lower
bound, phase coexistence, extremality, purity, clustering, a KMS state, real-
time dynamics, a ground-state phase, a spectral gap, a continuum limit, a
physical-vacuum interpretation, a cosmological conclusion, Sector A, CP1,
C6, Pre-A, or Yang--Mills closure.  No claim card, manuscript release,
submission package, or PDF is created.
