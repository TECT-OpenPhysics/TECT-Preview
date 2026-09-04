# Q3LOCK finite-grid FSS source-differentiation audit

**Status:** T0 proof-text audit; P-09 remains open pending independent review  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Purpose and boundary

The Q3LOCK infrared step needs a source normalization that survives the
time-grid limit.  This note writes the finite-dimensional
Froehlich--Simon--Spencer (FSS) application with the time-slice scaling shown
explicitly, differentiates the source inequality only after a finite-volume
uniform-integrability check, and records which statements still require an
independent proof audit.

The argument is at fixed spatial volume `Lambda_L`, fixed `beta`, and fixed
positive harmonic split.  It supplies no spatial thermodynamic limit by
itself, no strict cusp, and no DLR multiplicity.  In particular, a finite-grid
FSS inequality is not silently promoted to the continuous-loop statement.

## 2. Weighted finite-dimensional spin encoding

Let `epsilon=beta/N` and write the grid variable at site `y` and time slice
`k` as `x_(y,k) in R^8`.  Encode one complete time history at a spatial site
as

```text
s_y=(sqrt(epsilon)*x_(y,k))_(k=0,...,N-1) in R^(8N),
```

with the ordinary Euclidean dot product.  Thus

```text
s_y dot s_z = epsilon*sum_k x_(y,k) dot x_(z,k).
```

Put into a single-site prior `d lambda_N(s_y)` every factor that is local in
the spatial lattice: the temporal kinetic and harmonic terms, the Q3LOCK
onsite polynomial, the source-free local quadratic and quartic terms, and the
`3c/2` onsite term obtained by expanding the spatial difference square.  The
remaining spatial interaction is exactly

```text
exp[c*sum_<yz> s_y dot s_z].
```

At zero source the prior is even under `s_y -> -s_y`.  The quartic lower bound
after the harmonic split implies, for every fixed `N`,

```text
integral exp(alpha*|s|^2) d lambda_N(s) < infinity
```

for every finite `alpha`.  The constants in this moment statement may depend
on `N`; the FSS Gaussian-domination constant does not.

## 3. Reflection positivity and the FSS hypotheses

For a spatial reflection plane, the crossing factor is

```text
exp[-c*||a-b||^2/2]
 = exp[-c*||a||^2/2] exp[-c*||b||^2/2] exp[c*a dot b].
```

The last kernel is positive definite because

```text
exp[c*a dot b] = sum_(n>=0) c^n/n! * <a^(tensor n), b^(tensor n)>.
```

All temporal and Q3LOCK factors remain inside one spatial site prior, so no
radial or `O(8)` invariance is needed.  The finite-dimensional FSS theorem for
cubic nearest-neighbour boxes therefore applies to this `8N`-component prior.
Its Gaussian-domination constant is independent of the single-site measure,
the component count, and internal symmetry; the varying time-grid dimension
is consequently allowed only after the finite-`N` inequality has been proved.
The source paper's nearest-neighbour and periodic-box restrictions are kept
explicit; no general-lattice extension is used.

## 4. Source scaling and the finite-grid inequality

Let `a:Lambda_L -> R` satisfy `sum_y a_y=0` and let
`u=(1,...,1)/sqrt(8)`.  Insert the time-constant source

```text
weighted source j_y(k) = t*a_y*u,
standard-coordinate source eta_y
  = t*sqrt(epsilon)*(a_y*u)_(k=0,...,N-1).
```

The first line is the source in the weighted inner product
`<v,w>_N=epsilon*sum_(k,e) v_(k,e)w_(k,e)`.  After the encoding
`s_y=sqrt(epsilon)*(x_(y,k))_k` and the ordinary Euclidean dot product, the
second line is the same source.  Its pairing is therefore

```text
sum_y eta_y dot s_y
 = t*X_(N,L)(a),
X_(N,L)(a) = epsilon*sum_(y,k) a_y*(u dot x_(y,k)).
```

Writing `L_sp=D^*D` for the spatial graph Laplacian, the finite-grid FSS
inequality is therefore

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
 <= beta*t^2/(2*c) * <a,L_sp^(-1)a>.
```

The factor `beta` is not optional: it is the sum of the `N` slice weights
`epsilon`.  The inverse is used only on the zero-sum subspace, so the spatial
constant mode is never inverted.

At finite `N` the source moment is analytic at zero.  Differentiating the
displayed inequality twice gives

```text
Var_(N,L,0)(X_(N,L)(a))
 <= beta/c * <a,L_sp^(-1)a>.
