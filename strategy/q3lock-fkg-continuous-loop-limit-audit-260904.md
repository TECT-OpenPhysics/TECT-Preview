# Q3LOCK continuous-loop FKG limit audit

**Status:** T0 proof-text audit; P-06 remains open pending independent review  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Purpose and scope

The finite-time-grid sign calculation is not, by itself, an FKG theorem for
the continuous periodic-loop Gibbs law.  This note records the complete
finite-grid association argument, the order-preserving interpolation, and the
weak-limit passage used at fixed spatial volume.  It also isolates the
uniform-integrability step for the unbounded same-site coordinate products
used in the collective Q3 estimate.

The result is only a fixed finite spatial-volume statement.  It does not
prove the strict source cusp, the infrared lower bound, a spatial thermodynamic
limit, or DLR multiplicity.  P-06 remains subject to an independent theorem
and source audit.

## 2. Finite grid and positive density

Fix a spatial box `Lambda`, inverse temperature `beta`, source `h` in a
compact interval, and a positive harmonic split `a>0`.  Put
`epsilon=beta/N` and use the periodic grid variables `x_(y,k) in R^8`.
For the sign argument take `N>=3`; the `N=1,2` cyclic conventions are not
needed in the limit.  The one-component reference action has precision

```text
K_N = (2*m/epsilon+a*epsilon) I
      -(m/epsilon)(shift + shift^T),       m=chi/hbar^2>0.
```

For `N>=3`, every temporal off-diagonal entry is `-m/epsilon`; for `N=2`
the two directed bonds combine to `-2m/epsilon`, which has the same sign.
The spatial difference-square factor contributes a cross entry `-c*epsilon`
between corresponding coordinates at neighbouring sites.  The full finite
grid density is strictly positive and integrable because the Q3LOCK and
onsite quartic terms dominate all negative quadratic and linear pieces.

## 3. Log-supermodularity calculation

For a positive `C^2` density, nonnegative mixed second derivatives of its log
are the differential lattice condition for MTP2.  The reference Gaussian
gives

```text
partial_(x_(y,k,e)) partial_(x_(y,k+1,e)) log density
 = m/epsilon > 0,
```

and a spatial quadratic bond gives `c*epsilon>0` for the corresponding
cross-site coordinates.  All diagonal quadratic, scalar quartic, harmonic
split, and linear source terms have zero mixed derivative.

For an internal Q3 edge, set

```text
W(x,y) = lambda/4 * (x-y)^2 * (x^2+y^2).
```

The exact identity is

```text
partial_x partial_y W
 = -lambda/4 * ((x+y)^2+5*(x-y)^2) <= 0.
```

Since the density contains `exp[-epsilon W]`, its log mixed derivative is

```text
-epsilon*partial_x partial_y W
 = epsilon*lambda/4*((x+y)^2+5*(x-y)^2) >= 0.
```

Thus the entire finite-grid density is log-supermodular.  The Q3 prior is
nonradial, but its terms are within one spatial site and the sign calculation
uses no internal rotation symmetry.  The finite-dimensional MTP2 theorem and
its marginal/association closure therefore give

```text
E_(N,h)[F G] >= E_(N,h)[F] E_(N,h)[G]
```

for bounded coordinatewise-increasing grid functions `F,G`.

## 4. Order-preserving interpolation

Let `I_N` be periodic piecewise-linear interpolation.  On an interval with
`theta=(tau-k*epsilon)/epsilon`,

```text
(I_N x)(tau) = (1-theta)*x_(y,k) + theta*x_(y,k+1).
```

Both coefficients are nonnegative.  Hence `x<=x'` coordinatewise on the
grid implies `I_N x<=I_N x'` pointwise on every loop.  If `F` is a bounded
continuous pointwise-increasing functional on
`C_per([0,beta];R^8)^Lambda`, then `F o I_N` is an admissible increasing grid
function.  The finite-grid association inequality applies to all such
functionals.

The interpolation is also continuous in the sup norm.  The Gaussian
increment estimate and tightness from the covariance audits, together with
the quartic weight and the normalizer estimate from the weighted-law audit,
give

```text
I_N#(weighted grid law) => exact finite-volume loop law
```

at fixed `Lambda`, `beta`, and `h`.

## 5. Association in the loop limit

For bounded continuous increasing `F,G`, first add constants so that
`F_+=F+||F||_infty` and `G_+=G+||G||_infty` are nonnegative.  Covariance is
unchanged by these shifts, and `F_+G_+` is bounded, continuous, and increasing.
Applying finite-grid association to `F o I_N`, `G o I_N`, and
`(F_+G_+) o I_N`, then using weak convergence for each bounded continuous
functional, gives

