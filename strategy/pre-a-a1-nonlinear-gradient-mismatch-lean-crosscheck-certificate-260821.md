# A1 nonlinear gradient mismatch Lean cross-check

## Scope

This is a T0, claim-nonbearing cross-check of the exact scalar nonlinear core
already recorded in `A1-PFR-VARIATIONAL-MISMATCH`.  The pinned A1 manifest
uses the nonlinear density

`(lambda/2) rho^2 + (gamma/3) rho^3`

while its audited residual uses the scalar coefficient

`lambda rho + gamma rho^2`.

The real field gradient of the declared density has coefficient
`2 lambda rho + 2 gamma rho^2`.  The Lean theorem and the independent Fraction
lane prove that the declared coefficient is exactly twice the residual
coefficient, and that the manifest fixture `rho=1/4` is nonzero.

## Exact result

For the manifest values `lambda=-43/100`, `gamma=81/50`, and `rho=1/4`,

`R_exec = -1/160`,

`D F_decl = -1/80`,

and their difference is `-1/160`, so the two owners are not equal at this
registered point.  Equality occurs only at `rho=0` or `rho=43/162` in the
scalar rational model.

## Verification

The primary bridge hash-checks the A1 manifest, rejects Lean escape tokens,
checks the pinned Lake/Mathlib toolchain and compiles
`verification/lean/Tect/A1NonlinearMismatch.lean`.  The independent lane uses
only the Python standard library and `Fraction`; it does not import either
bridge.  The integrated lane compares both derived records and rejects all
eight declared hostile mutations.

## Boundary

This does not formalise the separate `cKK` versus `cJK` Class-II mismatch, the
shell-energy measure issue, the full spatial variation, historical solver
integration, a minimizer, continuum/PDE limits, physical vacuum, Sector A or
Pre-A.  It makes the existing A1 owner-interface obstruction reproducible and
does not change any tier, lifecycle, gate or negative-result status.

No PDF is issued for this intermediate cross-check.