```

Define the grid Duhamel matrix by

```text
Var(X_(N,L)(a)) = beta^2 * <a,D_(N,L) a>.
```

Then

```text
<a,D_(N,L)a> <= 1/(beta*c) * <a,L_sp^(-1)a>.
```

For a spatial Fourier mode `p != 0`, the graph eigenvalue is
`ell(p)=2*E(p)` with `E(p)=sum_i(1-cos(p_i))`.  The projected finite-grid
infrared estimate is consequently

```text
Dhat_(N,L)(p) <= 1/(2*beta*c*E(p)).
```

## 5. Passing the source inequality to the loop law

The weighted weak-limit result in
`q3lock-weighted-weak-limit-test-functional-audit-260904.md` gives weak
convergence only for bounded continuous functionals.  The source exponential
is unbounded, so the manuscript must add the following finite-volume
uniform-integrability step rather than invoke weak convergence directly.

For a compact range `|t|<=T`, use `|u dot x|<=|x|` and Young's inequality in
the form

```text
T*epsilon*|a_y|*|x_(y,k)|
 <= (A/2)*epsilon*|x_(y,k)|^4
    + C(A,T,|a_y|)*epsilon,
```

where `A` is the source-uniform quartic coefficient in the residual local
potential.  Multiplying by the grid Gibbs density absorbs the first term
against the quartic weight; the spatial difference term is nonpositive in the
action.  The same estimate with an additional polynomial factor controls
`|X_(N,L)(a)|^2 exp(T*|X_(N,L)(a)|)`.  The normalizer lower bound from the
Q3LOCK weighted-law audit is uniform in `N` at this fixed `Lambda_L`.
Thus the family of source exponentials and their second-derivative witnesses
is uniformly integrable.

The Gaussian tightness, compact Riemann-sum convergence, and the
Feynman--Kac identification then give, for each fixed `L`,

```text
E_(N,L,0) exp[t*X_(N,L)(a)] ->
E_(L,0) exp[t*X_L(a)],
Var_(N,L,0)(X_(N,L)(a)) -> Var_(L,0)(X_L(a)).
```

Passing the finite-grid inequality and its second-derivative identity to the
limit yields

```text
<a,D_L a> <= 1/(beta*c) * <a,L_sp^(-1)a>,
Dhat_L(p) <= 1/(2*beta*c*E(p)),   p != 0.
```

The result is a continuous-loop bound at fixed spatial volume.  It does not
use total-variation convergence and does not require differentiating a
spatial thermodynamic pressure at this stage.

## 6. Adversarial checks

1. **The time-grid dimension changes with `N`.**  This is allowed only because
   the FSS constant is dimension- and prior-independent; no uniform moment
   constant is attributed to FSS.
2. **The Q3LOCK prior is nonradial.**  It is entirely onsite in the spatial
   decomposition; the crossing kernel, not the prior, supplies reflection
   positivity.
3. **The zero spatial mode is inverted.**  The source is explicitly zero-sum,
   and all formulas use `L_sp^(-1)` on that subspace.
4. **A missing `beta` or factor two changes the theorem.**  The scaled-spin
   pairing contributes `N*epsilon=beta`, while `ell(p)=2E(p)`; both factors
   are shown before the Fourier bound.
5. **Weak convergence alone handles the exponential.**  This is false; the
   quartic Young estimate and the normalizer lower bound are required for
   uniform integrability.
6. **The spatial shift proves FSS by itself.**  This is not used.  The FSS
   theorem supplies the finite-grid inequality; the shift/majorant is only an
   integrability aid and cannot replace the theorem's reflection argument.

## 7. Remaining independent-audit obligations

* Match the exact theorem and numbering in the bibliography-version FSS source,
  including its prior-measure and periodic-box hypotheses.
* Write the quartic uniform-integrability constants and the fixed-`L`
  normalizer lower bound in the final proof, including all factors of `epsilon`.
* Verify that the finite-grid variance converges to the KP Duhamel covariance
  with the declared `D=(1/beta) integral C` normalization.
* Check the passage from dyadic periodic boxes to the EXP-000780 pressure
  sequence without claiming an unproved arbitrary-box extension.
* Obtain an independent mathematical audit of this source-differentiation
  passage before P-09 or P-12 is promoted.

P-09 therefore remains **PROOF TEXT AND EXTERNAL AUDIT REQUIRED**.  This note
does not register a claim, change a tier, create a manuscript, or generate a
PDF.

## 8. Nonclaims and publication boundary

No strict source cusp, positive zero mode, DLR multiplicity, real-time
dynamics, KMS state, ground state, gap, continuum limit, physical-vacuum
statement, Sector-A conclusion, claim registration, release, or publication
package is created here.  PDF compilation, rendering, and visual review are
reserved for the final content-frozen stage.

## 9. Primary source

J. Froehlich, B. Simon and T. Spencer, *Infrared Bounds, Phase Transitions and
Continuous Symmetry Breaking*, Communications in Mathematical Physics 50
(1976), 79--95, especially Theorems 2.1--2.3 and the discussion of the
constant's independence from the single-spin distribution, component count,
and internal symmetry:
<https://math.caltech.edu/SimonPapers/65.pdf>.
