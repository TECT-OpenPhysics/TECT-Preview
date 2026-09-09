# Q3LOCK upper-truncation resolvent repair audit

**Date:** 2026-09-07 UTC  
**Exploration:** EXP-001644  
**Task:** T-054  
**Status:** T0, claim_bearing=false, internal A1--A3 proof repair  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 / R-497  
**Paper PDF:** deferred until content review and final organization

## 1. Finding

The earlier finite-volume lemma said that the upper-truncated forms
`q_M=q_a+min(R_{a,h},M)` had a uniform bound in the full physical form norm.
That statement was too strong: the upper truncation removes the quartic coercive
term at large field amplitude, so only the harmonic form norm is uniformly
coercive before taking the cutoff limit.

This is a genuine proof-interface defect, not a cosmetic notation issue. It did
not change the finite envelope constants, but it invalidated the stated direct
justification if left unrepaired.

## 2. Repair

The manuscript now uses the following finite-volume argument.

1. The common residual lower bound gives `q_M >= q_a - V C_res`, so the
   resolvent minimizers have a uniform harmonic form bound after choosing
   `alpha > V C_res`.
2. The harmonic oscillator form embedding is compact in finite dimension; each
   subsequence therefore has a weak harmonic-form and strong L2 limit.
3. For every fixed cutoff `k`, monotonicity gives `q_k <= q_M`. Closedness and
   weak lower semicontinuity of the fixed-cutoff form give a bound for `q_k` at
   the limit. Monotone convergence in `k` then places the limit in the physical
   quartic form domain.
4. Minimality is passed by a two-sided variational inequality: the limsup of
   `F_M(v)` for a physical-domain test vector gives `F_h(v)`, while the fixed-k
   lower bounds and then `k -> infinity` give `F_h(u) <= liminf F_M(u_M)`.
   Uniqueness identifies the limit with the physical resolvent, and harmonic
   compactness upgrades subsequential convergence to full strong L2 convergence.

The proof no longer claims a uniform quartic bound for the upper-truncated
forms and does not rely on operator monotonicity of the exponential.

## 3. Adversarial checks

The finite audit now checks for the repair phrases and the explicit `F_M(u_M)`
variational passage, in addition to the graph-derived envelope constants,
hostile under-budget fixtures, monotone truncation and manuscript locators.
The audit remains finite algebra/provenance evidence; it is not an external
acceptance of the closed-form or semigroup theorem.

## 4. Disposition and boundary

This repair advances the internal A1--A3 proof interface but leaves A1--A3,
Simon applicability, kernel identification, endpoint continuity, all spatial
limits, A4--A23, external mathematics, literature review, claim tier and final
PDF gates OPEN. The previous result bytes remain immutable historical records.
No DLR phase, cusp, parity pair, TECT-sector status, KMS, ground-state,
continuum, physical-vacuum, cosmological or Yang--Mills conclusion follows.
