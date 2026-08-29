# R-425 expanded finite Q3 harmonic coarse-Schur stress

R-425 / EXP-001270 is a T0 claim-nonbearing finite stress result.  It keeps
the R-419 conditional law, projected conductance, R-422 core/tail split,
`beta={1/2,2,8}`, both orientations, `alpha=1/40` and `theta=4` fixed while
enlarging the finite sample to twelve cutoff-volume systems.

The primary run passes 4678/4678 assertions over 1488 conditional rows and
326 eligible two-block rows.  The exact finite harmonic Schur assembly gives
coarse gaps `[9.416287072814253,900.9775546526778]`, residual gaps
`[2.0277567083122383,7.874609499214968]`, and combined half-minimum envelopes
`[1.0138783541561192,3.937304749607484]`.  The largest residual reuse
difference is `9.393117395006811e-10`; the minimum harmonic probe margin is
`0.15688515408073822`.  Independent 27/27, hostile 7/7, integrated 15/15 and
Lean R425 pass.

This remains finite calibration only.  It does not establish cutoff, volume,
phase or exhaustion uniformity, a common Hamiltonian core, history transfer,
OS/KMS/GNS reconstruction, a physical sector, C6, Sector-A, Pre-A,
Yang--Mills, or a mass gap.  The support-eligibility boundary is retained:
some low-cutoff systems have no row with two core and two tail coordinates.

**Authority:** [R-425 certificate](../../strategy/pre-a-cp1-st8-q3lock-expanded-grid-schur-stress-certificate-260831.md), [machine manifest](../../strategy/pre-a-cp1-st8-q3lock-expanded-grid-schur-stress-manifest.json), [integrated run](../runs/2026-08-31-integrated-expanded_grid_schur_stress/integrated.json), and [Lean R425](../../verification/lean/Tect/R425.lean).
