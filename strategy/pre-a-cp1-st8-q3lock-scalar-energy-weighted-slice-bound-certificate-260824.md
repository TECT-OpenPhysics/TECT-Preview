# EXP-001053 — scalar energy-weighted Q3 slice bound

## Status

This is a T0, claim-nonbearing scalar QFT interface checkpoint.  It does not
change claim tiers, result or negative ledgers, common alpha, or production
ownership.

Primary: 17/17 PASS  
Independent Fraction lane: 14/14 PASS  
Integrated lane: 23/23 PASS  
Lean: R235 PASS

Run artefacts:

- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-scalar-energy-weighted-slice-bound/primary.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-scalar-energy-weighted-slice-bound/independent.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-scalar-energy-weighted-slice-bound/integrated.json`

## Exact scalar estimate

For the actual Q3 source on the declared slice \(v=0\), \(a=1/4\),

\[
P_0(q)=\frac{51}{140}q^3-\frac{153}{1120}q^2
       +\frac{2291}{2240}q-\frac{4531}{35840}.
\]

Set \(A(q)=1+q^4\).  Every power in the slice has degree \(k\le3\), and for
every real \(q\),

\[
|q|^k\le A(q)^{3/4},\qquad k=0,1,2,3.
\]

The coefficient triangle therefore gives the all-real scalar inequality

\[
|P_0(q)|\le C A(q)^{3/4},
\qquad
C=\left|\frac{51}{140}\right|+left|\frac{153}{1120}\right|
 +\left|\frac{2291}{2240}\right|+left|\frac{4531}{35840}\right|
 =\frac{59139}{35840}.
\]

The scripts additionally check the equivalent fourth-power inequality at
\(q=0,1,2,4,8,32\) using exact rational arithmetic.  Those samples are
self-tests only; the all-real statement comes from the coefficient-majorant
argument above.

## QFT boundary

This closes a scalar weighted interface that matches the cubic growth found in
EXP-001052.  It does not construct the Q3 common-core operator, prove domain
invariance, or establish the full multivariate estimate.  The candidate weight
is a route target, not a declaration that the canonical finite-volume energy
has already been identified with \(1+q^4\).

## Adversarial review

- The all-real estimate is attributed to the coefficient triangle and elementary
  power inequalities; finite samples are not substituted for it.
- The result is restricted to \(v=0,a=1/4\); no multivariate estimate is
  inferred.
- A scalar majorant is not called an operator/domain theorem.
- \(A(q)=1+q^4\) is a matching candidate, not the canonical full Hamiltonian.
- \(C\) is recomputed from exact coefficients in two independent arithmetic
  lanes.
- R235 checks rational identities only, not real-power domains or dynamics.
- No factorial incidence, first passage, exhaustion, common alpha, KMS/OS,
  GNS gap, continuum, C6, Sector A, Pre-A, or TECT production result follows.
- No `heat_root_incidence` or A1/R-192 production owner is supplied.

## Next gate

Lift this scalar majorant to the multivariate Q3 source on a declared common
energy domain, preserving both source orientations, and then test the
factorial spatial-incidence estimate.
