# N-001 homogeneous condensate numerical review (2026-07-16)

## Status and scope

This is an **experimental numerical record**, not a new registered claim and
not a tier change. It records a nonzero, spatially homogeneous stationary
branch obtained with the N-001 Newton--Krylov workflow. It does not establish
a global minimum, full-spectrum stability, a BCC condensate, or any BCC-based
downstream conclusion.

## Recorded run

The run root is `C:\Dev\Runs\q1a_final_pubgrade_compat_v2\refinement`.
The source files used at execution were located under `C:\Dev\Codes\PDE`.
The preserved JSON manifest next to this review records the exact paths and
SHA-256 values. The raw logs retain their historical `C:\Dev\TECT\Runs`
path strings because the directories were moved after execution; raw evidence
is not rewritten.

| Grid | Projected residual | Free energy | Lowest recorded Ritz value | Phase 0 | Phase 2 | Phase 3 |
|---|---:|---:|---:|---|---|---|
| 32^3 | 8.216939e-09 | -496.6861610721 | +3.377176 | PASS | PASS (20 recorded Ritz values; 0 negative) | PASS |
| 64^3 | 8.216773e-09 | -496.6861610721 | +54.478307 | PASS | PASS (20 recorded Ritz values; 0 negative) | PASS |
| 128^3 | 8.216990e-09 | -496.6861610721 | +919.855488 | PASS | PASS (20 recorded Ritz values; 0 negative) | PASS |

The N64 and N128 fields were periodic Fourier prolongations of the coarser
field. Their initial residuals were already below the requested 1e-8
tolerance, so each stopped at Newton step zero. This confirms that the
homogeneous branch is represented consistently on these grids; it is not an
independent nonlinear convergence demonstration at each resolution.

## Independent structure audit

An audit of the three stored `Psi_star.npy` fields found, at every grid:

```text
R_mod              = 5.9589228e-05
DC Fourier fraction = 9.9999999645e-01
q0-shell fraction   = about 2.25e-21
BCC/total power     = about 1.11e-21
classification       = NONUNIFORM_BUT_NO_Q0_SHELL
```

Accordingly, this record supports a **homogeneous condensate candidate** only.
It must not be cited as evidence for BCC shell occupancy, BCC structural
selection, or Reading-H/BCC downstream consequences.

## Interpretation

The recorded branch is nontrivial, stationary to the specified projected
residual, favorable relative to the trivial vacuum in this implementation, and
locally stable only in the reported projected Ritz audit. These are useful
numerical observations. They are not a proof of unrestricted global
optimality, nor do they override the retired/refuted B3-BCC-STRUCT claim.

## Next diagnostic

Before any further BCC seed sweep, evaluate the projected Hessian/Rayleigh
curvature of this homogeneous branch on the commensurate q0/BCC-star subspace.
Positive curvature makes a BCC bifurcation unsupported at this parameter point;
negative or near-zero curvature would justify a separately scoped periodic BCC
branch search.
