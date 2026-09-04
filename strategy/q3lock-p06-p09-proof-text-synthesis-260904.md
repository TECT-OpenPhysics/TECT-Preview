# Q3LOCK P-06/P-09 proof-text synthesis

**Status:** T0 research synthesis; manuscript-transcription candidate, not a
claim card  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 only  
**Proof-text status:** not independently audited  
**PDF:** deferred

## 1. Fixed model and topology

Fix a finite spatial box `Lambda`, inverse temperature `beta>0`, a compact
source interval `|h|<=h0`, and `m=chi/hbar^2>0`.  The Euclidean path space is

```text
X_Lambda = C_per([0,beta]; R^8)^Lambda
```

with the periodic sup norm.  Choose an arbitrary positive harmonic split
`a>0` in the onsite quadratic part.  The residual local potential `V_(h,a)`
is continuous and, uniformly in `|h|<=h0`, obeys

```text
V_(h,a)(q) >= A|q|^4-C,     A>0.
```

The spatial interaction is the nearest-neighbour factor

```text
exp[-c/2 integral_0^beta sum_<yz>
                 |omega_y(tau)-omega_z(tau)|^2 d tau].
```

All statements in this synthesis take the time-grid limit at fixed
`Lambda`; no spatial-volume or spatial-continuum limit is hidden in P-06 or
P-09.

## 2. Lemma A: periodic Gaussian grid limit

For `epsilon=beta/N`, let `G_(a,N)` be the product Gaussian with action

```text
m/(2*epsilon) sum_(y,k)|x_(y,k+1)-x_(y,k)|^2
 + a*epsilon/2 sum_(y,k)|x_(y,k)|^2.
```

Its cyclic one-component precision has eigenvalues

```text
kappa_(N,l)=a*epsilon+(2*m/epsilon)(1-cos(2*pi*l/N)).
```

The finite-grid increment variance satisfies the exact resistance estimate

```text
E|x_(k+r)-x_k|^2
 <= (epsilon/m) r(N-r)/N <= (epsilon/m)r,
```

because

```text
(1/N) sum_(l=1)^(N-1)
 (1-cos(2*pi*l*r/N))/(1-cos(2*pi*l/N))=r(N-r)/N.
```

Periodic piecewise-linear interpolation then gives

```text
E||I_Nx(t)-I_Nx(s)||^2 <= C_(m,Lambda) d_circle(t,s).
```

Centered Gaussian moment comparison and any `p>2` yield a uniform
`d_circle(t,s)^(p/2)` bound.  Kolmogorov therefore gives tightness in
`X_Lambda`.  The exact interpolation shape factor is contractive, and the
Fourier covariance tail obeys the summable bound

```text
1/(N*kappa_(N,l)) <= beta/(16*m*rho^2),
rho=min(|l|,N-|l|), rho>=1.
```

Dominated convergence of the Fourier sum gives the periodic Green kernel of
`-m*d^2/dtau^2+a`; combining finite-dimensional convergence with tightness
proves `I_N#G_(a,N) => G_a`.

The complete derivation is recorded in
`q3lock-gaussian-increment-estimate-audit-260904.md` and
`q3lock-covariance-tail-dominated-convergence-260904.md`.

## 3. Lemma B: weighted grid laws and the Feynman--Kac identification

Let `R_(N,h)` be the local and spatial grid weight.  The quartic lower bound
gives the global estimate

```text
0 < R_(N,h) <= exp(beta*|Lambda|*C).
```

The positive lower bound for the normalizer is obtained separately on a
sup-norm event: choose `R` so that the Gaussian interpolation has probability
at least `1/2` of lying in the sup-norm ball, bound the local potential there by
`M_R`, and bound each spatial difference by `K_R`.  Thus

```text
E_(G_(a,N)) R_(N,h)
 >= (1/2) exp[-beta*|Lambda|*M_R-beta*c*E(Lambda)*K_R^2/2].
```

The normalizer event does **not** supply uniform Riemann-sum convergence.  For
that step choose a compact set `K` from Gaussian tightness.  Arzela--Ascoli
gives common boundedness and equicontinuity on `K`, so both the local and
spatial Riemann sums in `R_(N,h)` converge uniformly on `K` to the continuous
loop weight `R_h`.  The global weight upper bound controls the complement of
`K`.  Tightness, uniform-on-compact convergence, and the two-sided normalizer
bounds imply

```text
I_N#(R_(N,h)G_(a,N)/E R_(N,h))
   => R_h G_a/E_(G_a)R_h.
```

The finite-volume operator-to-loop statement is now source-mapped to the
Kozitsky--Pasurek periodic Ornstein--Uhlenbeck/Feynman--Kac construction; the
exact Q3LOCK sign, edge-count and potential-hypothesis crosswalk is recorded
in `q3lock-feynman-kac-finite-volume-crosswalk-260904.md`.  The manuscript must
still state the exact cited theorem and check its form-domain hypotheses.  The
grid argument above is not a substitute for that citation, and the final
bibliography-version and independent source audit remain open.

## 4. Lemma C: association in the continuous-loop law (P-06)

At finite `N`, the cyclic Gaussian precision is an M-matrix.  The spatial
bond contributes a nonnegative mixed log derivative.  For each Q3 edge,

