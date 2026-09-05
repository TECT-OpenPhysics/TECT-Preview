# Q3LOCK P-06 quantitative Gaussian weak-limit and weighted-transfer audit

**Status:** T0 internal analytic audit; external mathematical review required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source crosswalk:** Kozitsky--Pasurek,
arXiv:math-ph/0609045v1, equations (2.18)--(2.31), Assumptions (A)--(B),
Lemma 2.11, and Theorems 3.1--3.3  
**PDF:** deferred until mathematical content freeze and external review

## 1. Question and boundary

R-500 checked the finite Fourier, cyclic-resistance and interpolation
normalizations used in P-06, but deliberately left the Gaussian weak limit as
an analytic obligation.  This note supplies a quantitative fixed-spatial-volume
proof.  It also states the bounded-weight transfer lemma needed to pass from
the Gaussian reference to the exact finite-volume Q3LOCK loop law.

The result is local in spatial volume.  It does not identify finite-product
sup-norm convergence with the global KP `W_t` topology.  It does not prove the
spatial thermodynamic limit, continuous-loop FKG by itself, the FSS infrared
bound, a pressure cusp, DLR multiplicity, or publication readiness.  The
companion verifier is regression evidence and not an external proof.

## 2. Frozen Gaussian convention

Fix `beta,m,a>0`, an even `N>=4`, `epsilon=beta/N`, and the representative set

```text
I_N={-N/2+1,...,N/2}.
```

For one scalar coordinate, the centered cyclic Gaussian has action

```text
S_G,N(x)=(1/2) sum_k [(m/epsilon)(x_(k+1)-x_k)^2
                       +a*epsilon*x_k^2].
```

After the unitary Fourier transform its vertex covariance is

```text
G_N(r)=(1/beta) sum_(n in I_N)
 exp(2*pi*i*n*r/N)/D_N(n),
D_N(n)=a+(4m/epsilon^2)sin^2(pi*n/N).
```

The proposed continuum covariance is

```text
G(t)=(1/beta) sum_(n in Z)
 exp(2*pi*i*n*t/beta)/D(n),
D(n)=a+4*pi^2*m*n^2/beta^2.
```

The coefficients are positive and summable.  Thus `G` is a continuous
positive-definite function and defines a centered periodic Gaussian process.
Its diagonal obeys

```text
G(0)<=K,       K=1/(beta*a)+beta/(12m).
```

## 3. Quantitative covariance convergence on the grid

For `0<|n|<=N/2`, put `x=pi*|n|/N`.  The elementary estimates

```text
sin(x)>=2x/pi=2|n|/N,
0<=x^2-sin^2(x)<=x^4/3
```

give

```text
0<=1/D_N(n)-1/D(n)<=pi^2*beta^2/(48m*N^2).
```

There are `N-1` nonzero retained modes.  The omitted continuum modes satisfy

```text
sum_(n notin I_N) 1/n^2 <= 6/N.
```

The latter follows by comparing the two one-sided decreasing tails with their
integrals and retaining the single missing negative Nyquist mode.  Therefore,
uniformly in every grid separation `r`,

```text
|G_N(r)-G(epsilon*r)|
 <= beta/(m*N)*(pi^2/48+3/(2*pi^2))=:B_N.       (3.1)
```

This is an analytic error bound, not a fitted convergence threshold.  The
verifier recomputes both elementary inequalities, the missing-mode tail and
(3.1) on multiple parameter triples and meshes.

## 4. Polygonal covariance and finite-dimensional convergence

Let `I_N x` be periodic piecewise-linear interpolation.  Its covariance at
two arbitrary times is a convex combination of four vertex covariances.  Each
corresponding vertex-time difference is within `2*epsilon` on the time circle
of the desired difference.

The continuum massless comparison gives

```text
E|X(t)-X(s)|^2<=d_beta(t,s)/m,
```

where `d_beta` is circle distance.  Cauchy--Schwarz and the diagonal bound then
give

```text
|G(t)-G(s)|<=sqrt(K*d_beta(t,s)/m).
```

Combining this modulus with (3.1) yields the uniform interpolated covariance
bound

