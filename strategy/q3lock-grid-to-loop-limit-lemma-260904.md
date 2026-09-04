# Q3LOCK finite-grid to loop-limit lemma

**Status:** T0 research addendum; paper-local analytic lemma with audit gates  
**Date:** 2026-09-04  
**Owner task:** T-054  
**PDF:** deferred

## 1. Setting

Fix a finite spatial volume `Lambda`, an inverse temperature `beta>0`, a
compact source interval `|h|<=h0`, and a positive harmonic split `a>0`.
Write `m=chi/hbar^2`, `epsilon=beta/N`, and let `G_(a,N)` be the product
periodic Gaussian on grid values `x_(y,k) in R^8` with action

```text
S_(a,N)(x) = m/(2*epsilon) * sum_(y,k) |x_(y,k+1)-x_(y,k)|^2
             + a*epsilon/2 * sum_(y,k) |x_(y,k)|^2.
```

The residual local potential is denoted by `V_(h,a)`; the split is chosen so
that, uniformly for `|h|<=h0`,

```text
V_(h,a)(q) >= A*|q|^4-C,
```

with `A>0`.  The grid weight relative to `G_(a,N)` is

```text
R_(N,h)(x) = exp[-epsilon*sum_(y,k) V_(h,a)(x_(y,k))]
             * exp[-epsilon*c/2*sum_(k,<yz>)
                    |x_(y,k)-x_(z,k)|^2].
```

Let `I_N x` be the periodic piecewise-linear interpolation.  The exact
finite-volume loop law is the corresponding weighted product periodic
Ornstein--Uhlenbeck law `G_a` on `C_per([0,beta];R^8)^Lambda`.

## 2. Gaussian interpolation convergence

The one-component grid precision has diagonal
`2m/epsilon+a*epsilon`, cyclic off-diagonal `-m/epsilon`, and Fourier
eigenvalues

```text
kappa_(N,l) = a*epsilon
              + (2*m/epsilon)*(1-cos(2*pi*l/N)),
              l=0,...,N-1.
```

For every fixed finite set of Fourier modes, the covariance of `I_N x`
converges to the covariance of the periodic Gaussian with operator
`-m*d^2/dtau^2+a`.  The same Fourier representation gives constants
`C_p`, independent of all sufficiently large `N`, such that for every
`p>=2` and `s,t in [0,beta]`,

```text
E_(G_(a,N)) |I_N x(t)-I_N x(s)|^p <= C_p*|t-s|^(p/2).
```

The bound includes the wrap-around interval.  Choosing `p>2` in the
Kolmogorov criterion proves tightness in the periodic continuous-loop
sup-norm topology.  Finite-dimensional covariance convergence plus tightness
therefore gives

```text
I_N#G_(a,N) => G_a.
```

The argument is componentwise and survives the finite product over `Lambda`.
It is the only Gaussian compactness input needed below; it does not invoke a
path-space MTP2 theorem.

## 3. Weighted-law convergence and normalizer

The Riemann-sum statement must be made on a compact subset of the loop space,
not on an arbitrary bounded sup-norm ball.  A compact subset of
`C_per([0,beta];R^8)^Lambda` is uniformly bounded and equicontinuous by
Arzela--Ascoli.  On such a compact `K`, the Riemann sums in `R_(N,h)` converge
uniformly to

```text
R_h(omega) = exp[-integral_0^beta sum_y V_(h,a)(omega_y(tau)) d tau]
             * exp[-c/2*integral_0^beta sum_<yz>
                    |omega_y(tau)-omega_z(tau)|^2 d tau].
```

The quartic lower bound gives the global upper estimate
`R_(N,h)<=exp(beta*V*C)`; the spatial factor is at most one.  The explicit
sup-norm-ball estimate in
`q3lock-fkg-normalizer-tightness-check-260904.md` gives a positive lower bound
for `E_(G_(a,N)) R_(N,h)` independent of `N`.

Choose a compact `K` with arbitrarily large Gaussian probability using the
mesh-uniform tightness from Section 2.  Uniform convergence on `K`, the global
weight upper bound, and the two-sided normalizer bounds then imply

```text
I_N#(R_(N,h) G_(a,N) / E R_(N,h)) => R_h G_a / E_(G_a) R_h.
```

The quartic bound and the same ratio estimate give uniform polynomial moments.
This identifies the weak limit with the finite-volume Euclidean
Feynman--Kac law for the split Hamiltonian; no formal infinite-dimensional
transfer matrix is used.

## 4. Association passage

At every finite `N`, the cyclic Gaussian precision is an M-matrix.  The
spatial and Q3LOCK factors have nonnegative mixed log derivatives, including

```text
-epsilon*d^2/dxdy [(lambda/4)(x-y)^2(x^2+y^2)]
  = (epsilon*lambda/4)*[(x+y)^2+5*(x-y)^2] >= 0.
```

Thus the grid law is associated.  If `F` and `G` are bounded continuous
pointwise-increasing functionals on the loop space, then `F(I_N x)` and
`G(I_N x)` are increasing functions of the grid coordinates.  Weak convergence
and boundedness give

```text
E_h[FG] >= E_h[F] E_h[G]
```

for the exact loop law.  For coordinate products, apply this inequality to
the bounded increasing clips `q -> max(-R,min(q,R))` and let `R->infinity`
using the uniform second-moment bound.  The conclusion is association, not
path-space MTP2 or total-variation convergence.

## 5. Shifted spatial bonds and Gaussian domination

For a fixed finite edge field `b` in the weighted grid Hilbert space, the
shifted spatial factor satisfies

```text
exp[-c*||D omega-b||^2/2]
  <= exp[c*||b||^2/2] * exp[-c*||D omega||^2/4].
```

The right side is integrable under the quartically confined local law.  For a
time-constant zero-sum source `j_y(tau)=s*a_y*u`, the Poisson edge field
`b=(1/c)D L_sp^(-1)j` is time-constant and has the same weighted norm at every
mesh.  Consequently the shifted grid partition functions have the same weak
loop limit as their exact continuous-loop counterparts, and the finite-grid
FSS inequality passes to the loop law.

All linear source exponential moments are finite by quartic Young absorption.
Therefore the limiting source moment is twice differentiable at zero and the
finite-grid Gaussian-domination inequality yields

```text
log E_0 exp(<j,omega>)
  <= (1/(2c))*<j,L_sp^(-1)j>.
```

## 6. Audit boundary

The displayed argument supplies the paper-local structure for the time-grid
and constant-source passages in P-06 and P-09.  An independent reviewer must
still check the discrete covariance estimate, the Kolmogorov exponent, the
uniform-on-compacts Riemann-sum argument, the normalizer ratio, and the exact
Feynman--Kac identification with the chosen Hamiltonian and source units.
No claim is promoted, and no infrared phase, pressure cusp, DLR multiplicity,
independent manuscript, release, or PDF is created by this addendum.
