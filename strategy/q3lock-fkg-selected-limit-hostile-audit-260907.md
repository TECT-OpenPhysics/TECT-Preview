# FKG selected-limit hostile audit

Date: 2026-09-07. Exploration: EXP-001649. Task: T-054.
Status: T0, claim_bearing=false, internal adversarial audit only.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
PDF status: deferred.

## Question

Does the repaired continuous-loop FKG section provide a complete route from
finite mesh association to bounded Borel association for the selected spatial
and source-tangent limits, under the topology actually declared in the
manuscript, without silently asserting association for arbitrary DLR mixtures?

## Audit scope and method

* Differentiate the temporal, spatial, source and Q3LOCK terms in
  `eq:log-supermodular`, checking the sign convention for the log density and
  the fact that unary/source terms have zero mixed derivative.
* Re-read the compact-product induction, likelihood-ratio monotonicity and
  growing-cube cutoff removal, including the integrability needed for the
  three bounded expectations.
* Check that periodic interpolation preserves the pointwise order and that
  weak convergence is invoked only for the bounded continuous tests `F`, `G`
  and `FG`.
* Check the closed positive cone, translation-invariant metric, compact-plus-
  cone closure, upper-set approximation, inner regularity and layer-cake
  extension in the declared tempered topology.
* Check the order of the selected spatial and source-tangent limits and the
  explicit counterexample showing why arbitrary mixtures are not admitted.

## Finding

No new local algebraic or topological defect was isolated in this pass. The
manuscript's repaired cone lemma supports the stated closed-upper-set
approximation, and the finite-to-continuous passage is connected to the
selected-limit passage with the intended order of limits. The explicit mixture
counterexample correctly prevents an overbroad claim about arbitrary DLR
mixtures.

This is not a signed proof audit. The route still depends on the exact finite
association theorem and cutoff-removal argument, the declared weighted weak
convergences for the selected sequences, and the measurable/Polish hypotheses
being accepted by an independent mathematician. Those dependencies remain
open in A11 and A16; the finite diagnostics do not discharge them.

## Disposition

**INCONCLUSIVE INTERNAL AUDIT; COMPLETE FKG AND SELECTED-LIMIT REVIEW OPEN.**
No claim tier, theorem status, TECT sector, publication status or PDF status
changes. The next gate is an external signed mathematics review that either
accepts each dependency or names a repair; after any repair the current
manuscript and integrated checkpoints must be rolled again.
