# Q3LOCK P-06 Gaussian tightness and normalizer audit

**Status:** T0 finite-mesh analytic audit; external review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and boundary

The P-06 proof needs a genuine compactness argument for the time-grid laws,
not a citation to a path-space FKG theorem.  This note supplies the missing
finite-volume estimates in a form that can be inserted before the finite-grid
association step:

1. a massive periodic Gaussian reference removes the temporal constant-mode
   singularity;
2. its diagonal and increment covariances are uniform in the mesh;
3. the Q3LOCK residual action has a Jensen normalizer lower bound uniform in
   the mesh at fixed spatial volume; and
4. quartic coercivity supplies the exponential and second-derivative uniform
   integrability needed for the weighted loop limit and the P-09 source
   passage.

The statement is fixed finite spatial volume and compact source interval.  It
does not prove a spatial thermodynamic limit, a uniform-in-volume common core,
the continuous-loop FKG theorem by itself, a DLR phase, a cusp, or a PDF.

## 2. Frozen finite-mesh decomposition

Fix a periodic spatial cube `Lambda_L` with `V=L^3`, a finite number `N` of
time slices, `epsilon=beta/N`, and `m=chi/hbar^2>0`.  Let `x_(y,k) in R^8`
with cyclic index `k+N=k`.  Choose an auxiliary `a>0` and use the normalized
product Gaussian with action

```text
S_G,N(x) = (1/2) sum_(y,k)
             [(m/epsilon)|x_(y,k+1)-x_(y,k)|^2
              + a*epsilon*|x_(y,k)|^2].
```

The exact finite-grid Q3LOCK law is written as

```text
mu_(N,L,h)(dx) = Z_(N,L,h)^(-1) exp(-R_(N,L,h)(x)) gamma_(N,L)(dx),
```

where `gamma_(N,L)` is the centered Gaussian defined by `S_G,N`, and
`R_(N,L,h)` contains the compensating local quadratic, the Q3 quartic,
the source, and the nonnegative spatial difference term.  The auxiliary `a`
is recombined with the compensating quadratic before the continuum Hamiltonian
is stated; it is not a new model parameter.

For a compact source interval `|h|<=h_0`, the local quartic audit supplies

```text
V_(h,a)(q) >= alpha*|q|^4 - C_(a,h_0),
alpha = g/128,
```

in the declared Q3LOCK normalization.  Consequently

```text
R_(N,L,h)(x) >= alpha*S4_(N,L)(x) - beta*V*C_(a,h_0),
S4_(N,L) = epsilon*sum_(y,k)|x_(y,k)|^4.
```

The spatial part of `R_(N,L,h)` is nonnegative.  All constants below may
depend on fixed `L`, `beta`, `m`, `a`, `g`, `lambda`, `r`, and `h_0`, but not on
`N`.

## 3. Exact Gaussian covariance bounds

The scalar cyclic precision eigenvalues are

```text
kappa_(N,j) = 4*m/epsilon*sin^2(pi*j/N) + a*epsilon,
               j=0,...,N-1.
```

The diagonal covariance is therefore

```text
g_N(0) = (1/N)*sum_j 1/kappa_(N,j).
```

The zero mode contributes exactly `1/(beta*a)`.  For `j!=0`, discard the
positive `a*epsilon` term and use the exact identity

```text
sum_(j=1)^(N-1) csc^2(pi*j/N) = (N^2-1)/3.
```

This gives the mesh-uniform bound

```text
g_N(0)
 <= 1/(beta*a) + epsilon/(4*m*N)*(N^2-1)/3
 <= 1/(beta*a) + beta/(12*m)
 =: K_(m,a,beta).
```

Every scalar coordinate has fourth moment at most `3*K^2` under `gamma`.
The eight-component and finite-site moments follow by the finite-dimensional
Gaussian moment inequalities; no constant in this paragraph is a fitted
numerical input.

## 4. Uniform increment estimate and interpolation tightness

Let `r=min(|k-l|,N-|k-l|)`.  For one scalar coordinate, comparison with the
massless denominator and the cyclic resistance identity give

```text
E_gamma |x_k-x_l|^2
 <= epsilon/(2*m*N)
       *sum_(j=1)^(N-1)[1-cos(2*pi*j*r/N)]/sin^2(pi*j/N)
 = epsilon*r*(N-r)/(m*N)
 <= epsilon*r/m.
```

The middle equality uses

```text
sum_(j=1)^(N-1)[1-cos(2*pi*j*r/N)]/sin^2(pi*j/N)=2*r*(N-r).
```

For every `p>=2`, finite-dimensional Gaussian hypercontractivity (or the
explicit Gaussian moment formula) then yields

```text
E_gamma |x_k-x_l|^p <= C_(p,8)*(epsilon*r/m)^(p/2).
```

For the interacting law, the quartic lower bound and the normalizer estimate
in Section 5 below imply

```text
E_mu |x_k-x_l|^p <= C_(L,p)*[epsilon*r]^(p/2),
```