```text
E_h[F G] >= E_h[F] E_h[G].
```

The constant-shift step is necessary: the product of two arbitrary
sign-changing increasing functions need not itself be increasing.

For coordinate products, let

```text
phi_R(t)=max(-R,min(t,R)),
F_R=phi_R(q_(y,e))+R,
G_R=phi_R(q_(y,f))+R.
```

Association for `F_R,G_R` is equivalent to association for the clipped
coordinates.  The source-uniform quartic lower bound and the normalizer
estimate give a uniform second-moment bound at fixed `Lambda`; hence
`phi_R(q_(y,e)) phi_R(q_(y,f))` converges in `L^1` to
`q_(y,e) q_(y,f)`.  Letting `R` tend to infinity proves the required
unbounded-coordinate covariance inequality.  This is a uniform-integrability
argument, not a consequence of weak convergence alone.

## 6. Zero-source Q3 consequences

At `h=0`, global inversion `q -> -q` gives `E[q_(y,e)]=0`.  Therefore the
coordinate covariance inequality yields

```text
E[q_(y,e) q_(y,f)] >= 0,       e != f.
```

For the cube graph `Q_3`, every vertex has degree three.  With

```text
S_y=sum_e q_(y,e)^2,
D_y=sum_{{e,f} in E(Q3)}(q_(y,e)-q_(y,f))^2,
```

the exact graph identity is

```text
D_y = 3*S_y - 2*sum_{{e,f} in E(Q3)} q_(y,e) q_(y,f).
```

The loop FKG covariance bound therefore gives `E[D_y] <= 3 E[S_y]`.  Also,
for `Q_y=8^(-1/2) sum_e q_(y,e)`,

```text
E[Q_y^2]
 = (E[S_y]+2*sum_(e<f)E[q_(y,e)q_(y,f)])/8
 >= E[S_y]/8.
```

These are the only FKG consequences used in the collective double-commutator
lower bound.  Q3 automorphism transitivity and spatial translation invariance
may be used to identify site/component variances, but no rotation-invariant
vector theorem is imported.

## 7. Source-direction boundary

Mixed derivatives do not depend on the sign of a linear source, so finite-grid
association holds for every fixed source in the declared compact interval.
The stronger stochastic monotonicity statement is used only for a source
direction with nonnegative components, such as
`u=(1,...,1)/sqrt(8)`.  No mixed-sign source monotonicity is asserted.

## 8. Adversarial checks

1. **The periodic temporal edge is duplicated for `N=2`.**  Its combined
   off-diagonal precision is still nonpositive; the proof uses `N>=3` for the
   limiting sequence and does not rely on the exceptional convention.
2. **A nonradial Q3 onsite term could break FKG.**  The exact sum-of-squares
   mixed-derivative identity gives the required sign for every field value.
3. **Interpolation could reverse order.**  Piecewise-linear coefficients are
   nonnegative, so coordinatewise grid order is preserved pointwise.
4. **Weak convergence proves unbounded coordinate association.**  False;
   clipping and a quartic uniform-integrability estimate are required.
5. **`F G` is always increasing when `F,G` are increasing.**  False for
   sign-changing functions; the nonnegative constant shifts are explicit.
6. **The graph-spectrum bound alone gives a collective lower bound.**  False;
   the collective projection uses the FKG nonnegative cross terms.

## 9. Remaining independent-audit obligations

* Match the precise finite-dimensional MTP2/association theorem and its
  integrability hypotheses in the bibliography-version source.
* Supply the constants in the source-uniform quartic moment estimate and show
  that they survive the clipped-product limit at fixed spatial volume.
* Check the exact KP Feynman--Kac topology and the interpolation covariance
  convergence used in the weak-limit step.
* Verify that the finite-volume zero-source symmetry and Q3 graph identity are
  used before, not after, the spatial thermodynamic limit.

P-06 remains **PROOF TEXT AND EXTERNAL AUDIT REQUIRED**.  No claim, tier,
manuscript, release, or PDF is created by this note.

## 10. Nonclaims and publication boundary

This audit proves no strict cusp, positive infrared zero mode, DLR
multiplicity, real-time dynamics, KMS state, ground state, gap, continuum
limit, physical-vacuum statement, Sector-A conclusion, or Pre-A conclusion.
PDF compilation, rendering, and visual review remain reserved for the final
content-frozen stage.
