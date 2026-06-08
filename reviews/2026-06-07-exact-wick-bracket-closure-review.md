# 2026-06-07 -- exact-Wick bracket residual closure review

**Reviewer:** operator (Jusang Lee)
**Format:** evaluation summary -> per-document adversarial review.
**Verdict:** twoshell-anchored-bracket v1.0 ACCEPTED -- the substantive exact-Wick
obstruction is removed. ESTIMATOR-UPGRADE is at "nearly closed": keep OPEN only for
the bulk anchored continuum refinement + operator sign-off. No tier/gate change.

## Confirmed
- exact slogdet engine reused (Math432 neuter-import), reproduces recorded brackets
  to 5e-8.
- at r=0.219: min anchored dF over (A1,A2)!=(0,0) = +6.7e-4 > 0.
- near origin bracket = O(A^4) (|bracket|(0.005)=3.9e-8) -> anchored Hessian =
  diagonal (kappa_{110}=5.16, kappa_{200}=3.86, kappa_12=0).
- the off-diagonal exact-Wick bracket does NOT overturn the no-condensate.

## Adversarial points and actions
1. **Not a node-free bulk theorem.** The exact anchored bulk is an 11x11x3 GRID
   statement; near-origin is continuum (PD + O(A^4) bracket). Correct phrasing:
   "closed at grid + near-origin continuum grade", not "fully continuum-proved".
   ALREADY so labelled (status, section 4, footer). Confirmed; no change.
2. **M-grid {0.7,1.0,1.3} is sparse.** Weak attack: the anchored min sits at small
   A where the bracket is O(A^4)~1e-8, so an M-grid-hidden negative valley is
   unlikely. Defended as strong-evidence. Confirmed.
3. **Stale self-review (beta) in estimator-upgrade-knobs.** Section 4 + footer were
   updated, but the (beta) item still carried the old "global no-condensate only
   cited / Math432 grid evidence" framing. ACTION: replaced (beta) with the
   operator-recommended text -- "the two-shell exact-Wick bulk is still grid-grade;
   the bracket residual is evaluated at the B1 point and does not overturn
   positivity; only the bulk continuum refinement remains."

## Operator-recommended ledger wording (recorded)
single-shell controlled for {M, dI, amplitude grid}; two-shell diagonal surface
positive at r=0.219; corrected Hessian kappa_{110}=5.16, kappa_{200}=3.86,
kappa_12=0 (softer = {200}); exact-Wick anchored min +6.7e-4>0 on the bulk grid,
O(A^4) bracket near origin so the anchored Hessian = diagonal PD; the off-diagonal
bracket does not overturn the selection. Remaining = a curvature-chord continuum
bound on the exact anchored bulk surface; then closure is an operator decision.

## Operator verdict
"bracket obstruction removed; keep OPEN only for bulk anchored continuum refinement
+ operator sign-off." No new round directed.

## Credit
The grid-vs-continuum precision and the (beta) self-review fix are reviewer-directed.
