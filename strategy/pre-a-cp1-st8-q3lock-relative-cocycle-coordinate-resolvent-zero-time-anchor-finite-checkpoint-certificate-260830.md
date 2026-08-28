# R-386 coordinate-resolvent zero-time commutator anchor

## Result-first boundary

R-386 is a T0, claim-nonbearing finite interface checkpoint under
EXP-001229.  It adds a new order-of-operations to the relative-cocycle route:
choose a coordinate resolvent before estimating the boundary interaction.  A
Q3 bond addition is a polynomial in commuting position coordinates, so its
commutator with that resolvent vanishes at time zero.  The resulting quadratic
time behavior is tested, not promoted to a uniform Cook estimate.

## 1. Anchor identity

For an actual bond prefix write `H_prime=H+B`, where

`B=c/2*(q_x-q_y)^2 + lambda/4*(q_x-q_y)^2*(q_x^2+q_y^2)`.

For every site `s` and nonzero `eta`, take
`A_z=(i eta I-q_s)^(-1)` and set

`Delta(t)=alpha_(H_prime,t)(A_z)-alpha_(H,t)(A_z)`.

Because all position-coordinate copies commute on the finite tensor product,
`[B,A_z]=0` for both `A_z` and `A_z^*`.  Thus

`Delta'(0)=(i/hbar)[B,A_z]=0`.

Expanding the second derivative only after this exact zero commutator gives

`Delta''(0)=-(1/hbar^2)[B,[H,A_z]]`.

The modular diagnostic `delta_H Delta(t)=(i/hbar)[H,Delta(t)]` has the same
zero first variation at time zero.  This is the proposed gain: the first
boundary insertion is removed algebraically, leaving one nested commutator to
be controlled by a future energy/BKM estimate.

## 2. Finite verification

The primary lane passes `2025/2025` assertions and the independent,
non-importing lane passes `2022/2022`.  Both cover the V=2 edge and V=4
square, both split orders, every actual bond prefix, every translated site,
both resolvent imaginary parts, both adjoint seeds and both beta values.  The
grid contains 288 state-weighted contexts, 144 seed rows, 10 bond prefixes and
1152 finite dynamic rows.  The integrated verifier passes `51/51` and Lean
R386 compiles.

The primary maxima are:

| quantity | maximum |
|---|---:|
| zero commutator residual | `2.317703490729531e-16` |
| first-variation residual | `1.259956570249438e-10` |
| second-variation finite-difference residual | `6.238635588734805e-07` |
| second-variation reduction residual | `4.232440506926493e-15` |
| modular first-variation residual | `3.6054124684301573e-10` |
| two-sided dynamic norm | `0.07193681804737587` |
| dynamic norm divided by `t^2` | `0.6576383064349549` |

The independent maximum fields agree within `1.4676852113146837e-07`, below
the manifest agreement tolerance `1.0e-6`.  The hostile lane adds the
manifest momentum mutation `B+(1/4)p_s`; its minimum commutator residual is
`0.279128784747792`, so the coordinate-only anchor is rejected for that
mutation above the `1.0e-7` threshold.

## 3. Adversarial review

1. **Interaction class.**  The anchor is asserted only for position-only bond
   additions.  Onsite kinetic terms and momentum mutations are not silently
   included in the commuting class.
2. **Resolvent inverse.**  Both `A_z` and its adjoint are tested at nonzero
   imaginary parameters; no real-axis inverse is used.
3. **Derivative convention.**  The central finite difference is compared with
   the exact commutator difference, and the second derivative is compared
   first with the full nested expansion and then with the reduced expression.
4. **Orientation.**  Forward and reverse term orders and both time signs are
   retained.  The hostile momentum mutation produces a non-roundoff failure.
5. **Finite boundary.**  The oscillator matrices are bounded.  No uniform
   quadratic remainder, form-domain theorem, or infinite-dimensional Cook
   integral follows from the finite `Delta(t)/t^2` diagnostic.
6. **Modular topology.**  The modular row is a finite reference-H commutator,
   not a phase-local BKM or strong-star estimate.
7. **Promotion firewall.**  Shell summability, all uniformities, common alpha,
   OS/KMS/GNS, gap, continuum, C6, Sector-A and Pre-A remain open.

## 4. Decision and next gate

R-386 advances the R-385 route by identifying a concrete coordinate-resolvent
subfamily with no first-order boundary insertion.  The next analytic step is
to bound the remaining nested commutator `[B,[H,A_z]]` and its modular version
in a phase-local BKM norm with constants uniform in source, cutoff, volume and
shape.  If a summable shell coefficient survives, integrate the anchored
relative cocycle by Cook; if not, record the failure for this anchored route
only.  The finite quadratic ratio is evidence of the decomposition, not a
uniform rate.

No negative result, tier change, or proof-note PDF is issued.  All
thermodynamic and QFT flags remain open.

**Proven in:** [manifest](pre-a-cp1-st8-q3lock-relative-cocycle-coordinate-resolvent-zero-time-anchor-finite-checkpoint-manifest.json), [primary script](../codes/foundations/pre_a_cp1_st8_q3lock_relative_cocycle_coordinate_resolvent_zero_time_anchor_finite_checkpoint.py), [independent script](../codes/foundations/pre_a_cp1_st8_q3lock_relative_cocycle_coordinate_resolvent_zero_time_anchor_finite_checkpoint_independent.py), [hostile script](../codes/foundations/pre_a_cp1_st8_q3lock_relative_cocycle_coordinate_resolvent_zero_time_anchor_finite_checkpoint_hostile.py), [integrated verifier](../codes/foundations/pre_a_cp1_st8_q3lock_relative_cocycle_coordinate_resolvent_zero_time_anchor_finite_checkpoint_verify.py), [Lean entrypoint](../verification/lean/Tect/R386.lean), [scope note](../claims/C6-SPACETIME-SIGNATURE/notes/relative-cocycle-coordinate-resolvent-zero-time-anchor-finite-checkpoint-boundary-260830.md), and saved run artefacts.
