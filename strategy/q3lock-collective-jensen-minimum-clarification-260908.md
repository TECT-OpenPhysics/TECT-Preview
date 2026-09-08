# Q3LOCK collective Jensen minimum clarification

Date: 2026-09-08. Exploration: EXP-001674. Task: T-054.
Status: T0 proof-text repair; claim_bearing=false; PDF deferred.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.

## Finding

In the collective translation block, let
\[
 F(t)=\rho_L\bigl(U(q+t v)-U(q)\bigr).
\]
The translated-form Jensen argument gives (F(t)\geq F(0)=0) for every
real (t).  The polynomial (F) is finite because all coefficients of the
translation expansion are integrable under the fixed finite-volume Gibbs law.
The required conclusion is therefore only (F''(0)\geq0), obtained from the
local minimum at (t=0).  It is not correct or necessary to state that
(F''(t)\geq0) for every (t); the negative quadratic coefficient (r<0)
means that a global convexity assertion would not follow from the displayed
formula.

The manuscript now states the local-minimum conclusion explicitly and keeps
the differentiation separate from any differentiation of the heat trace under
an unbounded cubic perturbation.  The resulting (B_L=F''(0)) and
\(\rho_L(B_L)\geq0\) are unchanged.

## Adversarial checks

1. A test with (r<0) and (q=0) rejects the stronger claim of global
   nonnegative second derivative; the repaired sentence makes no such claim.
2. The Jensen inequality still supplies (F(t)\geq0) for all (t), so the
   local second-derivative conclusion is sufficient for the double-commutator
   lower bound.
3. The repair does not differentiate the Gibbs state or the heat trace; it
   differentiates the explicitly finite polynomial of integrable Gibbs
   coefficients.

## Boundary

This is a proof-text precision repair only.  It does not close A14--A17,
does not promote R-497, does not establish the collective inequality in the
infinite-volume limit, and does not change the external-review or deferred-PDF
requirements.

Next action: issue a fresh non-overwriting replay family and send the repaired
line to the independent mathematics reviewer for the full form/core and
Falk--Bruch passage.
