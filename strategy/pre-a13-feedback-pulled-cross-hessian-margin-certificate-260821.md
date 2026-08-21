# R-182 certificate: feedback-pulled cross-Hessian margin

## 1. Status and owner

R-182 / EXP-000897 is a T0 claim-nonbearing Lean cross-check.  It combines
the actual active R-178 cross-owner coefficient with the R-181 finite feedback
matrix.  It does not close A13, T-050, Sector-A, physical-empty, or Pre-A.

## 2. Exact finite calculation

At the registered active phase, R-178 has field coefficient `2`, current
coefficient `3`, and root weights `w1=1`, `w2=2`.  The phase Hessian coefficient
is therefore `-(2+3*1*2)=-8`, giving

`H=[[-8,8],[8,-8]]`.

R-181 supplies `T=[[1,0],[1/2,1]]`.  The exact congruence is

`T^T H T=[[-2,4],[4,-8]]`.

The two quadratic forms are `-8*(x-y)^2` and `-2*(x-2*y)^2`.  The fixture
`(x,y)=(0,1)` gives `-8` before and after the feedback pullback, and the
pulled matrix has eigenvalues `-10` and `0`.

## 3. Verification lanes

The primary lane derives the coefficient, matrices, factorizations, eigenvalues
and fixture from R-178/R-181 manifests before compiling the pinned Lean source.
The independent lane uses only stdlib `Fraction` arithmetic and exact 2 by 2
matrix multiplication.  The integrated lane checks hashes, theorem markers,
Lean escape-token absence, independent imports, complete derived-value
agreement, eight hostile mutations, and formal append-only topology/freshness.

## 4. Adversarial review

* This negative cross block is not the complete production Hessian.  UPHELD;
  diagonal heat, forest, low, source and sextic terms are still uninserted.
* Congruence through a finite feedback map does not create a production spatial
  response or a uniform mixed-Gram envelope.  UPHELD as a scope boundary.
* The zero eigenvalue is the common phase direction; the negative eigenvalue is
  only a relative-phase margin requirement, not a physical instability claim.
  UPHELD.
* No regulator, matching, thermodynamic, continuum, physical-empty, Sector-A,
  or Pre-A statement follows from this finite calculation.  UPHELD.

## 5. Reusable conclusion and boundary

R-182 identifies the exact negative cross margin that the complete owner must
pay once: the R-181 feedback block does not erase it. The next theorem must
add every diagonal and returned-low/source/sextic owner before asserting any
sign. R-102, R-125, R-063, source/sextic one-use, finite collar, T-050, A13,
matching, the absolute anchor, Nelson, measure, physical-empty, removal,
continuum limits, Sector-A and Pre-A remain open. No R-182 PDF is issued.

<a id="pulled-cross-hessian"></a>
