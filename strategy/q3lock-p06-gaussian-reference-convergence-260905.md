# Q3LOCK P-06 Gaussian reference convergence and weighted loop-limit audit

**Status:** T0 fixed-volume analytic audit; external review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and boundary

The preceding P-06 audit isolated a massive periodic Gaussian reference and
proved mesh-uniform increments, but left its convergence to the continuous
periodic Gaussian loop measure as an explicit insertion.  This note supplies
that insertion at fixed spatial volume.  It also records the compact-set
Riemann-sum argument that turns the Gaussian convergence into convergence of
the residual-weighted Q3LOCK loop laws.

The spatial cube is fixed throughout.  No spatial thermodynamic limit,
weighted tempered compactness, common infinite-volume operator core, source
tangent, strict cusp, or DLR multiplicity is asserted.  The note is not a
claim card and does not authorize a manuscript PDF.

## 2. Discrete massive Gaussian and its Fourier covariance

Fix `Lambda_L` with `V=L^3`, `N` time slices, `epsilon=beta/N`, and
`m=chi/hbar^2>0`.  For one scalar coordinate use the normalized centered
Gaussian with action

```text
S_G,N(x) = (1/2) sum_k [(m/epsilon)*(x_(k+1)-x_(k))^2
                       + a*epsilon*x_(k)^2],    a>0.
```

With the unitary cyclic Fourier basis, the precision eigenvalues are

```text
kappa_(N,j) = 4*m/epsilon*sin^2(pi*j/N) + a*epsilon,
              j=0,...,N-1.
```

The vertex covariance at cyclic separation `r` is

```text
G_N(r) = (1/N)*sum_(j=0)^(N-1) exp(2*pi*i*j*r/N)/kappa_(N,j).
```

Since `N*epsilon=beta`, reindexing the modes by their least absolute
representatives gives

```text
G_N(r) = (1/beta)*sum_(n in I_N)
   exp(2*pi*i*n*(epsilon*r)/beta)
   / [a + (4*m/epsilon^2)*sin^2(pi*n/N)],
```

where `I_N` contains one representative of every residue class modulo `N`.
For `0<|n|<=N/2`,

```text
sin(pi*|n|/N) >= 2*|n|/N,
```

and hence

```text
0 <= 1/[a+(4*m/epsilon^2)*sin^2(pi*n/N)]
   <= beta^2/(16*m*n^2).
```

For every fixed integer `n`, the denominator converges to
`a+4*pi^2*m*n^2/beta^2`.  The displayed `n^(-2)` majorant is summable and is
uniform in `N`; the zero mode is bounded by `1/a`.  Dominated convergence of
the Fourier series therefore gives, whenever `epsilon*r_N -> tau`,

```text
G_N(r_N) -> G_a(tau),
G_a(tau) = (1/beta)*sum_(n in Z)
   exp(2*pi*i*n*tau/beta)
   / [a + 4*pi^2*m*n^2/beta^2].
```

The same majorant makes the convergence uniform in `tau` on the time circle.
The function `G_a` is the covariance of the centered periodic Gaussian loop
with formal action

```text
(1/2)*integral_0^beta [m*|dot x(tau)|^2 + a*|x(tau)|^2] d tau.
```

## 3. Interpolation and weak convergence on periodic continuous loops

Let `I_N` be the periodic piecewise-linear interpolation of the vertices.
For a time `tau` in the interval with left endpoint `k*epsilon`,

```text
|I_N x(tau)-x_(k)|^2 <= |x_(k+1)-x_(k)|^2.
```

The cyclic resistance estimate from the preceding audit gives

```text
E_gamma |x_(k+1)-x_(k)|^2 <= epsilon/m.
```

Thus interpolation changes every evaluation by a quantity converging to zero
in `L^2`.  The vertex covariance convergence in Section 2 consequently gives
finite-dimensional convergence of `I_N x` to the Gaussian process with
covariance `G_a`.  For the eight components and the `V` spatial sites the
coordinates are independent copies, so the fixed finite product has the same
finite-dimensional convergence.

For tightness, the Gaussian moment estimate and the cyclic resistance bound
give, for every `p>=2`,

```text
E_gamma |x_(k)-x_(l)|^p <= C_p*(epsilon*r)^(p/2),
```

where `r` is the cyclic separation.  Decomposing an interpolated increment
into its two fractional endpoint increments and the vertex increment yields

```text
E_gamma |I_N x(tau)-I_N x(sigma)|^p
   <= C'_p*dist_circle(tau,sigma)^(p/2).
```

Choosing `p>2` and applying Kolmogorov's criterion on the circle proves
tightness in `C_per([0,beta])`.  Together with Section 2 this establishes

```text
gamma_(N,L) o I_N^(-1)  ==>  gamma_(a,L)
```

in the finite product periodic sup-norm topology.  This is a fixed-`L`
statement; it is not the KP weighted tempered topology.

## 4. Residual Riemann sums on compact loop sets

Write the exact finite-grid law as

