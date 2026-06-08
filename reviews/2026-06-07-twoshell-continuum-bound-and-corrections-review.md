# 2026-06-07 -- twoshell-continuum-bound + correction-audit review

**Reviewer:** operator (Jusang Lee)
**Format:** evaluation summary -> per-document adversarial review.
**Verdict:** twoshell-continuum-bound v1.0 + the two corrections ACCEPTED; the
ESTIMATOR-UPGRADE residual is narrowed. Three adversarial points, all actioned.
No tier/gate change.

## Confirmed
- single-shell: controlled-error for M, dI, amplitude grid.
- two-shell (0,0) Hessian PD with corrected soft mode {200} (kappa_{200}=3.86 <
  kappa_{110}=5.16); both >0.
- operating-point correction: B1 is r=0.219, the cited Math432 ran at r=0.005.
- two-shell DIAGONAL global no-condensate at r=0.219: min +3.9e-5>0, 2D
  curvature-chord LB +1.2e-4>0; evaluator validated vs Math432 to 1.6e-7.

## Adversarial points and actions
1. **Diagonal is not exact anchored.** dF_anchored = dF_diag + bracket, bracket<0,
   so diagonal positivity does not imply anchored positivity; the exact-Wick
   bracket bound at r=0.219 is required. ACTION (this turn): twoshell-anchored-
   bracket v1.0 -- with the EXACT slogdet engine (Math432 neuter-imported,
   validated to 5e-8), min anchored over (A1,A2)!=(0,0) = +6.7e-4>0 at r=0.219; the
   bracket is O(A^4) near origin so the anchored (0,0) Hessian = diagonal (PD). The
   off-diagonal bracket does NOT overturn the no-condensate. Residual narrowed to a
   bulk-anchored continuum refinement.
2. **estimator-upgrade-knobs internal wording still conflicts.** Section 4 + footer
   still said "two-shell global continuum bound / grid evidence". ACTION: relabelled
   to point to the dedicated two-shell notes and to state the current residual
   (exact-Wick anchored established; bulk-anchored continuum refinement remains).
3. **M-grid minimisation is strong-evidence, not theorem-grade.** Accepted; both
   notes carry the strong-evidence grade.

## Operator-recommended ledger wording (recorded)
single-shell controlled w.r.t. {M, dI, amplitude grid}; two-shell {110}+{200}
Hessian PD with kappa_{110}=5.16, kappa_{200}=3.86, kappa_12=0 (softer = {200});
diagonal two-shell no-condensate at r=0.219 positive (continuum, strong-evidence);
the gate remains open only for the exact-Wick bracket -- now CLOSED at grid +
near-origin continuum by twoshell-anchored-bracket v1.0; remaining = bulk-anchored
continuum refinement.

## Operator verdict
"nearly closed; final residual = exact-Wick bracket continuum bound at r=0.219."
This turn closes that bracket (grid + near-origin continuum); only the bulk
node-free refinement + operator sign-off remain.

## Credit
The diagonal-vs-anchored distinction, the wording-remnant catch, and the
strong-evidence grading are reviewer-directed.
