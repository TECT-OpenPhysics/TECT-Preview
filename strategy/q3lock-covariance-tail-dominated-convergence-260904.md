# Q3LOCK covariance convergence with the interpolation shape factor

**Status:** T0 research addendum; explicit finite-time-grid audit  
**Date:** 2026-09-04  
**Owner task:** T-054  
**PDF:** deferred

## 1. Fourier representation

Keep `Lambda`, `beta`, `m>0`, and `a>0` fixed and set `epsilon=beta/N`.  Use
the cyclic representatives

```text
J_N = { -floor((N-1)/2), ..., floor(N/2) }
```

for the temporal Fourier modes, with `theta_(N,l)=2*pi*l/N`.  If `t` lies in
the cell `[k*epsilon,(k+1)*epsilon]` and `u=(t-k*epsilon)/epsilon`, the
periodic linear interpolant has mode factor

```text
h_(N,l)(t) = exp(i*theta_(N,l)*k)
              * [(1-u)+u*exp(i*theta_(N,l))].
```

The bracket has modulus at most one.  Thus the one-component interpolated
covariance is

```text
C_N(t,s) = sum_(l in J_N)
              h_(N,l)(t) conjugate(h_(N,l)(s))
              / (N*kappa_(N,l)),
```

where

```text
kappa_(N,l) = a*epsilon
              + (2*m/epsilon)*(1-cos(theta_(N,l))).
```

## 2. A summable tail majorant

The zero mode satisfies

```text
1/(N*kappa_(N,0)) = 1/(a*beta).
```

For a nonzero representative `l`, let `rho=min(|l|,N-|l|)`, so
`1<=rho<=N/2`.  The elementary sine bound on `[0,pi/2]` gives

```text
1-cos(2*pi*l/N)
  = 2*sin^2(pi*rho/N)
  >= 8*rho^2/N^2.
```

Comparing the denominator to its kinetic part therefore yields

```text
1/(N*kappa_(N,l))
  <= epsilon/[2*m*N*(1-cos(theta_(N,l)))]
  <= beta/(16*m*rho^2).                                  (2.1)
```

The right side is summable over the two representatives `+rho` and `-rho`,
independently of `N`.  Since the interpolation factors have modulus at most
one, (2.1) is a uniform Weierstrass majorant for every covariance summand.

## 3. Fixed-mode limit

For each fixed integer `l`, take the representative in `J_N` for all large
`N`.  Then

```text
kappa_(N,l)/epsilon
  = a + (2*m/epsilon^2)*(1-cos(2*pi*l/N))
  -> a + m*(2*pi*l/beta)^2,
```

and the interpolation bracket tends to one while
`exp(i*theta_(N,l)*k)` tends to `exp(i*2*pi*l*t/beta)` whenever the cell index
and fractional position represent the fixed time `t`.  The same holds for
`s`.  Consequently each fixed covariance summand converges to

```text
exp(i*2*pi*l*(t-s)/beta)
  / [beta*(a+m*(2*pi*l/beta)^2)].
```

The majorant (2.1), together with the separate zero mode, permits dominated
convergence of the mode sum.  Hence, for every finite set of times and
components,

```text
C_N(t,s) -> C_a(t,s)
  = (1/beta) sum_(l in Z)
      exp(i*2*pi*l*(t-s)/beta)
      / [a+m*(2*pi*l/beta)^2].
```

This is the covariance kernel of the centered periodic Gaussian with
quadratic action

```text
(1/2) integral_0^beta [m*|dot omega|^2+a*|omega|^2] d tau.
```

The absolute convergence of the limiting series also gives continuity of
`C_a`; the increment estimate in
`q3lock-gaussian-increment-estimate-audit-260904.md` supplies the uniform
Kolmogorov tightness needed to upgrade this finite-dimensional convergence to
weak convergence in the periodic sup norm.

## 4. Audit boundary

The mode-majorant argument is for fixed finite `Lambda` and fixed positive
`a`; it is not a spatial-volume or `a->0` uniform estimate.  An independent
reviewer must check the precise cell-index convention at the periodic seam,
the complex-conjugation convention in the covariance, and the normalization
of the continuum action before the result is copied into a manuscript.
No interacting-weight limit, FKG path theorem, source cusp, DLR multiplicity,
independent claim, release, or PDF is created by this addendum.
