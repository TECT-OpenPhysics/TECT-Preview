# Q3LOCK Duhamel and source normalization audit

**Status:** T0 research addendum; notation and factor audit  
**Date:** 2026-09-04  
**Owner task:** T-054  
**PDF:** deferred

## 1. Convention fixed for this paper

For zero-source finite-volume loop expectations define

```text
D_(L)(y,z) = (1/beta) * integral_0^beta
             Cov(Q_y(tau), Q_z(0)) d tau.
```

This is the convention used in the Bruch--Falk lower bound and in the
zero-mode density

```text
Pi_L = V^(-2) * sum_(y,z) D_(L)(y,z)
      = V^(-1) * Dhat_L(0).
```

The paper must not silently replace this by the unnormalized integrated
covariance.  If `D_int(y,z)=integral_0^beta Cov(...) d tau`, then
`D_int=beta*D_(L)`.

## 2. Constant-source moment identity

Let

```text
X_L = sum_y integral_0^beta Q_y(tau) d tau.
```

Time-translation invariance gives

```text
Var_0(X_L)
 = beta * sum_(y,z) integral_0^beta Cov(Q_y(tau),Q_z(0)) d tau
 = beta^2 * sum_(y,z) D_(L)(y,z)
 = beta^2 * V^2 * Pi_L.
```

Therefore the Griffiths variable normalized by `beta*V` satisfies

```text
E_0[(X_L/(beta*V))^2] = Pi_L.
```

The Euclidean source tilt is `exp(h X_L)`.  The fine energy pressure obeys

```text
V^(-1) log E_0 exp(h X_L)
   = 8*beta*[P_(beta,L)(h)-P_(beta,L)(0)].
```

Consequently the subgradient bound gives
`beta^2 limsup Pi_L <= [8*beta*D_+P_beta(0)]^2`, with no missing or extra
factor of `beta`.

## 3. Reflection-positivity factor

For the weighted loop inner product
`<f,g>_K=integral_0^beta f(tau)g(tau)d tau`, Gaussian domination reads

```text
log E_0 exp(<j,omega>_K)
  <= (1/(2c)) <j,L_sp^(-1)j>_K.
```

For `j_y(tau)=s*a_y*u`, the second derivative of the left side is
`beta^2*a^T D_(L) a`, while the right side is
`(beta/c)*a^T L_sp^(-1) a`.  Since the spatial Laplacian eigenvalue is
`2*E(p)`,

```text
Dhat_L(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

This is the bound used in the infrared sum.  If an external source writes its
covariance with a different beta normalization, the conversion must be made
before importing its displayed constant.

## 4. Bruch--Falk cross-check

For a harmonic test oscillator with mass `chi` and frequency `omega`, the
convention above gives

```text
(Q,Q)_D = 1/(beta*chi*omega^2),
<[Q,[beta*H,Q]]> = beta*hbar^2/chi.
```

The Falk--Bruch function therefore satisfies the exact equality

```text
(Q,Q)_D = <Q^2>*f(<[Q,[beta*H,Q]]>/(4*<Q^2>)),
```

which is the normalization test used by the independent verifier.  This
check prevents replacing `beta*hbar^2/chi` by `hbar^2/chi` or replacing the
Duhamel covariance by the unnormalized time integral.

## 5. Scope and next gate

The calculation fixes notation and all beta/factor-eight conversions used by
P-08, P-09, P-10 and P-12.  It does not prove the FSS loop limit, the
continuous-loop FKG limit, the thermodynamic pressure limit, or the phase
conclusion.  The manuscript and an independent reviewer must reproduce these
identities before claim registration.  No independent claim, manuscript,
release or PDF is created by this addendum.

