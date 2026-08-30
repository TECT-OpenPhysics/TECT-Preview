# R-437 -- fixed-support cross-cutoff boundary

`R-437 / EXP-001282` is a T0, claim-nonbearing finite audit of the
threshold-four support rule used by the R-435 and R-436 interval authorities.
It asks whether the unchanged d=17 core can be reused at d=18 when the
volume, beta, orientation, row kind and emission ordinal are held fixed.

## Exact finite scope

- volume `V=2`, beta `8`, right orientation;
- unconditional one-site marginal, emission ordinal `0`;
- d=17 parent `R-435` and d=18 parent `R-436`;
- threshold `4`, crossing index `4`;
- fixed support source: the d=17 core indices `4..12`;
- directed interval threshold assertions from the two hash-pinned parent
  primary runs, not rounded point values.

For d=17, index `4` is in the core and its directed phi interval is

`[2.928582137842666842328379942374782260821356965438242614347658772652559683976254399565,
 2.928582137842666842328379942374793763899593365995396958706748597526637672297939680216]`.

For d=18, index `4` is in the tail and its directed phi interval is

`[4.016145184038902632538356548209393899600440870692488949841237941696776136410376441,
 4.016145184038902632538356548209432108173973591163820303164228876431706984404931606871]`.

The primary lane passes `14/14`, the non-importing independent control passes
`9/9`, the hostile lane rejects `8/8` mutations, and the integrated verifier
passes `15/15`. Lean `R437.lean` compiles. The strict ordering is

`d17 upper < 4 < d18 lower`.

## Decision

The unchanged fixed d=17 support is rejected as a route-local uniformity
strategy: index `4` crosses from core to tail between these two finite
cutoffs. This does **not** reject an increasing-core rule, a different
cutoff-dependent support, or a full-sector argument. No new negative-result
card or tier change is warranted.

## Assumptions

1. R-435 and R-436 are the active hash-pinned interval authorities for the
   same finite row contract.
2. Threshold status is read from directed interval endpoints, with no
   rounding or post-selection.
3. A single crossing rejects only unchanged fixed-support reuse.
4. The audit is finite and claim-nonbearing.

## Missing assumptions and next gate

- a predeclared increasing-core rule;
- a cutoff-, volume-, phase- and exhaustion-uniform tail modulus or a
  full-sector completeness theorem;
- a common unbounded Q3 core, history transfer and OS/KMS/GNS reconstruction;
- a physical reference and any Yang--Mills interpretation.

The next gate is an owner-approved increasing-core/tail-modulus construction
checked before further cutoff evaluations. Until that is supplied, the
fixed-support route cannot be used for a uniform conclusion.

## Devil's-advocate review

- **Parent authority mismatch:** V, beta, orientation, row kind, ordinal and
  threshold are compared from both manifests and runs. **DISMISSED-FINITE.**
- **Interval-direction error:** the d=17 upper endpoint is below four and the
  d=18 lower endpoint is above four; no rounded estimate is used.
  **DISMISSED-FINITE.**
- **Index/split bookkeeping error:** both primary and independent lanes check
  the same index and the distinct core/tail splits. **DISMISSED-FINITE.**
- **Overgeneralization:** the manifest explicitly leaves increasing-core and
  full-sector routes open. **UPHELD-OPEN boundary.**
- **Physical promotion:** no common core, physical reference, limit theorem,
  or Yang--Mills map is present. **UPHELD-OPEN.**

## Non-claims

This certificate proves no theorem that every core rule fails, no increasing
core or tail modulus, no common core or GNS gap, no continuum or physical
sector result, and no C6, Sector-A, Pre-A, Yang--Mills or mass-gap statement.

**Proven in:** [R-437 manifest](pre-a-cp1-st8-q3lock-fixed-support-cross-cutoff-boundary-manifest.json),
[primary run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-fixed_support_cross_cutoff_boundary/primary.json),
[independent run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-fixed_support_cross_cutoff_boundary/independent.json),
[hostile run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-fixed_support_cross_cutoff_boundary/hostile.json),
[integrated run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-fixed_support_cross_cutoff_boundary/integrated.json),
and [Lean R437](../verification/lean/Tect/R437.lean).
