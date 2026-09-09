# Q3LOCK FKG cone-closure translation estimate

Date: 2026-09-07. Exploration: EXP-001672. Task: T-054.
Status: T0 proof-text clarification only; claim_bearing=false; PDF deferred.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.

## Question

Does the compact-plus-positive-cone closedness argument in the continuous-loop
FKG passage explicitly justify the step from `k_n+e_n -> x` and `k_n -> k` to
`e_n -> x-k` in the declared translation-invariant weighted metric?

## Finding

The manuscript's conclusion was already the intended one, but the phrase
"translation invariance then gives" compressed the required triangle estimate.
The proof text now displays

    d_t(e_n,x-k) <= d_t(k_n+e_n,x) + d_t(k_n+x-k,x) -> 0,

where the second term tends to zero because `k_n -> k` and the metric is
translation invariant.  The closedness of the positive cone then gives
`x-k` in the cone, so `x` is in the compact-plus-cone sum.  No hypothesis,
conclusion, limit order, or source law was changed.

## Boundary and adversarial checks

1. This is not a new proof of path-space FKG or a selected-limit theorem;
   A11 and A16 remain OPEN for signed review.
2. The estimate does not replace the measurable-extension, weak-limit,
   uniform-integrability, or source-tangent arguments.
3. The metric term `d_t(k_n+x-k,x)` is exactly the translation-invariant
   rewrite of `d_t(k_n,k)`; no unproved norm equivalence is introduced.
4. The repair changes manuscript bytes, so fresh, integrated, locator and
   completion checkpoints are required; no PDF is generated.

## Evidence and next gate

The fresh seven-audit checkpoint, non-importing algebra replay, independent
child replay, finite-form replay, integrated replay, and completion gate are
issued under the `fkg-cone-explicit` checkpoint family.  The next gate remains
an external line-by-line disposition of A1--A23 and the literature matrix,
followed by content/hash freeze.  The package remains T0,
`claim_bearing=false`, `UNFROZEN_CONTENT_REVIEW`, and PDF DEFERRED.
