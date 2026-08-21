# A1 nonlinear mismatch: Lean cross-check

This note records the exact algebraic sub-obstruction already named in the A1
manifest.  With `rho=|Psi|^2`, the declared nonlinear density has real-gradient
coefficient `2*lambda*rho + 2*gamma*rho^2`, while the audited residual contains
`lambda*rho + gamma*rho^2`.  The pinned values are `lambda=-43/100` and
`gamma=81/50`.

The Lean entrypoint `verification/lean/Tect/A1NonlinearMismatch.lean` proves
the factor-two identity, the exact `rho=1/4` fixture, and the scalar equality
zero set.  The primary bridge and independent standard-library Fraction lane
are listed in the cross-check manifest and the integrated JSON artifact.

The result is an owner-interface obstruction only.  The separate `cKK/cJK`
Class-II mismatch, shell-measure issue, full spatial variation and all
continuum, minimizer, physical-vacuum, Sector-A and Pre-A implications remain
outside this Lean theorem.
The stored integrated JSON records the primary, independent and mutation
checks together with the pinned Lean source/toolchain hashes.
