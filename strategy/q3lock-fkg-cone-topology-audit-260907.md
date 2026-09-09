# FKG positive-cone topology lemma

Date: 2026-09-07. Exploration: EXP-001648. Task: T-054.
Status: T0, claim_bearing=false, internal proof repair only.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
PDF status: deferred.

## Question and repair

The continuous-loop FKG passage uses a Borel extension on the projective
tempered space (eq:tempered-metric). The earlier text stated closed-cone and
translation-invariant-metric hypotheses abstractly. This audit checks those
hypotheses for the actual space and records the repair in
`manuscript.tex`, Lemma `lem:positive-cone-topology`.

## Result

For `d_t`, convergence contains a local sup-norm term at every site. Therefore
a limit of pointwise nonnegative loops remains nonnegative, so the positive cone
is closed. Each metric summand depends only on a difference, so the metric is
translation invariant. If `K` is compact and `k_n+e_n` converges with
`k_n` in `K` and `e_n` in the cone, a convergent subsequence of `k_n` and
translation invariance force `e_n` to converge in the closed cone; hence
`K+E_+` is closed. It is upper by addition of another nonnegative loop.
The same elementary property holds for the finite-loop sup-metric space.

This closes the stated topological premise of the upper-set/Borel extension;
it does not by itself prove finite log-supermodularity, weak-limit FKG, the
source-window DLR passage, or the phase cusp. Those remain subject to A1--A23
and independent review.

## Adversarial checks

1. The local sup terms cannot be omitted: weighted L2 convergence alone would
   not preserve pointwise positivity.
2. Compactness of `K` is used to extract `k_n`; closedness of the cone alone
   does not make an arbitrary cone sum closed.
3. The lemma concerns the projective topology actually declared in the
   manuscript, not an unproved stronger Banach norm.
4. No finite diagnostic is treated as an external proof certificate.

Disposition: **INTERNAL TOPOLOGICAL SUBLEMMA REPAIRED; FKG AND PHASE REVIEW OPEN.**
No theorem tier, claim status, or PDF status changes.
