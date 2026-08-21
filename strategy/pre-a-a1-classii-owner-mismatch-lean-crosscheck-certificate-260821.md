# A1 Class-II owner mismatch Lean cross-check

## Result

This is a T0, claim-nonbearing exact cross-check for `R-172` under
`EXP-000887`. The hash-pinned A1 manifest declares a K-energy numerator
`cKK beta_X^2`, whereas the historical residual uses `cJK alpha_X beta_X`.
With the registered values,

`cKK beta_X^2 = 3/320`,

`cJK alpha_X beta_X = 3/400`,

and the numerator difference is `3/1600`. Both are divided by the same
positive denominator `M_X^2 + rho_regularizer`, so the coefficient mismatch is
nonzero after the regularizer is retained.

The Lean source proves the four exact markers `numerator_fixture`,
`mass_denom_positive`, `coefficient_difference`, and
`coefficients_are_not_equal`. The primary bridge reads the A1 manifest and
hash-checks it and the Lean source. The independent bridge uses only the
standard library and `Fraction`. The integrated bridge compares both derived
records and rejects eight hostile scope or source mutations.

## Owner boundary

This is an owner-interface obstruction, not a complete variational theorem.
It does not formalise the spatial K current, divergence, integration by parts,
the full Class-II derivative, the proposed `F_ref`, the historical solver, the
canonical finite production cylinder, or the A13 joint sextic owner. The A1
standalone backend remains T5 only at its declared discrete variational-matrix
scope. The full A13 controlled-shell and progressive-revisit gates remain OPEN.

## Adversarial checks

- Factor and denominator: the common positive denominator is kept, and the
  numerator mismatch is derived from the manifest rather than copied from a
  decimal output.
- Convention: `cKK beta_X^2` and `cJK alpha_X beta_X` are distinct owner
  expressions; equality cannot be restored by the common mass denominator.
- Scope: the finite rational result is not promoted to a full field, PDE,
  minimizer, continuum, physical-vacuum, Sector-A, or Pre-A theorem.

No claim tier or lifecycle changes, no new negative result is registered, and
no R-172 PDF is issued.
