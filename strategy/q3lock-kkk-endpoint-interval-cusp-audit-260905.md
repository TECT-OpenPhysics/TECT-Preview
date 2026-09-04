# Q3LOCK KKK endpoint-interval and cusp inequality audit

**Status:** T0 proof-text correction; independent mathematical review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Pinned source:** Kargol--Kondratiev--Kozitsky, Proposition 3.9,
arXiv:0710.2303v1, source hash recorded in
`strategy/q3lock-literature-source-freeze-260905.md`  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and strict boundary

The Q3LOCK pressure bridge uses the Griffiths moment-to-slope result of
Kargol--Kondratiev--Kozitsky (KKK).  A wording ambiguity must be removed before
the result is transcribed into a paper: KKK Proposition 3.9 has a general
endpoint-interval estimate (3.23), while its displayed special consequence
(3.24) assumes differentiability at the origin.  A cusp proof must use (3.23),
not (3.24).  This note makes that substitution explicit and checks every
factor in the Q3LOCK map.

This is a proof-text correction, not a claim card or an external referee
response.  It does not promote EXP-000782, does not assert a strict cusp or
DLR multiplicity, and does not authorize a manuscript or PDF.

## 2. Exact KKK statement being used

KKK Proposition 3.9 considers probability measures `mu_n` on `R` and positive
scales `M_n` with `M_n -> infinity`.  If

```text
f(y) = lim_n (1/M_n) log integral exp(y*u) mu_n(du)
```

exists and is finite, then for every continuous `g` satisfying a linear
exponential growth bound,

```text
limsup_n integral g(u/M_n) mu_n(du)
  <= max_{z in [f'_-(0), f'_+(0)]} g(z).                 (2.1)
```

The source's statements about convergence to a single value and the formula
labelled (3.24) additionally assume `f'_-(0)=f'_+(0)`.  That differentiability
assumption is not used in (2.1).

The choice `g(z)=z^2` is admissible because a quadratic is bounded by a linear
exponential.  Thus, for an even convex `f` with
`f'_+(0)=a` and `f'_-(0)=-a`, (2.1) gives

```text
limsup_n integral (u/M_n)^2 mu_n(du) <= a^2.             (2.2)
```

This is the required one-sided-slope bound even when `a>0` and `f` is
nondifferentiable at zero.

## 3. Q3LOCK pressure map

At zero source let

```text
X_L = sum_y integral_0^beta Q_y(tau) d tau,
M_L = V_L = |Lambda_L|,
mu_L = law of X_L.
```

EXP-000780 supplies the finite, locally uniform limit

```text
f(h) = lim_L (1/V_L) log E_(L,0) exp(h*X_L)
     = p_beta(h) - p_beta(0),
```

where `p_beta=8*beta*P_beta`.  The zero-source global parity makes `f` even,
and convexity gives finite one-sided derivatives.  Put

```text
a = f'_+(0) = 8*beta*D_+P_beta(0),
f'_-(0) = -a.
```

The exact zero-mode identity from the pressure audit is

```text
integral (u/M_L)^2 mu_L(du)
  = E_(L,0)[X_L^2]/V_L^2
  = beta^2*Pi_L,
Pi_L = Dhat_L(0)/V_L.                                  (3.1)
```

Applying (2.2) along the same periodic volume sequence therefore yields

```text
beta^2*limsup_L Pi_L <= (8*beta*D_+P_beta(0))^2,
D_+P_beta(0) >= (1/8)*sqrt(limsup_L Pi_L).              (3.2)
```

If the Q3LOCK local Falk--Bruch and nonzero-mode infrared estimates give
`liminf_L Pi_L >= delta_beta > 0`, then (3.2) gives

```text
D_+P_beta(0) >= sqrt(delta_beta)/8,
D_-P_beta(0) = -D_+P_beta(0),                           (3.3)
```

The second equality is parity, not an additional differentiability
assumption.  Consequently (3.3) is a strict directional cusp conditional on
the upstream zero-mode bound.

## 4. Limit-order and source checks

1. The thermodynamic log-MGF limit is taken before the one-sided derivative;
   finite-volume derivatives at `h=0` are not substituted into KKK.
2. The source is the energy source `-h*sum_y Q_y`, so
   `p_beta=8*beta*P_beta` and no additional beta remains in (3.3).
3. The KKK scale is `M_L=V_L`, not `beta*V_L`; the beta factors enter only
   through the Euclidean integral in `X_L` and the identity (3.1).
4. The volume-squared witness is `Pi_L=Dhat_L(0)/V_L`; using `Dhat_L(0)`
   without division by `V_L` would not match (2.1).
5. The pressure limit and endpoint slopes come from EXP-000780.  The
   finite-grid FSS and loop-limit arguments are upstream inputs and are not
   replaced by this convex-analysis step.

## 5. Adversarial checks

| Objection | Disposition | Consequence |
|---|---|---|
| KKK (3.24) can be cited directly while proving a cusp | **UPHELD AS FALSE** | (3.24) assumes differentiability; the manuscript must cite the general (3.23) endpoint interval instead. |
| The endpoint interval is unavailable because the pressure is even | **UPHELD AS FALSE** | Evenness gives the interval `[-a,a]`, which is exactly what (2.2) needs. |
| A quadratic test function violates the KKK growth condition | **UPHELD AS FALSE** | `z^2 <= C exp(k|z|)` for suitable positive constants. |
| The KKK bound can be applied to finite-volume derivatives before the limit | **UPHELD AS FALSE** | The proposition is a statement about the limiting log-MGF and its endpoint slopes. |
| A positive `Pi_L` alone proves a cusp without the pressure limit | **UPHELD AS FALSE** | The finite limiting log-MGF is an explicit KKK hypothesis supplied by EXP-000780. |

## 6. Corrected manuscript insertion

The eventual paper should state the following implication in place of any
reference to the differentiable special case:

```text
By KKK Proposition 3.9, equation (3.23), with g(z)=z^2 and M_L=V_L,
limsup_L E[(X_L/V_L)^2] <= max_{z in [f'_-(0),f'_+(0)]} z^2.
Since f(h)=p_beta(h)-p_beta(0) is even and
f'_+(0)=8 beta D_+P_beta(0), this gives
D_+P_beta(0) >= (1/8) sqrt(limsup_L Pi_L).
No differentiability of f at zero is assumed; strict positivity of the
right-hand side is precisely what establishes the cusp.
```

## 7. Disposition and remaining gate

The KKK endpoint-interval route is now algebraically explicit and removes the
only circular-looking use of the differentiable special case.  The correction
is **T0 advanced**, conditional on independent review of the KKK hypothesis
map, the EXP-000780 pressure limit, and the preceding zero-mode identity.
The Q3LOCK claim remains unregistered and the P2/PDF channel remains closed.

## 8. Explicit nonclaims

This note does not assert a positive `Pi_L`, strict cusp, phase coexistence,
DLR multiplicity, extremality, purity, clustering, real-time dynamics, KMS,
ground state, spectral gap, continuum limit, physical vacuum, cosmological
interpretation, C6, CP1, Sector A or Pre-A closure.  It creates no claim card,
manuscript release, submission, upload, tag, release or PDF.
