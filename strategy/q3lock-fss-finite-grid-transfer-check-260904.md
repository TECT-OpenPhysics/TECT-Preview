# Q3LOCK finite-grid FSS transfer and infrared normalization check

**Status:** T0 research addendum; conditional finite-grid lemma only  
**Date:** 2026-09-04  
**Owner task:** T-054  
**PDF:** deferred

## 1. Finite-dimensional reduction

Fix an even periodic spatial cube `Lambda` and a Euclidean time mesh
`epsilon=beta/N`.  At each spatial site collect the eight components and all
time slices into

```text
a_y = (x_(y,k,e))_(k=0,...,N-1; e=1,...,8) in R^(8N),
<a,b>_N = epsilon * sum_(k,e) a_(k,e)b_(k,e).
```

Rescaling `a -> sqrt(epsilon)*a` identifies this weighted space with the
standard finite-dimensional Euclidean space, so the ordinary
Froehlich--Simon--Spencer transfer theorem applies at each fixed `N`.

The single-site a-priori measure contains the cyclic kinetic quadratic form,
the scalar and Q3LOCK onsite factors, the positive harmonic split, and the
source-free compensating terms.  The common quartic lower bound implies

```text
integral exp(alpha*||a_y||_N^2) d(lambda_N)(a_y) < infinity
```

for every fixed `N` and every real `alpha`.  No radial or internal `O(8)`
symmetry is assumed.

## 2. Crossing kernel and transfer inequality

For a spatial bond crossing a reflection plane, the finite-grid factor is

```text
K_N(a,b) = exp[-c*||a-b||_N^2/2]
         = exp[-c*||a||_N^2/2]
           exp[-c*||b||_N^2/2]
           exp[c*<a,b>_N].
```

The last kernel is positive definite because

```text
exp[c*<a,b>_N] = sum_(n>=0) c^n/n! * <a^(tensor n),b^(tensor n)>.
```

Thus every reflected partition function is a positive square for the
arbitrary anisotropic single-site measure.  The finite-dimensional FSS
transfer argument gives

```text
Y_N(b) <= Y_N(0)
```

for every collection of finite-dimensional edge shifts `b`.  This statement
is finite-dimensional and does not assert a transfer matrix on the loop
space.

## 3. Zero-sum source and exact factors

Orient every spatial edge once and write `D` for the corresponding incidence
operator and `L_sp=D^*D`.  For a zero-sum source `j` choose

```text
b = (1/c) * D * L_sp^(-1) j.
```

Expanding the shifted square gives

```text
c*<D omega,b>_N = <omega,j>_N,
(c/2)*||b||_N^2 = (1/(2c))*<j,L_sp^(-1)j>_N.
```

Differentiating `log Y_N(t b) <= log Y_N(0)` twice at `t=0` therefore gives

```text
Var_N(<j,omega>_N)
    <= (1/c) * <j,L_sp^(-1)j>_N.
```

For the load-bearing time-constant source `j_y(tau)=s*a_y*u`, with
`sum_y a_y=0` and `u=(1,...,1)/sqrt(8)`, the source is represented exactly
on every time mesh.  If `D_(N,L)` denotes the finite-grid integrated
Duhamel covariance, then

```text
beta^2 * a^T D_(N,L) a
    <= (beta/c) * a^T L_sp^(-1) a.
```

The spatial eigenvalue is `2 E(p)`, where
`E(p)=sum_j(1-cos(p_j))`.  Consequently the finite-grid bound has the exact
normalization

```text
Dhat_(N,L)(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

## 4. Remaining loop-limit obligation

The finite-grid transfer is compatible with the continuous-loop route because
the required source is time-constant.  To pass the displayed inequality to
the exact loop law, the manuscript must still supply the Feynman--Kac/Trotter
identification of the weighted grid laws, the shifted quartic majorant,
uniform integrability, and differentiation of the limiting source moment.  The
normalizer and spatial-factor bound are recorded separately in
`q3lock-fkg-normalizer-tightness-check-260904.md`.  The KKK rotation-invariant
corollary is not used.

No arbitrary-`L2` edge-field theorem, path-space transfer matrix,
rotation-invariance claim, infrared phase conclusion, pressure cusp, DLR
multiplicity, independent claim, manuscript, release, or PDF is created by
this addendum.

