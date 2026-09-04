# Q3LOCK P-09 constant-source loop-limit and Duhamel normalization audit

**Status:** T0 proof-text audit; P-09 remains open pending independent review  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary sources:** Froehlich--Simon--Spencer, [source PDF](https://math.caltech.edu/SimonPapers/65.pdf); Kozitsky--Pasurek, [arXiv:math-ph/0609045](https://arxiv.org/pdf/math-ph/0609045)  
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Purpose and boundary

The finite-grid FSS estimate is useful for Q3LOCK only after its source
observable is identified exactly with a continuous-loop integral and after
the unbounded exponential moment is passed through the grid limit.  This note
isolates those two points and fixes the Duhamel normalization.  It is a
paper-local analytic audit, not a new theorem registration.

The order of operations is fixed:

1. finite time mesh at fixed periodic spatial box `Lambda`, inverse
   temperature `beta`, and source parameter;
2. time-grid limit to the finite-volume periodic loop law;
3. only afterwards, spatial thermodynamic and source-tangent limits.

No spatial infinite-volume infrared conclusion, strict cusp, or DLR
multiplicity is obtained here.  In particular, the FSS source paper's remark
about periodic spatial limits is not used as a substitute for the Q3LOCK
grid-to-loop argument.

## 2. Exact source identity for periodic piecewise-linear interpolation

Let `epsilon=beta/N` and let `x_(y,k)` be the periodic grid variable at site
`y` and slice `k`, with `x_(y,N)=x_(y,0)`.  Let `I_N x` be the periodic
piecewise-linear interpolation.  For a spatially zero-sum coefficient
`a:Lambda -> R`, and `u=(1,...,1)/sqrt(8)`, define

```text
X_(N,L)(a) = epsilon*sum_(y,k) a_y*(u dot x_(y,k)).
```

On one time interval, the integral of the interpolation is

```text
integral_(k*epsilon)^((k+1)*epsilon) I_N x_y(tau) d tau
  = epsilon/2 * (x_(y,k)+x_(y,k+1)).
```

Summing over the cyclic index gives the exact telescoping identity

```text
sum_k epsilon/2*(x_(y,k)+x_(y,k+1)) = epsilon*sum_k x_(y,k).
```

Consequently, with

```text
X_L(a)(omega) = sum_y a_y*integral_0^beta
                  (u dot omega_y(tau)) d tau,
```

one has `X_L(a)(I_N x)=X_(N,L)(a)` for every grid configuration, not merely
an asymptotic Riemann-sum approximation.  Since `X_L(a)` is a continuous
linear functional in the periodic sup-norm topology, this identity removes a
possible source-observable seam in the weak-limit passage.

## 3. Finite-grid FSS inequality with the corrected source coordinates

Use the weighted inner product

```text
<v,w>_N = epsilon*sum_(y,k) v_(y,k) dot w_(y,k).
```

The time-constant source vector is `j_y(k)=a_y*u`, so
`<j,x>_N=X_(N,L)(a)`.  Equivalently, in the ordinary Euclidean encoding
`s_y=sqrt(epsilon)*(x_(y,k))_k in R^(8N)`, the source entries are
`sqrt(epsilon)*a_y*u` at every slice.  The latter factor is required by the
isometry and is not optional.

Let `G:V_0 -> E` be the signed spatial gradient and let
`B_FSS=G^*` be the FSS edge-to-vertex divergence.  The positive vertex
Laplacian is

```text
L_sp=G^*G=B_FSS B_FSS^* on V_0.
```

Because `sum_y a_y=0`, the zero-sum Poisson solution is well-defined.  The
time-constant minimum-norm edge field is

```text
h=G L_sp^(-1)j=B_FSS^*L_sp^(-1)j.
```

It obeys `c*(G x,h)_N=<j,x>_N` and
`(c/2)||h||_N^2=(1/(2c))<j,L_sp^(-1)j>_N`.  The positive-definite crossing
kernel in the finite-dimensional FSS transfer theorem therefore gives

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
  <= beta*t^2/(2*c) * <a,L_sp^(-1)a>.
```

Here `sum_k epsilon=beta`; no additional time-grid factor is hidden.  The
finite-grid source is analytic at zero, and differentiation gives

```text
Var_(N,L,0)(X_(N,L)(a))
  <= beta/c * <a,L_sp^(-1)a>.
```

The graph eigenvalue for a Fourier mode `p` is
`ell(p)=2*E(p)`, where `E(p)=sum_i(1-cos(p_i))`.  Thus, with the Duhamel
normalization fixed below,

```text
Dhat_(N,L)(p) <= 1/(2*beta*c*E(p)),   p != 0.
```

## 4. Source-uniform integrability: the missing limit hypothesis

Let the zero-source residual local potential after the positive harmonic
split satisfy, uniformly on a compact source interval,

```text
V_(h,a)(q) >= A*|q|^4-C,     A>0.
```

Put `S_N=epsilon*sum_(y,k)|x_(y,k)|^4`.  Holder's inequality gives the
explicit mesh-independent constant

```text
K_src = (beta*sum_y |a_y|^(4/3))^(3/4)
```

(using `|u|=1`) such that

```text
|X_(N,L)(a)| <= K_src*S_N^(1/4).
```

Young's inequality then implies, for every fixed `T` and every sufficiently
small `delta>0`,

```text
T*|X_(N,L)(a)| <= delta*S_N + C_(T,delta),
|X_(N,L)(a)|^2*exp(T*|X_(N,L)(a)|)
  <= C'_(T,delta)*exp(2*delta*S_N).
```

Choosing `delta` so that `2*delta<A` leaves a quartically decaying factor
after multiplication by the Gibbs weight.  The spatial difference factor is
at most one.  The fixed-volume normalizer lower bound from the Q3LOCK
weighted-law audit is uniform in `N` and in the compact source interval.
Therefore the families

```text
{ exp(t*X_(N,L)(a)) : |t|<=T }
and
{ |X_(N,L)(a)|^2*exp(T*|X_(N,L)(a)|) }
```

are uniformly integrable under the normalized zero-source grid laws.  The
same estimate applies to the source-perturbed weights used to identify the
moment-generating function.  This is the required tail input; weak
convergence of bounded continuous functionals alone would not justify either
the exponential moment or its second derivative.

## 5. Passing the FSS moment inequality to the exact loop law

The Gaussian interpolation tightness and covariance convergence, the
uniform-on-compact Riemann-sum argument, and the normalizer bounds give

```text
I_N#(R_(N,h)*G_(a,N)/E R_(N,h))
  => R_h*G_a/E_(G_a)R_h
```

for each fixed finite `Lambda` and compact source interval.  The exact source
identity in Section 2 and the uniform-integrability estimate in Section 4
upgrade this to

```text
E_(N,L,0) exp[t*X_(N,L)(a)] -> E_(L,0) exp[t*X_L(a)],
Var_(N,L,0)(X_(N,L)(a)) -> Var_(L,0)(X_L(a)).
```

The KP finite-volume Feynman--Kac representation identifies the limiting law
on the right with the Q3LOCK periodic Euclidean Gibbs law after the explicit
potential and pair-normalization crosswalk.  Taking the limit in the finite
FSS inequality gives

```text
log E_(L,0) exp[t*X_L(a)]
  <= beta*t^2/(2*c) * <a,L_sp^(-1)a>.
```

The conclusion is a fixed-spatial-volume continuous-loop Gaussian-domination
bound.  It is not a path-space FSS theorem proved by citation; the grid,
topology and integrability passage are Q3LOCK-local.

## 6. Duhamel covariance and the factor ledger

Let `C_(yz)(tau)` denote the connected, time-translation-invariant loop
correlation of `(u,omega_y(tau))` and `(u,omega_z(0))` in the finite-volume
zero-source law.  Define

```text
D_L(y,z) = (1/beta)*integral_0^beta C_(yz)(tau) d tau.
```

Time-translation invariance and periodicity give

```text
Var(X_L(a))
 = sum_(y,z) a_y*a_z*integral_0^beta integral_0^beta
     C_(yz)(tau-sigma) d tau d sigma
 = beta^2 * <a,D_L a>.
```

Combining this identity with the loop FSS inequality yields

```text
<a,D_L a> <= 1/(beta*c) * <a,L_sp^(-1)a>.
```

For `p != 0`, `L_sp` has eigenvalue `2*E(p)`, so

```text
Dhat_L(p) <= 1/(2*beta*c*E(p)).
```

The single `beta` comes from the two time integrations divided by the
declared `D_L` normalization; the factor two comes only from the spatial
Laplacian eigenvalue.  The constant spatial mode is excluded by the
zero-sum source and is not inverted.

## 7. Adversarial checks

1. **The interpolation introduces an `O(epsilon)` source error.**  False:
   cyclic piecewise-linear integration gives the exact identity in Section 2.
2. **The ordinary source vector can be written without `sqrt(epsilon)`.**
   False: that is correct only in the weighted inner product; ordinary
   `R^(8N)` coordinates require the isometric factor.
3. **Weak convergence proves exponential-moment convergence.**  False:
   the quartic Young estimate and a uniform normalizer lower bound are used.
4. **The FSS constant supplies a uniform quartic moment bound.**  False:
   its independence from the prior and component count is a domination
   constant, not the Q3LOCK source-uniform integrability estimate.
5. **The loop inequality controls `p=0`.**  False: the Poisson inverse is
   defined only on the spatial zero-sum subspace.
6. **The FSS infinite-volume remark closes the Q3LOCK limit order.**  False:
   the time-grid limit at fixed `Lambda`, the pressure limit and the source
   tangent remain separate operations.
7. **A finite-grid variance bound alone proves a strict cusp.**  False: the
   infrared estimate is only one input to the later collective lower-bound,
   Griffiths and source-tangent composition.

## 8. Remaining independent-audit obligations

* Recheck the cyclic interpolation identity and the declared loop topology
  against the exact KP finite-volume construction.
* Reproduce the Holder/Young constants, including their independence of the
  time-grid size and compatibility with the shifted FSS weight.
* Verify the finite-grid-to-loop convergence of the second derivative with
  the connected-correlation convention used in the manuscript.
* Check the periodic spatial edge multiset and the corrected `3c` onsite
  allocation in every finite volume used before the pressure limit; use the
  site-dependent `(c/2)d_R(y)` diagonal for open boxes (EXP-001512).
* Have an independent reviewer audit the source theorem version, all
  `epsilon`/`beta` factors and the order of limits.

P-09 therefore remains **PAPER-LOCAL PROOF AND EXTERNAL AUDIT REQUIRED**.
P-06/P-12, claim registration, manuscript release and PDF generation remain
deferred until those audits and the final content freeze are complete.

## 9. Nonclaims and publication boundary

This audit does not assert a positive infrared zero mode, strict pressure
cusp, phase coexistence, DLR multiplicity, extremality, purity, clustering,
real-time dynamics, KMS state, ground state, mass gap, continuum limit,
physical vacuum, cosmological interpretation, Sector-A conclusion or Pre-A
closure.  It creates no claim card, P2 manuscript or release package.  PDF
compilation, rendering and visual review are explicitly reserved for the
final stage after mathematical content and independent audits are complete.
