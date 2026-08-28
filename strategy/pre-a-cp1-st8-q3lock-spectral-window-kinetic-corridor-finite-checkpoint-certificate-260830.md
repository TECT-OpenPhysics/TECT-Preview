# R-389 spectral-window kinetic corridor

## Result-first boundary

R-389 is a T0, claim-nonbearing finite checkpoint under EXP-001232.  It
combines the R-359 fixed-energy-window idea with the R-388 kinetic target
`K=[B,[T,(i eta I-q_s)^(-1)]]`.  For a fixed spectral projector
`P_E=1_{H-min(H)<=E}`, the projected Gibbs density is
`rho_beta,E=P_E rho_beta P_E`.  Both the unnormalized two-sided seminorm and
the conditional value divided by `sqrt(Tr(rho_beta,E))` are tracked.  The
finite candidate corridor is `eta>=1` for all sampled beta values and
`E<=4`; `eta=1/2` is retained as an outside stress control.  The spectral
complement is not discarded analytically.

## Finite verification

The primary and non-importing independent lanes rebuild the V=2 edge at
cutoffs `d=3,4,5,6,8,10,12,16,20,24`, both sites, both resolvent imaginary
parts, both adjoint seeds, beta `1/4,1/2,1,2` and energy windows
`1/2,1,2,4`.  They cover 80 seed rows and 1280 projected weighted rows.  The
primary lane passes `2704/2704`, the independent lane passes `2704/2704`, and
the integrated verifier passes `48/48`.

The derived controls are:

| quantity | value |
|---|---:|
| raw operator-norm growth ratio (d=24 / d=3) | `616.8263791895746` |
| maximum raw operator norm | `769.7929363619676` |
| maximum projected weighted norm | `10.769400853001088` |
| maximum conditional projected norm | `12.651740292953878` |
| largest corridor projected tail ratio (`eta=1`) | `1.232320071019603` |
| largest corridor conditional tail ratio (`eta=1`) | `1.2552329832966966` |
| largest outside projected tail ratio (`eta=1/2`) | `2.0883741716629083` |
| minimum projected window mass | `0.13537204295091224` |

The corridor and outside ratios use the four late cutoffs `d>=12` and the
registered threshold `1.5`.  Primary and independent summary fields agree
within `6.4073191197167e-12`.

## Hostile and Lean checks

The hostile lane replaces the coordinate resolvent with a momentum resolvent
over all 80 seed contexts.  The correct coordinate commutator has maximum
residual `3.706064735360124e-14`; the momentum mutation has minimum residual
`1.0355377554099874`, above the `1.0e-7` threshold.  Lean
`verification/lean/Tect/R389.lean` compiles with
`lake env lean Tect/R389.lean` and checks only nonnegativity of the projected
seminorm proxy and the mass-plus-tail identity.

## Adversarial review

1. **Window versus full state.**  `rho_beta,E` is an unnormalized finite
   spectral contribution; the complement and global KMS transfer remain open.
2. **Normalization.**  Projected and conditional seminorms are reported
   separately, so window mass is not silently treated as one.
3. **Cutoff interpretation.**  The tail ratios use only bounded oscillator
   matrices at the ten declared dimensions and are not an asymptotic theorem.
4. **Anchor hypothesis.**  The momentum-resolvent mutation breaks the
   coordinate commutator anchor and is quantitatively rejected.
5. **QFT promotion.**  No Gibbs-tail theorem, beta/eta independence, shell
   summability, domain, Cook/common-alpha, OS/KMS/GNS, gap, continuum, C6,
   Sector-A or Pre-A result is promoted.

## Decision and next gate

R-389 advances the R-388 route by showing that a fixed low-energy projection
can make the kinetic corridor stable for every sampled beta when `eta>=1`,
while the lower-eta control remains unstable.  The next decisive analytic
gate is a cutoff- and volume-uniform estimate for the complementary Gibbs tail
plus an invariant window-to-common-core transfer.  Only after that transfer
can one test whether the `eta` damping is removable and whether the boundary
coefficients are summable for Cook/common-alpha.  Failure of this transfer
retires this spectral-window route only.

No negative result, tier change or proof-note PDF is issued.

**Proven in:** [manifest](pre-a-cp1-st8-q3lock-spectral-window-kinetic-corridor-finite-checkpoint-manifest.json), [primary script](../codes/foundations/pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint.py), [independent script](../codes/foundations/pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint_independent.py), [hostile script](../codes/foundations/pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint_hostile.py), [integrated verifier](../codes/foundations/pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint_verify.py), [Lean entrypoint](../verification/lean/Tect/R389.lean), [scope note](../claims/C6-SPACETIME-SIGNATURE/notes/spectral-window-kinetic-corridor-finite-checkpoint-boundary-260830.md), and saved run artefacts.
