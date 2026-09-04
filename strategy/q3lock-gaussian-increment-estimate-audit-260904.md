# Q3LOCK Gaussian interpolation increment estimate

**Status:** T0 research addendum; explicit paper-local derivation with audit gates  
**Date:** 2026-09-04  
**Owner task:** T-054  
**PDF:** deferred

## 1. Purpose and fixed scope

This note supplies the missing estimate used in the finite-time-grid to
continuous-loop passage for P-06 and P-09.  The spatial volume `Lambda`, the
number of components (`8`), `beta`, `m>0`, and the harmonic split `a>0` are
fixed.  Only the periodic time mesh is refined.  No infinite spatial-volume
or continuum-spatial limit is asserted.

Set `epsilon=beta/N`.  For one real component, the centered grid Gaussian has
cyclic precision

```text
K_(N) = (2*m/epsilon+a*epsilon) I - (m/epsilon)(S+S^*)
```

and eigenvalues

```text
kappa_(N,l) = a*epsilon + (2*m/epsilon)(1-cos(2*pi*l/N)).
```

The zero mode is harmless because `a>0`; all estimates below are uniform in
`N`.

## 2. Exact grid-increment bound

For an integer separation `r` with `0<=r<=N`, translation invariance and the
discrete Fourier transform give

```text
v_(N,r) := E |x_(k+r)-x_k|^2
         = (1/N) sum_(l=0)^(N-1)
             2(1-cos(2*pi*l*r/N))/kappa_(N,l).
```

The zero-mode summand vanishes.  Since `kappa_(N,l) >=
(2*m/epsilon)(1-cos(2*pi*l/N))` for `l!=0`,

```text
v_(N,r) <= (epsilon/(m*N))
           sum_(l=1)^(N-1)
           (1-cos(2*pi*l*r/N))/(1-cos(2*pi*l/N)).
```

The cycle effective-resistance identity

```text
(1/N) sum_(l=1)^(N-1)
  (1-cos(2*pi*l*r/N))/(1-cos(2*pi*l/N))
  = r(N-r)/N
```

therefore yields the load-bearing estimate

```text
v_(N,r) <= (epsilon/m) * r(N-r)/N <= (epsilon/m) r.       (2.1)
```

In particular, one mesh increment has variance at most `epsilon/m`.  The
bound is valid without using a massless zero-mode inverse; the positive
harmonic term only decreases the variance.

## 3. Piecewise-linear interpolation

Let `I_N x` be the periodic linear interpolation.  Write `delta=|t-s|`
for the shorter representative on the time circle, so `0<=delta<=beta/2`.

### 3.1 Sub-mesh separations

If `delta<=epsilon`, the two points lie in one cell or in two cells sharing a
vertex.  In either case their difference is a sum of at most two adjacent
mesh increments with nonnegative coefficients whose sum is `delta/epsilon`.
Using

```text
|sum_i alpha_i d_i|^2 <= (sum_i alpha_i)
                         sum_i alpha_i |d_i|^2,
```

and (2.1) with `r=1` gives

```text
E |I_N x(t)-I_N x(s)|^2
  <= (delta/epsilon)^2 * (epsilon/m)
  <= delta/m.                                             (3.1)
```

This explicitly handles the apparent large slope of a linear interpolant at
scales below one mesh spacing.

### 3.2 Separations of at least one mesh

For `delta>=epsilon`, choose the oriented mesh arc from the cell containing
`s` to the cell containing `t`.  If `r` is the number of complete mesh steps,
then `r*epsilon <= delta+epsilon`.  The interpolation identity writes the
difference as a grid endpoint difference plus at most two fractional mesh
increments.  The elementary three-term inequality and (2.1) imply

```text
E |I_N x(t)-I_N x(s)|^2
  <= 3*(epsilon*r/m + 2*epsilon/m)
  <= 9*delta/m.                                           (3.2)
```

The same argument on the reverse arc covers the periodic seam.  Combining
(3.1)--(3.2),

```text
sup_N sup_(s,t) E |I_N x(t)-I_N x(s)|^2
  <= C_(m) * d_circle(s,t),
```

with a mesh-independent constant `C_(m)` (for example `9/m` in the displayed
normalization).  For the `8*|Lambda|`-dimensional field, the right side is
multiplied only by the fixed component-volume factor.

## 4. Gaussian higher moments and tightness

Every increment is a centered Gaussian vector.  For each `p>=2`, the finite
dimensional Gaussian moment comparison gives

```text
E ||I_N x(t)-I_N x(s)||^p
  <= C_(p,8|Lambda|) [C_(m,Lambda) d_circle(s,t)]^(p/2).
```

Choose any `p>2`.  The exponent `p/2>1` satisfies the one-dimensional
Kolmogorov criterion, uniformly in `N`; periodicity is handled by the circle
metric.  Thus the interpolated Gaussian laws are tight in
`C_per([0,beta];R^8)^Lambda`.

## 5. Covariance convergence (what remains to check)

For fixed temporal Fourier indices, `kappa_(N,l)/epsilon` converges to
`a+m(2*pi*l/beta)^2`, and the linear-interpolation shape factor converges to
one.  The tail is dominated by the discrete kinetic denominator, using

```text
(1-cos(2*pi*l/N)) >= c * (l/N)^2
```

for `|l|<=N/2`.  Consequently the finite-mode covariance sums converge to the
periodic Green kernel of `-m*d^2/dtau^2+a`.  This is the finite-dimensional
convergence input; the increment estimate above supplies tightness, so the
Gaussian interpolation laws converge weakly to the periodic
Ornstein--Uhlenbeck loop law.

The exact tail domination and the interpolation shape-factor bookkeeping must
be checked independently against the chosen normalization before publication.

## 6. Adversarial checks and boundary

* A covariance bound at mesh points alone is insufficient below one mesh
  spacing; (3.1) is required.
* The positive `a` term cannot be dropped before controlling the zero mode;
  the proof compares to the kinetic denominator only for nonzero modes, where
  the numerator already vanishes at `r=0`.
* The cycle identity controls fixed finite spatial volume only; it is not a
  uniform spatial-volume or spatial-continuum estimate.
* Kolmogorov tightness plus finite-dimensional covariance convergence identifies
  the Gaussian limit, but does not by itself identify the interacting
  Feynman--Kac weight; that weighted-law step remains a separate audit.

This addendum advances the analytic limit framework at T0.  It creates no
independent claim, no DLR multiplicity result, no strict source cusp, no P2
manuscript, and no PDF.
