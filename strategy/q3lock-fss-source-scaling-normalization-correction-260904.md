# Q3LOCK FSS source scaling and normalization correction

**Status:** T0 proof-text correction; P-09 remains open pending independent
theorem audit  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred

## 1. Issue found

The finite-grid FSS notes used two equivalent coordinate conventions but did
not state their conversion in the source vector.  If the time-slice variables
are encoded as the ordinary Euclidean spin

```text
s_y = sqrt(epsilon)*(x_(y,k))_(k=0,...,N-1) in R^(8N),
```

then a time-integrated source is not represented by entries `t*a_y*u`; its
ordinary-coordinate entries are `t*sqrt(epsilon)*a_y*u` at every slice.  The
unscaled notation `j_y(tau)=t*a_y*u` is correct only when the spin space is
kept with the weighted inner product

```text
<v,w>_N = epsilon*sum_(y,k) v_(y,k) dot w_(y,k).
```

This is a notation/normalization repair, not a change to the finite-grid
inequality.  The two conventions are related by the isometry
`x -> sqrt(epsilon)*x`.

## 2. Exact conversion

Let `sum_y a_y=0` and `u=(1,...,1)/sqrt(8)`.  The loop source observable on a
mesh is

```text
X_(N,L)(a) = epsilon*sum_(y,k) a_y*(u dot x_(y,k)).
```

In the weighted convention, use the time-constant source

```text
j_y(k) = t*a_y*u,
```

so that

```text
<j,x>_N = t*epsilon*sum_(y,k) a_y*(u dot x_(y,k))
         = t*X_(N,L)(a).
```

In ordinary coordinates `s_y=sqrt(epsilon)*x_y`, use instead

```text
eta_y = t*sqrt(epsilon)*(a_y*u)_(k=0,...,N-1),
```

and obtain the identical pairing

```text
sum_y eta_y dot s_y = t*X_(N,L)(a).
```

The spatial bond remains

```text
-c*epsilon*sum_<yz>,k x_(y,k) dot x_(z,k)
 = -c*sum_<yz> s_y dot s_z,
```

so the FSS coupling parameter is still `c`.  The source norm is

```text
sum_y |eta_y|^2 = beta*sum_y |a_y|^2,
```

which is the origin of the single factor `beta` in the shifted Gaussian
bound.

## 3. Consequence for the FSS and Duhamel ledger

For the zero-sum source, set `b=(1/c)D L_sp^(-1)j` in the weighted convention,
or use its isometric image in ordinary coordinates.  The finite-dimensional
FSS transfer gives

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
 <= beta*t^2/(2*c) * <a,L_sp^(-1)a>.
```

The second derivative at zero is therefore

```text
Var_(N,L,0)(X_(N,L)(a))
 <= beta/c * <a,L_sp^(-1)a>.
```

With `Var(X_(N,L)(a))=beta^2<a,D_(N,L)a>` and the spatial eigenvalue
`2*E(p)`, this yields

```text
Dhat_(N,L)(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

No factor of `sqrt(epsilon)`, `epsilon`, `beta` or two is omitted once one
convention is used consistently.  The prior finite-grid FSS note already
uses the weighted convention; the source-differentiation note now states both
forms explicitly.

## 4. Adversarial boundary checks

* The correction does not turn a weighted inner product into an unweighted
  one without the `sqrt(epsilon)` isometry.
* The source is zero-sum, so `L_sp^(-1)` is used only on the nonconstant
  spatial subspace.
* The correction does not claim a time-grid limit, source-exponential
  uniform integrability, or the continuous-loop Duhamel identity; those remain
  separate obligations.
* The correction does not import the KKK rotation-invariant vector corollary.
* The correction does not change the Q3LOCK phase sufficient condition or any
  claim/tier.

## 5. Required manuscript action

The final proof must choose one convention at the start of the FSS lemma.  If
ordinary coordinates are used, display `eta_y=t*sqrt(epsilon)*(a_y*u)_k`.
If the weighted convention is used, define `<.,.>_N` before invoking FSS and
state the isometric rescaling to the source theorem's ordinary Euclidean
coordinates.  The independent reviewer must check the same choice in the
source pairing, shifted Poisson field and Duhamel variance definition.

P-09 remains **PROOF TEXT AND EXTERNAL AUDIT REQUIRED**.  No claim card,
manuscript release or PDF is created by this correction.

