# Q3LOCK mesh-uniform normalizer bound by a Gaussian Jensen estimate

**Status:** T0 proof-strengthening addendum; P-06/P-09 remain open pending independent review  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and boundary

The finite-time-grid arguments for continuous-loop FKG and for the
Hilbert-valued FSS transfer both divide by a weighted Gaussian normalizer.  A
previous proof-text route obtained a lower bound by restricting the Gaussian
law to a sup-norm ball.  This addendum records a shorter, independently
checkable alternative: put only a positive harmonic temporal part in the
reference Gaussian and use Jensen's inequality on the remaining polynomial
action.  The estimate is uniform in the time-grid size at fixed finite spatial
volume and on a compact source interval.

This is a local analytic lemma.  It does not identify the time-grid limit with
a Feynman--Kac loop law, prove the interpolation modulus estimate, establish
FKG or reflection positivity, or close the spatial thermodynamic limit.  It
does not promote R-497, create a claim card or manuscript, or authorize PDF
production.

## 2. Reference Gaussian and residual action

Fix a finite spatial volume `Lambda` with `V` sites and a time mesh
`epsilon=beta/N`.  For one scalar coordinate at one site let

```text
S_G,N(x) = (1/2) sum_(k=0)^(N-1)
              [ (m/epsilon)(x_(k+1)-x_k)^2 + a*epsilon*x_k^2 ],
```

with periodic indexing, `m=chi/hbar^2>0` and a fixed harmonic split `a>0`.
The reference law `gamma_N` is the centered Gaussian obtained by taking the
product of this law over the `8V` site/component coordinates.  The remaining
finite-grid action can be written

```text
S_(N,L,h)(x) = epsilon*sum_(k,y) V_(h,a)(x_(y,k))
              + (epsilon*c/2)*sum_(k,<yz>) |x_(y,k)-x_(z,k)|^2,
```

where the spatial edge list is the declared finite-volume list.  The source
term `-h*u dot x_(y,k)` is included in `V_(h,a)`, not in the reference
Gaussian.  The corresponding normalizer is

```text
Z_(N,L)(h) = E_(gamma_N)[ exp(-S_(N,L,h)) ].
```

The Q3LOCK polynomial gives constants `A>0` and `B<infinity`, depending only
on the fixed finite volume, the compact interval `|h|<=h_0` and the model
parameters, such that

```text
V_(h,a)(q) >= A*|q|^4 - B.                         (2.1)
```

The same polynomial has a finite Gaussian expectation after the harmonic
split.  No sign assumption on its quadratic coefficient is needed for that
statement.

## 3. Uniform diagonal covariance bound

The precision eigenvalues of the scalar periodic Gaussian are

```text
lambda_j = 4*m/epsilon * sin^2(pi*j/N) + a*epsilon,
             j=0,...,N-1.
```

For `N>=2`, its diagonal covariance satisfies

```text
g_N(0) = (1/N)*sum_j lambda_j^(-1)
       <= 1/(beta*a) + (epsilon/(4*m*N))*sum_(j=1)^(N-1)csc^2(pi*j/N)
       = 1/(beta*a) + beta*(N^2-1)/(12*m*N^2)
       <= K_(m,a,beta),
```

where

```text
K_(m,a,beta) = 1/(beta*a) + beta/(12*m).
```

The identity `sum_(j=1)^(N-1)csc^2(pi*j/N)=(N^2-1)/3` is the standard finite
trigonometric sum; it can also be obtained by differentiating the logarithmic
derivative of `sin(N z)`.  For `N=1`, the first term alone gives the same
bound.  Thus the bound is independent of `N` and uses the positive harmonic
split to control the temporal zero mode.

Because the reference is centered Gaussian, for every site and component

```text
E_gamma[x_(y,k)^2] <= K_(m,a,beta),
E_gamma[x_(y,k)^4] <= 3*K_(m,a,beta)^2.             (3.1)
```

For a spatial bond, independence of distinct site factors gives

```text
E_gamma[ |x_(y,k)-x_(z,k)|^2 ] <= 16*K_(m,a,beta),  (3.2)
```

for the eight-component norm.  The Q3 locking monomial obeys the elementary
bound

```text
(x-y)^2*(x^2+y^2) <= 4*(x^4+y^4),                 (3.3)
```

so (3.1) controls every Q3 edge term.  Consequently there is a finite
constant `C_(L,h_0)` such that, simultaneously for all `N>=1` and
`|h|<=h_0`,

```text
(1/(beta*V))*E_gamma[S_(N,L,h)] <= C_(L,h_0).       (3.4)
```

The source contribution has zero reference expectation because the Gaussian
is centered.  If a later convention uses a non-centered reference, (3.4)
must be rederived with the corresponding mean; it is not silently inherited.

## 4. Jensen lower bound for the normalizer

