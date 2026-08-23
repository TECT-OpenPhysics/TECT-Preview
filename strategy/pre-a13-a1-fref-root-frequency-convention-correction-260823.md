# Append-only R-176 Fourier convention correction

## Decision

The canonical executable convention for future crosswalks is
`2*pi/L`, with `L=16` giving a step of `pi/8`.  The two registered R-176
roots are therefore the modes `k=(2*pi/L,0,0)` and `2k=(4*pi/L,0,0)`, with
spatial norm-squares `1` and `4`.

The historical R-176 manifest string `r+Z*(m*pi/L)^2+Y*(m*pi/L)^4` is not
edited.  It is retained as a stale formula record, because the R-174
production-cylinder manifest, the R-176 executable, and the A1 spectral
backend all use the `2*pi/L` step.  This file is an append-only convention
decision, not a rewrite of R-176.

## Crosswalk evidence

The freshly re-run crosswalk passes primary `23/23`, independent `16/16`, and
integrated `19/19`.  It gives
`q_*^2/(2*pi/16)^2 = 2.999999999993102473641602178113512365467`, so the nearest
side-16 F_ref shell has norm-square `3`, not either R-176 root norm-square.
The convention decision therefore resolves only the formula ambiguity; it
does not identify the F_ref shell with the production roots.

## Boundary

This correction does not supply `heat_root_incidence`, a root filtration,
conditional replicas, the raw-current spatial intertwiner, or the one-use
nonnegative production `q` ledger.  R-192 therefore remains open at
`heat_root_incidence`, and no A13, Sector-A, Pre-A, OS/KMS, continuum,
thermodynamic, physical-empty, or mass-gap conclusion follows.
