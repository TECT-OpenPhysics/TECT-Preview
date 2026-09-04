# Q3LOCK P-09 FSS Poisson-shift and infrared-constant audit

**Status:** T0 finite-grid constant audit; independent review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Pinned source:** FSS, Commun. Math. Phys. 50 (1976), 79--95; the
hash-frozen PDF is listed in `strategy/q3lock-literature-source-freeze-260905.md`  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and boundary

This note checks the exact constant in the finite-dimensional
Froehlich--Simon--Spencer (FSS) source estimate used by P-09.  The source
paper's Theorem 2.1 is an exponential bound for a discrete divergence source,
with right side `(2J)^(-1)` times the squared norm of the auxiliary edge
field.  The Q3LOCK source is mapped to that theorem by a minimum-norm Poisson
shift.  The calculation below exposes the source scaling, the zero-mode
restriction, and the spatial factor `2` in the Fourier denominator.

This is a finite spatial cube and a finite Euclidean time mesh.  It does not
prove the continuous-loop limit, an infinite-volume infrared lower bound, a
pressure cusp, or DLR multiplicity.

## 2. Exact FSS theorem block

For a periodic rectilinear cube, FSS defines the forward differences

```text
(partial_i h_i)(y) = h_i(y+e_i)-h_i(y)
```

and the graph Laplacian

```text
(-Delta h)(y) = 2*v*h(y) - sum_i [h(y+e_i)+h(y-e_i)].
```

With a finite vector spin at each site and an arbitrary single-site measure
having every finite quadratic exponential moment, Theorem 2.1 states

```text
E exp[ sigma(sum_i partial_i h_i) ]
   <= exp[ (2*J)^(-1) * sum_(y,i) |h_i(y)|^2 ].
```

The same source gives the second-moment form in Theorem 2.2 and the
translation-invariant Laplacian form in Theorem 2.3.  The exponential form is
the one used here.  The source's nearest-neighbour pair is counted once and
the right side is independent of the spin component number and the
single-site prior.

## 3. Q3LOCK finite-grid identification

At one spatial site encode the complete time history by

```text
s_y = sqrt(epsilon)*(x_(y,k))_(k=0,...,N-1) in R^(8N),
epsilon=beta/N.
```

The spatial bond in the Q3LOCK action becomes

```text
(c/2)*sum_<yz> |s_y-s_z|^2
   = 3*c*sum_y |s_y|^2 - c*sum_<yz> s_y dot s_z.
```

The first term is local and belongs to the one-site prior; the second gives
the FSS coupling `J=c`.  The temporal kinetic, scalar quartic, Q3 locking,
and all compensating local factors are also in that prior.  At each finite
`N`, the quartic lower bound implies every finite quadratic exponential
moment required by FSS.  No radial or `O(8)` symmetry is used.

For a real spatial test field `a` with `sum_y a_y=0`, let

```text
j_y = t*sqrt(epsilon)*(a_y*u)_(k=0,...,N-1),
u=(1,...,1)/sqrt(8).
```

The ordinary Euclidean pairing is exactly

```text
sum_y j_y dot s_y
  = t*epsilon*sum_(y,k) a_y*(u dot x_(y,k))
  = t*X_(N,L)(a).
```

## 4. Minimum-norm Poisson shift

Let `D_FSS` denote the FSS discrete-divergence map
`h -> sum_i partial_i h_i`, with its adjoint chosen so that

```text
L_sp = D_FSS*D_FSS^*
```

on the spatial zero-sum subspace.  This is the positive graph Laplacian with
eigenvalue `2*E(p)`, where `E(p)=sum_i(1-cos(p_i))`.  For zero-sum `j`, choose

```text
h = D_FSS^* L_sp^(-1) j.
```

Then `D_FSS h=j` and the minimum-norm identity is

```text
sum_(y,i) |h_i(y)|^2 = <j,L_sp^(-1)j>.
```

Because `j` is constant in the time-slice coordinate and `|u|=1`,

```text
<j,L_sp^(-1)j>
  = beta*t^2*<a,L_sp^(-1)a>.
```

Applying FSS Theorem 2.1 with `J=c` gives the exact finite-grid estimate

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
  <= beta*t^2/(2*c) * <a,L_sp^(-1)a>.
```

The finite-grid variance bound follows by differentiating the finite
log-Laplace transform at zero:

```text
Var_(N,L,0)(X_(N,L)(a))
  <= beta/c * <a,L_sp^(-1)a>.
```

No extra factor `8` appears: the collective direction is the unit vector
`u`, and all eight components are already one coordinate block of `s_y`.

## 5. Duhamel and Fourier conversion

With the loop convention

```text
Var(X_L(a)) = beta^2*<a,D_L a>,
D_L = (1/beta)*integral_0^beta C(tau) d tau,
```

the finite-grid bound, after the separately audited loop passage, gives

```text
<a,D_L a> <= (1/(beta*c))*<a,L_sp^(-1)a>.
```

For a nonzero spatial Fourier mode, `L_sp` has eigenvalue `2*E(p)`.  Hence

```text
Dhat_L(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

The source is zero-sum, so the constant mode is never inverted.  The factor
`beta` comes only from `N*epsilon=beta`; the factor `2` comes only from the
graph-Laplacian eigenvalue.  Neither is a fitted parameter.

## 6. Adversarial checks

1. **Use `J=2c` because every site has six neighbours.**  Rejected: FSS
   counts each undirected pair once, and the Q3LOCK bond expansion gives
   `-c*sum_<yz> s_y dot s_z`, so `J=c`.
2. **Invert the Laplacian on a constant source.**  Rejected: `sum_y a_y=0`
   is imposed before the Poisson shift.
3. **Insert a factor `8` from the component count.**  Rejected: `u` is unit
   norm and the FSS spin is the full `R^(8N)` history vector.
4. **Use the ordinary source entries `t*a_y*u` after scaling the spin.**
   Rejected: ordinary coordinates require `t*sqrt(epsilon)*a_y*u`.
5. **Treat the FSS estimate as a continuous-loop or thermodynamic theorem.**
   Rejected: all statements here are finite `N` and finite `L`.
6. **Import the FSS bound as an `O(8)`-invariant result.**  Rejected: the
   source theorem permits an arbitrary finite single-site prior; its exact
   hypotheses still require independent sign-off in the Q3LOCK context.

## 7. Disposition and review gate

**Advanced at T0:** the source theorem's `(2J)^(-1)` constant, the
minimum-norm Poisson shift, the `sqrt(epsilon)` source map, and the `2*E(p)`
Fourier factor are written in one convention.  This repairs the remaining
constant ambiguity in the P-09 proof text.

**Still open:** independent verification of the FSS theorem-version and
discrete-divergence convention, the finite-grid/Feynman--Kac identification,
source-uniform loop passage, spatial thermodynamic limit, Duhamel/source
tangent composition, and external referee review.  No claim card, phase
theorem, manuscript release or PDF is created.