Apply Jensen to the convex function `exp(-s)`:

```text
Z_(N,L)(h) = E_gamma[exp(-S_(N,L,h))]
            >= exp(-E_gamma[S_(N,L,h)])
            >= exp(-beta*V*C_(L,h_0)).               (4.1)
```

The estimate holds for every `N` and every `|h|<=h_0`.  It does not require a
positive-probability sup-norm event, and it remains valid even when the
residual quadratic part of `V_(h,a)` is negative.  Together with (2.1),

```text
exp(-S_(N,L,h)) <= exp(beta*V*B),                   (4.2)
```

because the spatial bond contribution is nonnegative in `S`.  Hence at fixed
`L` and compact source interval the normalized density relative to `gamma_N`
has the mesh-uniform bound

```text
exp(-S_(N,L,h))/Z_(N,L)(h)
    <= exp(beta*V*(B+C_(L,h_0))).                   (4.3)
```

This is the exact estimate needed when transferring Gaussian tightness to the
weighted laws.  It also supplies the denominator in the quartic Young
estimate used for source exponentials and second-derivative witnesses.

## 5. Consequence for the source-uniform integrability step

Let `X_(N,L)(a)=epsilon*sum_(y,k) a_y*(u,x_(y,k))` with fixed zero-sum spatial
test vector `a`.  Holder and Young give, for every fixed source bound `T` and
sufficiently small `delta>0`,

```text
T*|X_(N,L)(a)| <= delta*epsilon*sum_(y,k)|x_(y,k)|^4 + C_(T,delta,a,beta,L),
|X_(N,L)(a)|^2*exp(T*|X_(N,L)(a)|)
    <= C'_(T,delta)*exp(2*delta*epsilon*sum_(y,k)|x_(y,k)|^4).
```

Choosing `2*delta<A` and using (2.1), (4.1) gives a mesh-independent bound
for the weighted expectation of the right-hand side.  Therefore the passage

```text
E_(N,L,h)[exp(t*X_(N,L)(a))] -> E_(L,h)[exp(t*X_L(a))]
```

and the corresponding second-moment passage may be justified by truncation
once the separate weak-convergence and Feynman--Kac identification lemmas are
inserted.  The Jensen step supplies only the denominator and moment
integrability; it is not itself a weak-convergence theorem.

## 6. Adversarial checks

1. **The temporal zero mode makes the covariance bound diverge with `N`.**
   Rejected: the `a*epsilon` term contributes exactly `1/(beta*a)` after the
   `(1/N)` spectral average, and the nonzero modes are controlled by the
   csc-squared identity.
2. **Jensen requires the residual action to be nonnegative.** Rejected:
   Jensen applies to `exp(-s)` whenever `E_gamma|S|` is finite; the Gaussian
   polynomial moments in (3.1)--(3.3) provide that finiteness.
3. **A centered reference cannot handle a linear source.** Rejected for the
   declared convention: the source is in the residual action and its Gaussian
   expectation is exactly zero.  A shifted-reference convention would require
   a new calculation.
4. **The bound is uniform in spatial volume.** Not claimed.  `C_(L,h_0)` is
   allowed to depend on the fixed finite volume; the spatial thermodynamic
   limit remains a separate KP compactness/pressure argument.
5. **The normalizer estimate closes continuous-loop FKG or FSS.** Rejected:
   the interpolation modulus, finite-grid/Feynman--Kac identification,
   reflection-positive transfer and external theorem-hypothesis audits remain
   open.

## 7. Disposition and next gate

The mesh-uniform normalizer lower bound is now available in two independent
forms: the earlier sup-norm event estimate and the Jensen estimate (4.1).
The Jensen form is preferable in the manuscript because it exposes the only
needed inputs—positive temporal harmonic splitting and uniform Gaussian
polynomial moments—without hiding a Brownian-bridge small-ball assertion.
The disposition is **sub-obligation advanced at T0; P-06 and P-09 remain
proof-text assembled pending independent mathematical review**.

The next audit must check that the final finite-grid action uses precisely the
split written in Section 2, that the reference covariance convention matches
the Feynman--Kac normalization, and that the same source interval is used in
the subsequent DLR tangent limit.  Only after those checks and the remaining
P-06/P-09/operator audits pass may the bounded claim and manuscript be
content-frozen.  PDF compilation, rendering and page review remain final-stage
actions after that freeze.

## 8. Explicit nonclaims

This addendum does not assert a strict infrared lower bound, a pressure cusp,
DLR multiplicity, an all-parameter phase theorem, extremality, purity,
clustering, real-time dynamics, KMS states, ground states, a spectral gap, a
continuum limit, a physical vacuum, a cosmological interpretation, C6, CP1,
Sector A or Pre-A closure.  It creates no claim card, P2 manuscript,
submission, upload, tag, release or PDF.
