# R-388 state-weighted kinetic resolvent corridor

## Result-first boundary

R-388 is a T0, claim-nonbearing finite checkpoint under EXP-001231.  It
tests a new route after the R-387 kinetic isolation: instead of asking for a
cutoff-uniform operator norm of `K=[B,[T,A_z]]`, measure the same finite target
in the two-sided Gibbs seminorm
`N_beta(X)^2=Tr(rho_beta X^*X)+Tr(rho_beta XX^*)`, with
`rho_beta=Z^(-1) exp(-beta H)`.  The sampled corridor is the parameter region
`beta >= 1/2`, `eta >= 1`, where the late cutoff ratio is at most one on the
declared grid.  This is a finite corridor candidate and a stress test, not a
uniform estimate or a replacement for the common algebra norm.

## Finite verification

The primary and non-importing independent lanes rebuild the V=2 edge model at
cutoffs `d=3,4,5,6,8,10,12,16,20,24`, for both sites, both resolvent
imaginaries `eta=1/2,1`, both adjoint seeds and four beta values
`1/4,1/2,1,2`.  They cover 80 seed rows and 320 weighted rows.  The primary
lane passes `409/409` assertions, the independent lane passes `404/404`, and
the integrated verifier passes `44/44`.

The exact derived controls are:

| quantity | value |
|---|---:|
| raw operator-norm growth ratio (d=24 / d=3) | `616.8263791895753` |
| maximum raw operator norm | `769.7929363619684` |
| maximum two-sided weighted norm | `24.60012282810548` |
| late ratio, beta=1/2, eta=1 | `0.6231820763515571` |
| late ratio, beta=1, eta=1 | `0.6728818039994496` |
| late ratio, beta=2, eta=1 | `0.8705457144035674` |
| late ratio, beta=1/4, eta=1/2 | `2.015532296066202` |
| late ratio, beta=1/4, eta=1 | `1.50229981401046` |

Thus the finite data separate a strongly cutoff-growing raw operator stress
from a narrower Gibbs-weighted corridor, while the lower-beta or lower-eta
controls grow instead of entering that corridor.  Primary and independent
numeric fields agree within `7.958078640513122e-13`.

## Hostile and Lean checks

The hostile lane replaces the coordinate resolvent by a momentum resolvent.
The coordinate commutator remains at roundoff (`3.785481597218718e-14` max),
whereas the wrong momentum commutator has minimum residual
`1.0355377554099876`, above the `1.0e-7` threshold, so the mutation is
rejected.  `verification/lean/Tect/R388.lean` compiles with
`lake env lean Tect/R388.lean`; it checks the Jacobi reduction, the
kinetic-coordinate isolation implication and the finite-scope marker.  Lean
does not encode the matrices, Gibbs traces or any limit.

## Adversarial review

1. **Topology substitution.**  Raw operator norms and Gibbs seminorms are
   reported separately.  A bounded weighted row is not relabelled as an
   operator-norm bound.
2. **Parameter debt.**  The corridor is stated only on the sampled
   `beta >= 1/2`, `eta >= 1` grid; all lower values remain outside stress
   controls.
3. **Cutoff inference.**  Dimensions 3 through 24 are bounded oscillator
   truncations.  The raw growth is a route stress, not a divergence theorem.
4. **Observable class.**  The momentum-resolvent mutation breaks the
   coordinate commutator anchor and is quantitatively separated.
5. **QFT promotion.**  No beta/eta independence, shell summability, domain,
   Cook/common-alpha, OS/KMS/GNS, gap, continuum, C6, Sector-A or Pre-A claim
   is promoted.

## Decision and next gate

R-388 advances the anchored route by identifying a testable state-weighted
   corridor in which the isolated kinetic target is less cutoff-sensitive
   than its raw operator norm.  The next analytic gate is a fixed-parameter
   BKM/graph estimate on an explicitly invariant resolvent/form core, with
   constants tracked by boundary shell, source, volume and exhaustion shape.
   The proof must then test whether the estimate can be made independent of
   beta and eta and whether the shell coefficients are l1-summable.  If either
   independence or summability fails, the precise failure will retire only
   this corridor route and leave the other Q3LOCK routes intact.

No negative result, tier change or proof-note PDF is issued.

**Proven in:** [manifest](pre-a-cp1-st8-q3lock-state-weighted-kinetic-resolvent-corridor-finite-checkpoint-manifest.json), [primary script](../codes/foundations/pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint.py), [independent script](../codes/foundations/pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint_independent.py), [hostile script](../codes/foundations/pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint_hostile.py), [integrated verifier](../codes/foundations/pre_a_cp1_st8_q3lock_state_weighted_kinetic_resolvent_corridor_finite_checkpoint_verify.py), [Lean entrypoint](../verification/lean/Tect/R388.lean), [scope note](../claims/C6-SPACETIME-SIGNATURE/notes/state-weighted-kinetic-resolvent-corridor-finite-checkpoint-boundary-260830.md), and saved run artefacts.
