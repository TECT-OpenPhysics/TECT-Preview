# EXP-001051 — Q3 operator-evaluation map contract

## Status

This is a T0, claim-nonbearing QFT interface checkpoint.  It does not change
any claim tier, result ledger, negative-result registry, common-alpha status,
or production-kernel ownership.

Primary: 34/34 PASS  
Independent Fraction lane: 33/33 PASS  
Integrated lane: 25/25 PASS  
Lean: R233 PASS  

Run artefacts:

- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-operator-evaluation-map-contract/primary.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-operator-evaluation-map-contract/independent.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-operator-evaluation-map-contract/integrated.json`

## Question

The preceding EXP-001050 coefficient calculation gives the actual shifted Q3
source polynomial a formal weighted l1 norm

\[
B=1382807/7168
\]

in both spatial orientations.  The unresolved issue is whether that formal
number controls an operator source history.  This checkpoint separates the
exact sufficient interface from the invalid inference that the coefficient
array controls an operator without an explicit realization.

## Conditional map contract

Let \(D\) be a common invariant core for every ordered monomial in the source
and every product used by the history.  Assume that the operator seminorm on
\(D\) is homogeneous and submultiplicative, that the evaluation \(\Phi\) is
linear on the finite coefficient span, and that it is multiplicative for the
ordered source product.  The required generator bounds are

\[
\|\Phi(q)\|\le 4,\qquad
\|\Phi(v)\|\le 8,\qquad
\|\Phi(a)\|\le 1/4.
\]

The triangle inequality and submultiplicativity then give, for a polynomial
\(p=\sum c_{ijk}q^iv^ja^k\),

\[
\|\Phi(p)\|
 \le \sum |c_{ijk}|4^i8^j(1/4)^k
 =\|p\|_{(4,8,1/4)},
\]

and multiplicativity gives

\[
\|\Phi(p_1)\cdots\Phi(p_n)\|
 \le \prod_{r=1}^{n}\|p_r\|_{(4,8,1/4)}.
\]

Applying this contract to the EXP-001050 source polynomial would supply the
formal \(B^n\) word envelope.  It is a conditional admission rule, not a
construction of the actual Q3 common core.

## Finite checks

The primary SymPy and independent Fraction lanes evaluate both orientations
at all eight sign points formed from the declared radii.  Every value is at
most \(B\) in absolute value, and lengths one through four satisfy the
corresponding \(B^n\) product bound.  The Lean R233 entry checks the exact
rational bounded value, positivity of the product fixtures, and the boundary
witness.

The same polynomial evaluated at the test point

\[
(q,v,a)=(32,0,1/4)
\]

has value

\[
84794793/7168>B.
\]

This point violates the declared generator radius \(|q|\le4\).  It therefore
rejects only the coefficient-only inference: the formal coefficient norm does
not choose or bound an operator representation by itself.  The witness is not
identified with the physical Q3 representation and is not a Q3 no-go.

## Adversarial review

- The coefficient norm is never called an unbounded-operator norm; the map
  contract is stated explicitly.
- Common-core invariance and multiplicativity are hypotheses, not outputs of
  the finite sign fixture.
- Center and source-at-neighbor orientations use their own radii and are
  checked independently.
- The radius-violating witness rejects only missing generator bounds and is
  not promoted to a physical counterexample.
- The product estimate uses submultiplicativity only after the multiplicative
  evaluation assumption is declared.
- R233 compiles exact rational fixtures only; it does not prove domains,
  closures, or thermodynamic limits.
- No factorial incidence, spatial first-passage, exhaustion, common alpha,
  KMS/OS reconstruction, GNS gap, continuum, C6, Sector A, or Pre-A result is
  inferred.
- No `heat_root_incidence` or A1/R-192 production owner is supplied.

## Boundary and next gate

Closed here: a precise conditional coefficient-to-operator admission contract,
finite bounded orientation tests, a finite product consequence, and a
coefficient-only non-implication boundary.

Still open: an actual Q3 common-core realization with domain invariance and
uniform generator bounds; the factorial spatial incidence bound; exhaustion
Cauchy convergence; common alpha; and all QFT reconstruction, gap, continuum,
C6, Sector A, Pre-A, and TECT production-owner gates.

Next gate: construct the actual Q3 common-core map or prove a Q3-specific
energy/domain estimate that verifies the contract, then audit the factorial
spatial incidence independently.