```text
mu_(N,L,h)(dx) = Z_(N,L,h)^(-1)
                 exp(-R_(N,L,h)(x)) gamma_(N,L)(dx).
```

The auxiliary harmonic term with coefficient `a` is included in the Gaussian
reference and subtracted in `R`; after recombination it is the original
Q3LOCK local potential.  The residual contains only time-integrated local
polynomials, spatial bond polynomials, and the linear source.  For a compact
set `K` in the finite product `C_per` space, Arzela--Ascoli gives a common
sup-norm bound and equicontinuity.  Every residual integrand is uniformly
continuous on the resulting bounded range.  Uniform Riemann-sum convergence
therefore gives

```text
sup_{I_N x in K} |R_(N,L,h)(x)-R_(L,h)(I_N x)| -> 0,
```

uniformly for `|h|<=h_0`.  The source term needs no error estimate because
piecewise-linear interpolation satisfies the exact identity

```text
integral_0^beta (u,I_N x_y)(tau) d tau
   = epsilon*sum_k (u,x_(y,k)).
```

The temporal kinetic term is not compared as a Riemann sum; it is carried by
the Gaussian convergence in Sections 2--3.

## 5. Weighted-law convergence and denominator control

The quartic lower bound from the coercivity audit has the form

```text
R_(N,L,h)(x) >= alpha*S4_(N,L)(x) - beta*V*C_(a,h_0),
alpha=g/128.
```

Consequently the residual weights obey the mesh-uniform envelope

```text
0 <= exp(-R_(N,L,h)(x)) <= exp(beta*V*C_(a,h_0)).
```

For a bounded continuous test functional `F`, tightness of the Gaussian laws,
the compact convergence in Section 4, and this envelope imply

```text
E_gamma[F(I_N x)*exp(-R_(N,L,h)(x))]
  -> E_(gamma_(a,L))[F(x)*exp(-R_(L,h)(x))].
```

The centered-Gaussian Jensen estimate gives the additional explicit bound

```text
Z_(N,L,h) >= exp(-beta*V*C_(L,h_0)) > 0,
```

uniformly in `N` and `|h|<=h_0`.  The limiting normalizer is strictly positive
because the residual is finite on every continuous loop.  Division by the
normalizers therefore proves weak convergence of the normalized weighted
finite-grid laws to the exact finite-volume Q3LOCK loop law with the
recombined local potential.

For source derivatives, the quartic Holder--Young estimate in the companion
normalizer audit gives uniform integrability of
`exp(T*|X_(N,L)(a)|)` and
`X_(N,L)(a)^2*exp(T*|X_(N,L)(a)|)`.  The exact source identity in Section 4
then permits the same weak-limit argument for the first and second source
derivatives.  This is the precise fixed-volume input required before passing
the finite-grid FKG and FSS inequalities to the continuous loop law.

## 6. Disposition and strict boundary

**Advanced at T0:** the massive Gaussian vertex covariance converges to the
periodic continuum covariance; interpolation has vanishing vertex error;
finite-product loop laws converge in periodic sup norm; and the bounded
residual weights, Jensen denominator, compact Riemann sums, and source-UI
estimates give the fixed-volume weighted-loop passage.

**Still open:** independent verification of the Gaussian comparison and all
constants; the finite FKG and FSS theorem hypotheses; the spatial limit and
tempered topology; operator common-core and trace differentiation; pressure
and source-tangent composition; and the final external referee audit.

No strict infrared lower bound, source cusp, phase coexistence, DLR
multiplicity, extremality, purity, clustering, real-time dynamics, KMS state,
ground-state gap, continuum limit, physical-vacuum or cosmological conclusion
is inferred.

## 7. Adversarial checks

1. **Use only vertex covariance convergence.**  Rejected: interpolation error
   is separately bounded in `L^2`, and tightness is proved for interpolated
   paths.
2. **Treat the time kinetic action as a uniform Riemann sum.**  Rejected: the
   kinetic term is encoded in the Gaussian reference; only residual terms are
   compared by compact-set Riemann sums.
3. **Ignore high discrete Fourier modes.**  Rejected: the uniform `n^(-2)`
   majorant controls the reindexed tails and justifies dominated convergence.
4. **Use a source derivative without uniform integrability.**  Rejected: the
   quartic Holder--Young estimate and Jensen denominator are load-bearing.
5. **Call fixed-`L` convergence a thermodynamic theorem.**  Rejected: every
   constant and topology statement in this note is finite spatial volume.
6. **Generate the publication PDF after this insertion.**  Rejected: the
   independent audit, claim/result registration, content freeze, clean replay,
   and release gates remain ahead.

## 8. Reproduction and review gate

The Fourier tail bound, covariance limit, interpolation estimate, and residual
compact convergence must be checked line-by-line in the independent Q3LOCK
proof audit.  This note is an analytic proof-text input, not a numerical fit or
a replacement for external source review.  PDF compilation and visual review
remain final-stage actions only.