```text
sup_(t,s) |Cov(I_N X(t),I_N X(s))-G(t-s)|
 <= B_N+sqrt(2*K*beta/(m*N)).                    (4.1)
```

Hence the right side is `O(N^(-1/2))`.  Every finite vector of evaluations is
centered Gaussian, so convergence of its covariance matrix proves
finite-dimensional convergence to the Gaussian process with covariance `G`.

## 5. Uniform tightness in the periodic sup-norm topology

The cyclic resistance estimate gives vertex increments

```text
E|x_k-x_l|^2<=epsilon*r/(m),
```

with `r` the shortest cyclic separation.  For arbitrary `t,s`, if
`d_beta(t,s)<=epsilon`, interpolation crosses at most two partial mesh edges
and gives variance at most `d_beta(t,s)/m`.  If
`d_beta(t,s)>epsilon`, insert the two neighboring vertices and use the
`L^2` triangle inequality.  Since the vertex separation is at most
`d_beta(t,s)+2epsilon`,

```text
E|I_N X(t)-I_N X(s)|^2
 <=(2+sqrt(3))^2*d_beta(t,s)/m
 <14*d_beta(t,s)/m.                              (5.1)
```

For a scalar Gaussian increment, its fourth moment is three times the square
of its variance.  For the finite product of `q=8*|Lambda|` independent
coordinates,

```text
E||I_N X(t)-I_N X(s)||^4
 <=q*(q+2)*14^2*d_beta(t,s)^2/m^2.               (5.2)
```

Kolmogorov's criterion on the circle gives tightness in
`C_per(S_beta;R^q)`.  Together with Section 4 and uniqueness of the centered
Gaussian finite-dimensional distributions, this proves

```text
(I_N)_# gamma_(N,L) ==> gamma_(a,L)
```

in the finite-volume periodic sup-norm topology.  KP v1 uses precisely
`C_beta=C(S_beta;R^nu)` with the sup norm as its single-spin space.  Its
infinite-volume `Omega_t`/`W_t` topology additionally contains weighted
sitewise `L^2_beta` control and is not inferred here.

## 6. Bounded residual-weight transfer

Let `nu_N=(I_N)_#gamma_(N,L)` and `nu=gamma_(a,L)`.  Suppose the residual
weights satisfy

```text
w_N(I_N x)=exp(-R_N(x)),       w(omega)=exp(-R(omega)),
0<=w_N,w<=M,
sup_(I_N x in K)|R_N(x)-R(I_N x)| -> 0
```

for every compact set `K` in the finite-product sup-norm loop space.  For a
bounded continuous `F`, tightness chooses one compact `K` carrying all but an
arbitrarily small common probability tail.  Uniform convergence controls
`F(w_N-w)` on `K`; boundedness controls its complement; and ordinary weak
convergence applies to the bounded continuous function `F*w`.  Therefore

```text
int F*w_N dnu_N -> int F*w dnu.                  (6.1)
```

Taking `F=1` gives convergence of normalizers.  Since `w>0` pointwise on the
continuous loop space, the limiting normalizer is positive, and division in
(6.1) proves weak convergence of the normalized Q3LOCK finite-volume loop
laws.

For the Q3LOCK residual, the quartic lower bound gives `w_N<=exp(C)` uniformly
in the mesh, while local and spatial polynomial Riemann sums converge
uniformly on compact equicontinuous loop sets.  The temporal kinetic action is
not treated as a Riemann sum; it is entirely contained in the Gaussian
reference.

## 7. Source uniform integrability

For the zero-sum spatial source observable

```text
X_N=epsilon*sum_(y,k) a_y*(u,x_(y,k)),
```

weighted Holder gives

```text
|X_N|<=K_src*Q_N^(1/4),
K_src=(beta*sum_y |a_y|^(4/3))^(3/4),
Q_N=epsilon*sum_(y,k)|x_(y,k)|^4.
```

For `b>0`, `delta>0`, direct maximization of `b*z-delta*z^4` gives

```text
b*z<=delta*z^4+C_Y(b,delta),
C_Y(b,delta)=3*b^(4/3)/(4*(4*delta)^(1/3)).       (7.1)
```

