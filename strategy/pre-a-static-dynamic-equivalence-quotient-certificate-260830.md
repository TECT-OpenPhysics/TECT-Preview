# R-448 static-dynamic equivalence quotient certificate

## Evidence and exact scope

R-448 / EXP-001321 is a T0, claim-nonbearing interface result for T-061.
It preserves the existing forward T-054 method and the additive observation-first
inverse lane. The finite fixture is the already registered two-coordinate static
signature from R-193/R-200: Hessian `(1,2)`, covariance `(1,1/2)`, and two positive
diagonal comparison factor pairs A `(1/2,1/4)` and B `(1/4,1/2)`.

The reusable relation is `d1 ~_static d2` exactly when their static signatures are
equal. Reflexivity, symmetry, and transitivity are checked in Lean, while the exact
Fraction lanes reconstruct the same quotient witness. A fixed algebraic probe
`(1,0)` gives distinct one-step proxy outputs for A and B. The label is deliberately
not physical time and no production generator is inferred.

The result therefore records existence of a non-singleton static-equivalence class
and availability of a finite separating estimand. It records non-identifiability,
not a candidate selection. Observation-error stability, regulator stability,
holdout prediction, `F_reg/F_lim/F_eff/F_obs`, source-owned dynamics, and physical
identity are all outside the scope.

## Adversarial review

1. **Method-overhaul objection — DISMISSED.** The construction is an interface over
   the existing R-193/R-200 witness; it adds no Q3LOCK table and changes no owner
   order or forward estimate.
2. **Static-fit uniqueness objection — UPHELD.** Equal static signatures do not
   select A over B. The quotient remains set-valued and the selection field is
   `NO_SELECTION_FROM_STATIC_DATA`.
3. **Finite proxy as physical time — UPHELD.** The probe is an algebraic one-step
   diagnostic only; it cannot establish a heat semigroup, real-time law or physical
   observable.
4. **Unowned dynamics promotion — UPHELD.** A source-owned generator, state,
   projection, heat-root/filtration, raw-current intertwiner and q-ledger remain
   missing. The hostile lane rejects their unearned admission.
5. **Retrospective fit as holdout prediction — UPHELD.** No holdout list or
   likelihood is supplied, so stability and prediction are explicitly not assessed.

## Reproduction and boundary

Run the primary, independent, hostile, and integrated scripts named in the manifest.
The integrated verifier also invokes the pinned direct Lean toolchain on
`verification/lean/Tect/R448.lean`. No PDF is issued at this intermediate lemma;
the next PDF remains the single gate-level synthesis checkpoint.

R-448 does not close T-061, T-054, Pre-A, Sector-A, C6, QFT, Yang--Mills, gravity,
continuum, cosmic-origin, or mass-gap gates. The next action is to use this quotient
as the intake boundary for an actual hash-pinned source-owner contract, without
adding another equivalent finite mobility witness.
