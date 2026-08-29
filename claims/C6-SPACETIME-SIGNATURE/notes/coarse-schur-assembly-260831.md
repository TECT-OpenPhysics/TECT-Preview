# R-424 finite two-block harmonic coarse Schur assembly

R-424 / EXP-001269 is a T0 claim-nonbearing finite interface.  It keeps the
R-419 Q3 conditional law and the R-422 core/tail split fixed, retains the two
block-constant modes, and eliminates the residual complement with the exact
finite harmonic Schur complement.  The finite lower envelope recorded by the
primary lane is `0.5*min(coarse Schur gap,residual gap)`.

Primary execution passes 1471/1471 assertions over 858 conditional rows and
114 eligible rows.  Coarse gaps are `[9.416287072814253,
900.9775546526778]`, residual gaps are `[2.0659023307146094,
7.874609499214968]`, and combined envelopes are `[1.0329511653573047,
3.937304749607484]`.  Residual reuse differs by at most
`9.393117395006811e-10`.  Independent 27/27, hostile 7/7, integrated 22/22
and Lean R424 pass.

This finite result does not establish cutoff/volume/phase/exhaustion
uniformity, a common Hamiltonian core, history transfer, OS/KMS/GNS
reconstruction, a continuum limit, C6, Sector-A, Pre-A, Yang--Mills or a
mass-gap conclusion.  The next gate is a domain-controlled analytic estimate
for the coarse Schur capacity and residual boundary budget.

**Authority:** [R-424 certificate](../../strategy/pre-a-cp1-st8-q3lock-coarse-schur-assembly-certificate-260831.md), [machine manifest](../../strategy/pre-a-cp1-st8-q3lock-coarse-schur-assembly-manifest.json), [integrated run](../runs/2026-08-31-integrated-coarse_schur_assembly/integrated.json), and [Lean R424](../../verification/lean/Tect/R424.lean).