If `R_N>=alpha*Q_N-C` and the normalizers have a positive mesh-uniform lower
bound, apply (7.1) with `b=p*T*K_src` and `delta<alpha`.  This yields an
`L^p`, `p>1`, bound for `exp(T|X_N|)`.  A slightly larger exponential absorbs
the polynomial factor in `X_N^2 exp(T|X_N|)`.  Both source families are
therefore uniformly integrable, so their first two source witnesses may be
passed after truncation.  Weak convergence alone is not used for these
unbounded quantities.

## 8. Source-level topology crosswalk

The hash-frozen KP v1 source makes the following distinctions explicit:

| source item | exact role here | boundary |
|---|---|---|
| equations (2.18)--(2.21) | periodic loop space `C_beta`, sup norm, product Polish topology | matches the fixed-volume topology in Sections 4--6 |
| equations (2.22)--(2.31) | massive periodic OU reference and finite-volume Feynman--Kac density | matches the harmonic split after parameter crosswalk |
| equations (2.47)--(2.49) | weighted `Omega_alpha` and projective `Omega_t` | spatial accumulation only; not proved by the time-mesh limit |
| Lemma 2.11 and Theorem 3.1 | DLR closure and `W_t` compactness under KP hypotheses | fixed-source infinite-volume input, not a P-06 consequence |
| Theorems 3.2--3.3 | exponential moment and tempered support | do not supply the nonradial vector FKG theorem |

The Q3LOCK potential is a continuous polynomial with `V(0)=0`, the quartic
audit supplies KP exponent `r_KP=2`, and the nearest-neighbor interaction has
`Jhat_0=6c`.  This audit does not import KP's scalar order propositions.

## 9. Adversarial review

1. **Dominated convergence gives total-variation convergence.** Rejected:
   polygonal paths and the nondegenerate OU loop law are mutually singular at
   every finite mesh.  Only weak convergence is proved.
2. **Pointwise Fourier convergence is enough.** Rejected: the retained-mode
   error and omitted-mode tail are bounded uniformly in the time separation.
3. **Grid-time convergence automatically controls interpolation.** Rejected:
   the continuum covariance modulus produces the explicit square-root term in
   (4.1).
4. **Vertex increments alone prove tightness.** Rejected: (5.1) separately
   treats same/adjacent cells and separated cells at arbitrary times.
5. **The finite-product sup-norm topology is KP `W_t`.** Rejected: the latter
   is a spatial projective-limit topology with weighted `L^2_beta` control.
6. **Weak convergence passes source exponentials.** Rejected: the `L^p`
   estimate from (7.1) and the normalizer lower bound are load-bearing.
7. **This internal proof closes P-06 or authorizes a PDF.** Rejected: the
   exact residual split, KP parameter map, spatial accumulation, external
   mathematical review, claim registration and content freeze remain open.

## 10. Disposition and next gate

**Advanced at T0:** the Gaussian reference weak limit is no longer supported
only by finite refinement.  Equations (3.1)--(5.2) provide a quantitative
analytic covariance and tightness proof, and Section 6 gives the exact bounded
weighted-transfer lemma.  The verifier checks all displayed finite constants,
hostile weakened inequalities, interpolation probes and deterministic replay.

**Still open:** external line-by-line acceptance of the analytic inequalities;
verification that the final Q3LOCK residual uses the identical harmonic split;
the spatial `W_t` accumulation; the P-09/FSS and operator audits; pressure,
Griffiths, cusp and source-tangent composition; bounded claim registration;
clean-snapshot replay; content freeze; and external referee review.

No strict cusp, phase coexistence, DLR multiplicity, extremality, purity,
clustering, real-time dynamics, KMS state, ground-state phase, spectral gap,
continuum limit, physical vacuum, cosmological interpretation, C6, CP1,
Sector A, Pre-A, Yang--Mills or mass-gap conclusion is asserted.  No P2
manuscript, submission, upload, release, tag or PDF is created.

## 11. Reproduction

```text
python -X utf8 verification/scripts/q3lock_p06_gaussian_weak_limit_quantitative_audit.py
```

Expected prefix:

```text
EXP-001586 PASS
```
