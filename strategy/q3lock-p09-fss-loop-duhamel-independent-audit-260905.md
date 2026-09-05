# Q3LOCK P-09 FSS-to-loop Duhamel independent audit

**Status:** T0 internal independent audit; P-09 remains open  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Companion proof text:** `strategy/q3lock-p06-p09-independent-proof-audit-round2-260905.md`  
**Primary source:** Froehlich--Simon--Spencer, Commun. Math. Phys. 50 (1976),
79--95, Theorems 2.1--2.3  
**PDF:** deferred until mathematical content freeze and external review

## 1. Question and boundary

This audit independently recomputes the finite-dimensional FSS source bound and
its passage to the fixed-spatial-volume periodic loop covariance.  It checks
the spatial bond expansion, the scaled-spin source, the edge/vertex adjoint,
the Poisson shift, the beta and Fourier factors, and the uniform-integrability
condition needed for the source exponential.  It imports only the finite FSS
theorem under its pinned hypotheses.  It does not claim a continuous-loop
FSS theorem by citation, an infinite-volume infrared lower bound, a cusp, or
DLR multiplicity.

## 2. Spatial finite-grid map

Let `Lambda_L` be the periodic cubic torus with `V=L^3` sites and let
`epsilon=beta/N`.  At each site encode the complete eight-component time
history as

```text
s_y=sqrt(epsilon)*(x_(y,k))_(k=0,...,N-1) in R^(8N).
```

The spatial part of the Euclidean action is

```text
(c/2)*sum_(<yz>)*|s_y-s_z|^2
 = 3*c*sum_y|s_y|^2 - c*sum_(<yz>) s_y dot s_z.
```

The periodic bond set counts each undirected nearest-neighbour pair once and
has six incidences per site.  Thus the interaction between distinct sites is
exactly the FSS ferromagnetic coupling `J=c`; the onsite `3c` term, temporal
kinetic term, scalar quartic and nonradial Q3 polynomial belong to the
single-site prior.  The finite-grid prior has all finite quadratic exponential
moments by quartic coercivity.  No radial or `O(8N)` invariance is required.

## 3. Source scaling and Poisson shift

Let `u=(1,...,1)/sqrt(8)` and let `a:Lambda_L -> R` obey `sum_y a_y=0`.
Define the weighted source and ordinary FSS source by

```text
j_y(k)=t*a_y*u,
eta_y=t*sqrt(epsilon)*(a_y*u)_(k=0,...,N-1).
```

The ordinary Euclidean pairing is

```text
sum_y eta_y dot s_y
 = t*epsilon*sum_(y,k) a_y*(u dot x_(y,k))
 = t*X_(N,L)(a),
X_(N,L)(a)=epsilon*sum_(y,k)a_y*(u dot x_(y,k)).
```

Let `B:E -> V_0` be the FSS edge-to-vertex divergence and `G=B^*` the
signed vertex-to-edge gradient.  On the zero-sum subspace,

```text
L_sp=B*B^*=G^*G,
 h=G*L_sp^(-1)j,
 B*h=j,
 |h|^2=<j,L_sp^(-1)j>.
```

The inverse is defined only on `V_0`; the constant spatial mode is excluded.
With the bond completion square `b=h/c`, FSS Theorem 2.1 with `J=c` gives

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
 <= (1/(2*c))*|j|^2
 = beta*t^2/(2*c)*<a,L_sp^(-1)a>.
```

The equality `|j|^2=beta*t^2*|a|^2` uses `N*epsilon=beta` and `|u|=1`.
No component-count factor is added.

## 4. Variance and Fourier ledger

At finite `N`, quartic confinement makes the source log-MGF finite and
analytic near zero.  Since the zero-source law is parity-even, its first
source derivative vanishes.  Differentiating the quadratic bound twice gives

```text
Var_(N,L,0)(X_(N,L)(a))
 <= beta/c*<a,L_sp^(-1)a>.
