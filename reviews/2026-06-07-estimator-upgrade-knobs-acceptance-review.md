# 2026-06-07 — ESTIMATOR-UPGRADE knob-closure note acceptance review

**Reviewer:** operator (Jusang Lee)
**Format:** evaluation summary -> per-document adversarial review.
**Verdict:** estimator-upgrade-knobs v1.0 ACCEPTED, recorded as single-shell knob
closure + two-shell Hessian advance (NOT full ESTIMATOR-UPGRADE closure). One
minor fix applied; next round directed. No tier/gate change.

## Confirmed
- single-shell LAM/HEX/FCC/BCC: controlled-error against all named numerical knobs
  (M from enumerated v1.0; dI-refinement moves kappa by <0.1%; amplitude grid).
- curvature-chord continuum lower bound positive on every single-shell interval
  (LAM +8.80e-7 ... BCC +2.54e-7; M_max 126..629).
- two-shell {110}+{200} (0,0) Hessian positive-definite: kappa_12=0 (orthogonality),
  lambda_soft=kappa_BCC=5.116, lambda_{200}>0 (penalty C q0^4=0.214>0).
- full ESTIMATOR-UPGRADE: still OPEN.

## Adversarial points and actions
1. **curvature-chord is strong-evidence, not theorem-grade.** M_i is a local
   second-difference estimate of |dF''|, not a rigorous analytic upper bound, so
   the continuum bound is controlled-error / strong-evidence, not a T7
   interval-arithmetic theorem. ALREADY so labelled in the note (devil's-advocate
   alpha + the EVIDENCE-grade line). Confirmed; no change.
2. **two-shell GLOBAL no-condensate is not closed.** The note closes the two-shell
   (0,0) Hessian; the m31 tilted-valley GLOBAL statement only cites Math432 grid
   evidence. The residual is the 2D surface bound dF(A1,A2)>0 for all (A1,A2)!=(0,0)
   -- a 2D surface chord bound, not a 1D one. ALREADY named as the residual; gate
   stays OPEN. Confirmed.
3. **minor: section-3 numbering typo** "(ii) amplitude-grid / (ii) dI / (i)
   two-shell". ACTION: relabelled the three Method paragraphs (a)/(b)/(c) to remove
   the duplicate (ii) and the misleading (i); FORM-CHECK re-run.

## Recommended ledger wording (operator-provided, recorded)
For the single-shell readings the estimator-grade margins are controlled-error
w.r.t. the named knobs {M, dI, amplitude grid}: kappa_R>0 for every reading, the
dI-refinement moves kappa_R by <0.1%, and the curvature-chord lower bound is
positive on every single-shell amplitude interval. For the two-shell {110}+{200}
ensemble the (0,0) Hessian is positive-definite (kappa_12=0, lambda_soft=
kappa_BCC=5.116, lambda_{200}>0). The full ESTIMATOR-UPGRADE gate remains open
until the two-shell GLOBAL no-condensate is upgraded from grid evidence to a
continuum bound over the (A1,A2) surface.

## Operator verdict + next round
ESTIMATOR-UPGRADE: single-shell controlled-error subgate closed; two-shell (0,0)
PD; two-shell global continuum bound remains. NEXT = two-shell global continuum
no-condensate bound over (A1,A2). Directed: proceed with the next round.

## Credit
The strong-evidence-vs-theorem precision, the 2D-surface residual framing, and the
section-numbering fix are reviewer-directed.
