# N-001 q0/BCC-star curvature probe (2026-07-16)

## Status and scope

This is an experimental diagnostic attached to T-033.  It does not create a
new claim, does not change a tier, and does not prove BCC existence or
nonexistence.  It asks whether the uploaded homogeneous N-001 branch has a
negative curvature direction in a commensurate q0/BCC-star perturbation
subspace.

## Method

The script `codes/foundations/n001_bcc_star_curvature.py` imports the same
external PDE solver used by the uploaded run and evaluates the solver's
matrix-free projected Hessian at the stored `Psi_star.npy`.  The Phase-2
convention is matched by removing translation zero modes and using the
unsymmetrised Hessian operator.

The full N32 probe used all six antipodal BCC `{110}` pairs.  The commensurate
integer was `m=5`, so the tested shell has `|k|=0.7142857273` versus
`q0=0.6801747616`, a relative mismatch of about `5.015%`.

## Result

All six 12-dimensional real antipodal-pair subspaces were positive:

```text
minimum Rayleigh eigenvalue = +52.12042392718455
negative directions         = 0
near-zero directions        = 0
diagnosis                   = POSITIVE_Q0_BCC_STAR_CURVATURE
```

The compact evidence file is
`reviews/2026-07-16-n001-bcc-star-curvature-n32-fullstar.json`.  The earlier
representative-pair probe is retained as
`reviews/2026-07-16-n001-bcc-star-curvature-n32-pair01.json`.

## Interpretation

This is evidence against a BCC-star bifurcation in the full commensurate N32
`{110}` star around the uploaded homogeneous branch.  It is not a theorem and
does not rule out BCC branches at other parameters, boxes, discretisations, or
seed families.  N64/N128 projected star checks remain optional follow-up work
because the uploaded N64/N128 fields were Fourier prolongations whose initial
residuals were already below tolerance.

## Next step

Record N32 full-star positivity as the current operator-level stop signal for
this parameter point.  Spend the larger runtime on N64/N128 only if a stricter
grid-transfer audit is needed.
