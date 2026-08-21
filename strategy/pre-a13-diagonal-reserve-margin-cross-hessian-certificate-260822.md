# R-183: diagonal reserve margin for the feedback-pulled cross-Hessian

## 1. Status and owner

R-183 / EXP-000898 is a T0 claim-nonbearing Lean cross-check. It starts from
the active negative cross block isolated by R-182 and computes the exact
diagonal reserve that a complete two-root owner must pay. It does not close
T-050, A13, Sector-A, physical-empty, or Pre-A.

## 2. Exact margin theorem

Let `a>0` be the magnitude of the active cross coefficient and let `d1,d2`
be diagonal reserves in the two original root coordinates. After subtracting
the cross block, the reserve matrix is

`M=[[d1-a,a],[a,d2-a]]`.

With the registered feedback matrix

`T=[[1,0],[1/2,1]]`,

the pulled matrix is

`T^T M T=[[d1-a+a+(d2-a)/4, a+(d2-a)/2],`
`          [a+(d2-a)/2,       d2-a]]`.

For `p=d1-a>0` and
`r=d2-a-a^2/p>=0`, the original quadratic has the exact completion

`p*x^2+2*a*x*y+(a^2/p+r)*y^2`
`  = p*(x+(a/p)*y)^2+r*y^2 >= 0`.

The feedback pullback is nonnegative because it evaluates this form at
`(x/2+y)` in the second coordinate. Conversely, testing the original form at
`x=-a/p,y=1` gives `q-a^2/p`; therefore no nonnegative owner can pass this
margin unless `q=d2-a>=a^2/p` when `p>0`.

For an isotropic reserve `d1=d2=d`, the exact decomposition is

`q_d=d/2*(x+y)^2+(d-2*a)/2*(x-y)^2`.

Thus the exact threshold is `d>=2*a`. The registered R-182 scale is `a=8`,
so the threshold is `d>=16`; at `d=15`, the relative-phase vector `(1,-1)`
has value `-2`, and its feedback coordinate is `(1,-3/2)`.

## 3. Verification lanes

`verification/lean/Tect/R183.lean` proves the matrix pullback, completion,
necessary witness, isotropic decomposition, threshold nonnegativity and
subthreshold negative fixture over `Rat`, with no `sorry`, `admit`, `axiom` or
`unsafe`. The primary SymPy lane derives `a`, the threshold, asymmetric
remainder, matrices and fixtures from the R-182 manifest. The independent lane
uses only stdlib `Fraction` arithmetic. The integrated lane checks source and
authority hashes, complete derived-value agreement, independent imports,
eight hostile mutations, append-only topology and stored freshness.

## 4. Adversarial review

* The theorem does not identify actual heat, forest, complement, returned-low,
  source or sextic terms with `d1,d2`. UPHELD.
* A finite reserve threshold is not a uniform production lower bound over
  roots, shells, cutoffs or feedback laws. UPHELD.
* The isotropic threshold cancels only the registered finite cross block; it
  does not sign the full A1/A7 owner or a physical action. UPHELD.
* The feedback matrix is invertible, but congruence does not create a missing
  source/sextic one-use estimate, matching, limit, Nelson or measure theorem.
  UPHELD.

## 5. Boundary and next obligation

R-183 turns the R-182 negative block into an exact reserve-budget test. The
next proof packet must map every actual diagonal and returned term into these
reserve variables and prove the threshold once, without duplicating a forest,
variance rebate, source term or sextic payment. Failure to meet the threshold
will be recorded as a scoped finite-owner margin obstruction, not promoted to a
global A13 or Sector-A no-go. No gate closure, tier change, new negative or
R-183 PDF is issued.

<a id="diagonal-reserve-margin"></a>
