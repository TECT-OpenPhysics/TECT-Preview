# Q3LOCK selected-limit FKG audit

Date: 2026-09-08. Exploration: EXP-001671. Task: T-054.
Status: T0, claim_bearing=false, internal finite/topological audit only.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
PDF status: deferred.

## Question

Do the displayed finite FKG signs, selected-limit covariance passage,
positive-cone approximation, zero-extension order, mixture warning, and
fourth-moment clipping estimates agree with the manuscript without silently
turning a finite diagnostic into a path-space or DLR theorem?

## Audit scope and method

The standard-library checker `verification/scripts/q3lock_fkg_selected_limit_audit.py`
performs the following bounded checks.

* It evaluates the temporal and spatial bond mixed derivatives, the Q3LOCK
  mixed derivative identity, and the vanishing mixed derivative of unary
  terms on rational fixtures.
* It replays the compact-product association diagnostic on an attractive
  binary cube, including upper-event covariance and conditional likelihood
  ratios.
* It constructs a small order-preserving sequence of attractive measures on a
  compact square and checks convergence of bounded continuous increasing test
  covariances and of the three expectations used in the weak-convergence
  passage.
* It checks the closed-upper-set distance approximation in the sup metric,
  finite compact-plus-cone upper sets, and the order-preserving zero extension
  used for selected spatial limits.
* It verifies the exact two-atom counterexample showing that an arbitrary
  mixture of associated states need not be associated.
* It evaluates the fourth-moment clipping bounds for coordinate products and
  first moments on finite weighted fixtures, and checks the parity-symmetric
  Q3 graph inequalities for ferromagnetic binary fixtures.

All checks are finite arithmetic or finite numerical diagnostics. No check
proves the infinite-dimensional measurable extension, a uniform integrability
theorem for the actual loop laws, the existence of the selected limits, or
association of arbitrary DLR mixtures.

## Finding

All registered assertions pass. No new local algebraic, order-theoretic, or
finite clipping defect is isolated in this pass. In particular, the sign in
the Q3LOCK mixed derivative, the upper-set approximation direction, the
mixture counterexample, and the fourth-moment product bound are internally
consistent on the declared fixtures.

This is not a signed proof audit. The manuscript still depends on acceptance
of the exact finite FKG theorem, the cutoff removal, the declared weighted
weak convergences in the selected spatial and source-tangent sequences, the
Polish-space measurable extension, and the actual uniform moment estimates.
Those dependencies remain open in A10, A11, and A16.

## Disposition

**INCONCLUSIVE INTERNAL AUDIT; FKG AND SELECTED-LIMIT REVIEW OPEN.**
No claim tier, theorem status, TECT sector, publication status, or PDF status
changes. The next gate is an external signed line-by-line mathematics review
of the finite-to-loop and selected-limit dependencies. Any repair must be
followed by a fresh manuscript/replay checkpoint before content freeze.

