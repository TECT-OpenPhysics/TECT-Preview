# EXP-001054 — multivariate energy-weighted Q3 source bound

## Status

This is a T0, claim-nonbearing pointwise QFT interface checkpoint.  It does
not change claim tiers, result or negative ledgers, common alpha, or production
ownership.

Primary: 209/209 PASS  
Independent Fraction lane: 208/208 PASS  
Integrated lane: 26/26 PASS  
Lean: R236 PASS

Run artefacts:

- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-multivariate-energy-weighted-source-bound/primary.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-multivariate-energy-weighted-source-bound/independent.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-multivariate-energy-weighted-source-bound/integrated.json`

## Exact bound

Reconstruct the actual Q3 source and its source-at-neighbor orientation from
the registered potential.  Every monomial has field degree
\(i+j\le3\) in \(q,v\), and source degree at most four in \(a\).  With

\[
A(q,v)=1+q^4+v^4,\qquad |a|\le1/4,
\]

each monomial obeys

\[
|q|^i|v|^j|a|^k
 \le (1/4)^k A(q,v)^{3/4}.
\]

The exact coefficient triangle gives the same constant in both orientations:

\[
|P(q,v,a)|\le \frac{122099}{35840}A(q,v)^{3/4},
\qquad
|P_{\rm reverse}(q,v,a)|\le \frac{122099}{35840}A(q,v)^{3/4}.
\]

The primary and independent lanes recompute this coefficient sum from the
polynomial rather than importing the constant.  They also check the equivalent
fourth-power inequality on all 98 exact grid points per orientation.

## QFT boundary

This is a genuine multivariate commuting scalar weighted interface, stronger
than the EXP-001053 one-variable slice.  It still does not prove that the
canonical Q3 Hamiltonian supplies a common invariant operator domain, that the
weighted seminorm is submultiplicative for histories, or that the bound is
uniform through volume exhaustion.

The remaining QFT route is therefore:

1. identify the actual energy operator and common core;
2. promote this pointwise bound to a domain/graph estimate for both source
   orientations;
3. prove the weighted product and factorial spatial-incidence recurrence;
4. only then attempt exhaustion, common alpha, OS/KMS or GNS reconstruction,
   and the gap/continuum gates.

## Adversarial review

- The all-real conclusion comes from the coefficient majorant and degree bounds;
  the 98-point grid is an exact self-test, not the proof of all-real control.
- Center and reverse orientations are reconstructed separately and checked
  separately.
- The source restriction \(|a|\le1/4\) is explicit; no unrestricted amplitude
  is inferred.
- This is a pointwise commuting estimate, not an unbounded-operator,
  common-core, or central-context theorem.
- The constant \(122099/35840\) is recomputed in both arithmetic lanes.
- R236 checks exact coefficient and orientation fixtures only.
- No factorial incidence, first passage, exhaustion, common alpha, KMS/OS,
  GNS gap, continuum, C6, Sector A, Pre-A, or TECT production result follows.
- No `heat_root_incidence` or A1/R-192 production owner is supplied.

## Next gate

Connect the pointwise majorant to the actual Q3 common energy domain and prove
a multiplicative weighted history estimate before attempting the factorial
spatial-incidence and common-alpha gates.