```text
-epsilon*d^2/dxdy [(lambda/4)(x-y)^2(x^2+y^2)]
 = (epsilon*lambda/4)[(x+y)^2+5(x-y)^2] >= 0.
```

Linear sources and diagonal quadratic terms do not alter mixed derivatives.
Finite-dimensional FKG therefore gives association of every grid law.

Let `F,G` be bounded continuous pointwise-increasing functionals on
`X_Lambda`.  Their compositions with `I_N` are increasing in the grid
coordinates.  Lemmas A and B permit passage to the weak limit, and boundedness
gives

```text
E_h[FG] >= E_h[F]E_h[G].
```

For coordinate products, first use bounded increasing clips and then remove
the clips with the uniform quartic second-moment bound.  This proves the
association needed for the collective Q3 projection.  It does not assert
path-space MTP2, total-variation convergence, or an infinite-dimensional
FKG theorem.

## 5. Lemma D: Hilbert-valued FSS transfer (P-09)

At fixed `N`, collect the eight components and time slices at one site into
one spin in `R^(8N)` with weighted inner product
`<a,b>_N=epsilon sum_k a_k dot b_k`.  Equivalently set
`s_y=sqrt(epsilon)*(x_(y,k))_k` and use the ordinary Euclidean dot product.
The onsite measure has all quadratic exponential moments because the quartic
local term dominates every quadratic form at fixed `N`.

For an oriented spatial edge, the crossing kernel is

```text
exp[-c||a-b||^2/2]
 = exp[-c||a||^2/2] exp[-c||b||^2/2] exp[c<a,b>].
```

The final factor is positive definite by its nonnegative symmetric-tensor
series, so the finite-dimensional FSS Gaussian-domination theorem applies
without an O(8) invariance assumption.  The source paper's constant is
independent of the single-spin distribution, component count and internal
symmetry; the time-grid dimension is therefore allowed to vary after the
finite-grid inequality is established.

For the only load-bearing source, `j_y(tau)=t a_y u` with `sum_y a_y=0`, set
`b=(1/c)D L_sp^(-1)j`.  It is constant in time and is represented exactly on
every mesh.  In the ordinary `s` coordinates the corresponding source vector
has entries `t*sqrt(epsilon)*a_y*u` at every time slice; this is the factor
that makes its Euclidean pairing equal to the time-integrated observable.
The shifted factor obeys

```text
exp[-c||D omega-b||^2/2]
 <= exp[c||b||^2/2] exp[-c||D omega||^2/4].
```

The quartic bound and Lemma B pass the shifted and unshifted partition
functions to the loop limit.  Expanding the square gives

```text
log E_0 exp(<j,omega>)
 <= (1/(2c))<j,L_sp^(-1)j>.
```

With `D=(1/beta) integral_0^beta C(tau)d tau`, the time-constant source has
second derivative `beta^2 a^T D_L a` on the left and
`(beta/c)a^T L_sp^(-1)a` on the right.  Since the spatial Laplacian eigenvalue
is `2E(p)`,

```text
Dhat_L(p) <= 1/(2*beta*c*E(p)),  p!=0.
```

KKK's rotation-invariant vector corollary is not used.  The finite-grid FSS
inequality, the shifted-source limit and the differentiation-at-zero step
must all appear explicitly in the manuscript.  The exact `8N` spin scaling,
`beta` and factor-two ledger, and the uniform-integrability passage for the
unbounded source exponential are audited in
`q3lock-fss-source-differentiation-audit-260904.md`.

## 6. Gate ledger after synthesis

| Obligation | Current status | Required before claim registration |
|---|---|---|
| Gaussian increment/tightness | explicit T0 derivation (EXP-001488) | independent Fourier/interpolation audit |
| Fourier covariance tail | explicit T0 derivation (EXP-001489) | seam and `1/beta` normalization check |
| Normalizer lower bound | explicit T0 derivation (EXP-001484) | check common source compact and spatial edge count |
| Weighted Riemann sums | corrected compact-set formulation (EXP-001490) | tightness-to-weighted-law audit |
| Finite-grid FKG | finite-dimensional theorem plus derivative calculation (EXP-001500) | independent MTP2/association check |
| Loop association | weak-limit bounded-continuous route (EXP-001500) | verify clip/uniform-integrability passage |
| FSS finite-grid transfer | Hilbert-valued tensor-kernel route (EXP-001485), source-differentiation audit (EXP-001499) | source moment and dimension-uniformity audit |
| Shifted constant-source limit | explicit majorant and Poisson field | source units and differentiation audit |
| Feynman--Kac/Trotter identification | cited as standard but not yet fixed | exact theorem and form-domain audit |

P-06 and P-09 remain `PROOF TEXT AND EXTERNAL AUDIT REQUIRED`.  The
source-scope and normalization audits do not promote them to a registered
independent result.

## 7. Nonclaims and publication boundary

This synthesis does not claim a strict source cusp, a positive infrared zero
mode, DLR multiplicity, extremality, purity, clustering, a common real-time
dynamics, a ground-state phase or gap, a continuum limit, or any physical or
cosmological interpretation.  It does not create a claim card, P2 manuscript,
submission package, release commit, or PDF.  PDF generation and visual review
are reserved for the final stage after mathematical content and independent
audits are complete.