uniformly in `N`, `h`, and the spatial site.  Piecewise-linear periodic
interpolation `I_N` changes an arbitrary pair of times by at most two nearest
grid increments.  Choosing `p>2` gives an exponent `p/2>1`; Kolmogorov's
criterion on the circle therefore gives tightness of the interpolated laws in
the finite-volume periodic sup-norm topology.  This is a fixed-volume result;
the KKK weighted tempered topology is used only after the spatial accumulation.

## 5. Jensen lower bound for the residual normalizer

The Gaussian expectation of the residual action is finite.  The bound in
Section 3, the estimate `E_gamma|x|^4<=3*K^2`, and independence of distinct
spatial sites under `gamma` give a constant `C_(L,h_0)` such that

```text
E_gamma[R_(N,L,h)] <= beta*V*C_(L,h_0)
```

for every `N` and `|h|<=h_0`.  The centered Gaussian makes the linear source
term have zero expectation.  Jensen's inequality consequently yields

```text
Z_(N,L,h)=E_gamma[exp(-R_(N,L,h))]
          >= exp(-beta*V*C_(L,h_0)).
```

The coercive lower bound also gives the pointwise estimate

```text
exp(-R_(N,L,h)) <= exp(beta*V*C_(a,h_0))
```

after dropping the nonnegative quartic and spatial terms.  Thus the
normalized grid weights have a mesh-uniform denominator and a fixed-volume
upper envelope.  This replaces an informal Gaussian sup-norm event with an
explicit expectation bound.

## 6. Quartic uniform integrability for the loop and source limits

For a finitely supported zero-sum spatial vector `a_y`, define

```text
X_(N,L)(a) = epsilon*sum_(y,k) a_y*(u,x_(y,k)).
```

Weighted Holder gives

```text
|X_(N,L)(a)|
 <= [beta*sum_y|a_y|^(4/3)]^(3/4)*S4_(N,L)^(1/4).
```

For every fixed `T`, Young's inequality therefore supplies constants
`delta>0` and `C_(T,delta,a)` with

```text
T*|X_(N,L)(a)| <= delta*S4_(N,L)+C_(T,delta,a).
```

Choosing `2*delta<alpha`, the coercive bound and the Jensen denominator imply
mesh-uniform integrability of

```text
exp(T*|X_(N,L)(a)|),
X_(N,L)(a)^2*exp(T*|X_(N,L)(a)|).
```

The same argument with a bounded continuous functional of `I_N x` multiplied
in front proves that weak convergence of the interpolated laws passes both
the source exponential and its second derivative.  The cyclic interpolation
identity is exact:

```text
integral_0^beta (u,I_N x_y)(tau)d tau
 = epsilon*sum_k (u,x_(y,k)).
```

There is no hidden `O(epsilon)` source error.  Hence, once the Gaussian
reference convergence and residual Riemann-sum convergence are independently
inserted, the finite-grid FSS inequality and its second derivative pass to the
continuous-loop law.

## 7. Consequences and strict boundary

This audit supplies the analytic estimates needed to make the P-06/P-09 proof
text precise at fixed spatial volume:

- the time-grid interpolation laws are tight in periodic sup norm;
- the residual normalizers are bounded away from zero uniformly in the mesh;
- quartic domination passes clipped products, source exponentials, and second
  derivatives through the loop limit; and
- the source scaling in the FSS step is exact under cyclic interpolation.

It does not by itself prove the finite-dimensional FKG lattice condition, the
FSS theorem, the operator trace differentiation, the spatial thermodynamic
limit, or the DLR/source-tangent composition.  The independent KP/FSS source
audit, the operator/form-domain audit, and the P-06/P-09 round-2 audit remain
required.  No claim card, phase theorem, manuscript release, or PDF is created.

## 8. Adversarial checks

1. **Use the pure periodic kinetic Gaussian as a probability reference.**
   Rejected: its constant mode is singular; the auxiliary `a>0` split is
   required and is recombined into the local potential.
2. **Use weak convergence without a source-uniform integrability bound.**
   Rejected: the quartic Holder--Young estimate and the Jensen denominator are
   explicitly required for the exponential and second-derivative witnesses.
3. **Claim the increment estimate is already uniform in spatial volume.**
   Rejected: constants are uniform in `N` at fixed `L`; no `L`-uniform common
   core or thermodynamic estimate is asserted.
4. **Treat the discrete kinetic action as uniformly convergent on all compact
   subsets of `C_per`.**  Rejected: only the residual Riemann sums are compared
   on equicontinuous compact sets; the Gaussian reference carries the kinetic
   limit.
5. **Hide a source discretization error in the FSS map.**  Rejected: periodic
   piecewise-linear interpolation integrates each segment exactly, producing
   the displayed cyclic identity.
6. **Promote these bounds to a phase result or a PDF.**  Rejected: FKG, IR,
   pressure, tangent-state, independent-review, content-freeze, and final PDF
   gates remain separate.

## 9. Reproduction and review gate

The exact csc-squared and cyclic-resistance identities should be checked in the
independent Q3LOCK verifier before manuscript transcription.  The current
primary, independent, and integrated scripts remain regression witnesses only;
they do not replace this analytic estimate.  A mathematical reviewer must
check the Gaussian comparison, the residual split, the fixed-volume scope, and
the order of the mesh, spatial, and source limits.  PDF compilation and visual
review remain final-stage actions only.