```

Define the scalar Duhamel matrix by

```text
Var(X_(N,L)(a))=beta^2*<a,D_(N,L)a>.
```

Then

```text
<a,D_(N,L)a> <= 1/(beta*c)*<a,L_sp^(-1)a>.
```

For a nonzero spatial Fourier mode, the positive cubic graph Laplacian has

a eigenvalue

```text
ell(p)=2*E(p),
E(p)=sum_j(1-cos(p_j)).
```

Therefore

```text
Dhat_(N,L)(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

The factor two is the graph eigenvalue and the single beta is the conversion
from the integrated variance to the averaged Duhamel matrix.  The estimate is
not a bound on `p=0`.

## 5. Time-grid to periodic loop passage

The periodic piecewise-linear interpolation satisfies the exact identity

```text
integral_0^beta (u,I_N x_y)(tau)d tau
 = epsilon*sum_k (u,x_(y,k)).
```

Thus the source observable has no discretization error.  To pass the source
log-MGF and its second derivative through the mesh limit, weak convergence of
bounded continuous functionals is insufficient.  The required additional
inputs are:

1. fixed-volume Gaussian interpolation tightness in periodic sup norm;
2. compact residual Riemann-sum convergence after the massive Gaussian split;
3. a mesh-uniform positive normalizer lower bound; and
4. a quartic Holder--Young estimate giving uniform integrability of
   `exp(T*|X_(N,L)(a)|)` and
   `|X_(N,L)(a)|^2*exp(T*|X_(N,L)(a)|)`.

Under exactly these fixed-volume inputs,

```text
E_(N,L,0) exp[t*X_(N,L)(a)] -> E_(L,0) exp[t*X_L(a)],
Var_(N,L,0)(X_(N,L)(a)) -> Var_(L,0)(X_L(a)),
```

and the finite FSS inequality passes to the continuous periodic loop law.
This is a conditional analytic passage, not an assertion that the FSS paper
already contains the Q3LOCK time-grid limit.

## 6. Duhamel conversion and source scope

For the exact loop law define

```text
C_(yz)(tau)=Cov((u,omega_y(tau)),(u,omega_z(0))),
D_L=(1/beta)*integral_0^beta C(tau)d tau.
```

Time translation and periodicity give

```text
Var(X_L(a))=beta^2*<a,D_L a>.
```

Consequently the fixed-volume loop inequality is

```text
<a,D_L a> <= 1/(beta*c)*<a,L_sp^(-1)a>,
Dhat_L(p) <= 1/(2*beta*c*E(p)), p != 0.
```

The source is the unit collective projection `u`; the Q3LOCK prior remains
nonradial.  The FSS theorem's component-independent constant does not license
the KKK rotation-invariant corollary.  The pressure source dictionary and the
KKK integrated covariance are separate conversions recorded in the companion
source audits.

## 7. Hypothesis ledger

| FSS-to-loop link | Required input | Disposition |
|---|---|---|
| spatial FSS coupling | periodic bond expansion and `c>0` | exact under declared periodic edge set |
| single-site prior | finite quadratic exponential moments | conditional on quartic coercivity |
| source pairing | ordinary source `sqrt(epsilon)*a*u` | exact |
| Poisson inverse | zero-sum `a` and `L_sp` on `V_0` | exact; zero mode excluded |
| finite variance | analytic finite log-MGF | exact at fixed mesh |
| loop exponential passage | Gaussian/residual convergence and source UI | conditional; independent audit remains required |
| Duhamel covariance | time translation and periodicity | conditional on exact loop identification |
| spatial thermodynamic limit | volume-uniform bound and declared pressure sequence | not supplied here |

## 8. Adversarial checks

| Objection | Disposition |
|---|---|
| The coupling is `2c` because six neighbours occur at each site | **UPHELD AS FALSE:** each undirected bond is counted once and the cross coefficient is `-c`. |
| The ordinary FSS source is `t*a*u` | **UPHELD AS FALSE:** the scaled-spin isometry requires `t*sqrt(epsilon)*a*u`. |
| The component count contributes an extra factor eight | **UPHELD AS FALSE:** `u` is unit norm and the full history is one `R^(8N)` spin. |
| The Poisson inverse can be applied to the constant mode | **UPHELD AS FALSE:** the source is restricted to `V_0`. |
| Weak convergence alone passes the source exponential | **UPHELD AS FALSE:** source-uniform quartic UI and a normalizer bound are load-bearing. |
| The finite FSS bound is already a thermodynamic or DLR theorem | **UPHELD AS FALSE:** mesh, volume, pressure and DLR steps are separate. |
| The result proves a strict cusp | **UPHELD AS FALSE:** a positive zero-mode lower bound and KKK endpoint argument are still needed. |

## 9. Disposition and next gate

The finite FSS source map, Poisson shift, variance conversion and Fourier
constant are internally consistent.  The continuous-loop statement follows
only conditionally on the fixed-volume Gaussian/residual and source-UI
inputs, and the spatial thermodynamic step remains outside this audit.  This
is an **advanced T0 internal audit**, not an external mathematical
certification.  The next gate is line-by-line review of the pinned FSS theorem,
the KP loop identification, the source-UI estimates and the volume-uniform
extension.

## 10. Explicit nonclaims

No positive infrared zero mode, strict source cusp, phase coexistence, DLR
multiplicity, extremality, purity, clustering, KMS state, real-time dynamics,
ground-state phase, spectral gap, continuum limit, physical vacuum,
cosmological interpretation, Sector A, CP1, C6, Pre-A, or Yang--Mills result
is asserted.  No claim card, manuscript release, submission package, or PDF
is created.
