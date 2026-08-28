# R-387 anchored nested-commutator kinetic isolation

## Result-first boundary

R-387 is a T0, claim-nonbearing finite interface checkpoint under
EXP-001230.  It adds a new analytic route to the R-386 coordinate-resolvent
anchor: split each actual bond-prefix Hamiltonian as `H=T+V`, with `T` the
quadratic momentum part and `V` a polynomial in commuting positions.  For
`A_z=(i eta I-q_s)^(-1)` and a position-only bond `B`, the finite algebra is

`[V,A_z]=[B,A_z]=0`,

so the first nonzero anchored coefficient obeys

`[B,[H,A_z]]=[B,[T,A_z]]`.

The finite check does not estimate the remaining kinetic commutator in an
unbounded form domain and does not imply a thermodynamic or QFT result.

## Finite verification

The primary and non-importing independent lanes rebuild every bond prefix on
the V=2 edge and V=4 square, in forward and reverse order, for every
translated site, both nonzero resolvent imaginary parts, both adjoint seeds,
both beta values and potential scales `0,1,2`.  The primary lane passes
`1019/1019` assertions; the independent lane passes `1012/1012`.

The integrated verifier passes `46/46` and Lean R387 compiles.  The grid has
`288` beta-weighted contexts, `144` seed rows and `10` bond prefixes.  Primary
maximum residuals are:

| quantity | maximum |
|---|---:|
| `[V,A_z]` | `7.415006673014076e-16` |
| `[B,A_z]` | `2.317703490729531e-16` |
| `[H,A_z]-[T,A_z]` | `1.0801915330073514e-15` |
| nested kinetic-isolation residual | `1.5436854843327511e-15` |
| potential-scale residual | `1.984473368162697e-15` |
| two-sided weighted isolation | `7.402251795272793e-16` |

The independent maximum-field difference is `7.95529426326475e-18`.  A
hostile same-site momentum mutation `V -> V+(1/4)p_left` is separated with
minimum inner-isolation residual `0.279128784747792` and minimum nested
residual `0.364793624984`, above the `1.0e-7` threshold.

## Lean cross-check

`verification/lean/Tect/R387.lean` compiles with
`lake env lean Tect/R387.lean` and checks the abstract ring implications for
commutator addition, kinetic isolation and a commuting scaled potential.  It
does not encode the finite matrices, weighted norms, operator domains or any
limit theorem.

## Adversarial review

1. **Term-by-term split.**  The primary and independent lanes rebuild `T` and
   `V` for every actual prefix; a full-H shortcut is not used.
2. **Commuting class.**  Both resolvent adjoints and all translated seeds are
   checked.  The hostile momentum mutation breaks the coordinate hypothesis
   and is rejected.
3. **Potential dependence.**  The nested residual is tested at three
   potential scales, including zero and doubled potential, so the cancellation
   is not a one-parameter numerical accident.
4. **Finite boundary.**  The oscillator matrices are bounded truncations.
   No canonical commutation limit, form-domain estimate, or uniform bound is
   inferred.
5. **Promotion firewall.**  Phase-local BKM control, boundary-shell `l1`
   summability, all cutoff/source/volume/shape uniformities, domain embedding,
   direct `D`/`delta-D` Cook convergence, common alpha, OS/KMS/GNS, gap,
   continuum, C6, Sector-A and Pre-A remain open.

## Decision and next gate

R-387 advances the anchored route by removing all coordinate-only potentials
from its first nonzero nested commutator.  The next decisive task is an
explicit invariant resolvent/form-core estimate for `[B,[T,A_z]]` and its
modular companion, with constants tracked by boundary shell and source.  If
the kinetic coefficients are summable uniformly in cutoff, volume and shape,
the result can feed the anchored Cook integral; otherwise the failure must be
registered for this route only.  Higher time coefficients may reintroduce
`V`, so this checkpoint is not a full relative-dynamics theorem.

No negative result, tier change or proof-note PDF is issued.

**Proven in:** [manifest](pre-a-cp1-st8-q3lock-anchored-nested-commutator-kinetic-isolation-finite-checkpoint-manifest.json), [primary script](../codes/foundations/pre_a_cp1_st8_q3lock_anchored_nested_commutator_kinetic_isolation_finite_checkpoint.py), [independent script](../codes/foundations/pre_a_cp1_st8_q3lock_anchored_nested_commutator_kinetic_isolation_finite_checkpoint_independent.py), [hostile script](../codes/foundations/pre_a_cp1_st8_q3lock_anchored_nested_commutator_kinetic_isolation_finite_checkpoint_hostile.py), [integrated verifier](../codes/foundations/pre_a_cp1_st8_q3lock_anchored_nested_commutator_kinetic_isolation_finite_checkpoint_verify.py), [Lean entrypoint](../verification/lean/Tect/R387.lean), [scope note](../claims/C6-SPACETIME-SIGNATURE/notes/anchored-nested-commutator-kinetic-isolation-finite-checkpoint-boundary-260830.md), and saved run artefacts.
