# R-406 - harmonic-extension Schur capacity decomposition

R-406 / EXP-001251 is a T0 claim-nonbearing finite checkpoint following
R-405.  It uses a Dirichlet-principle harmonic extension of the weighted
block-constant coordinates instead of the unsafe block-constant Ritz gap.

For each finite conditional momentum graph, `A=diag(pi)^(-1/2)Ldiag(pi)^(-1/2)`
is split into a weighted block span `U` and complement `V`.  Eliminating `V`
gives the Schur operator `S=A_UU-A_UV A_VV^(-1) A_VU`; the generalized coarse
gap uses the harmonic-extension norm, while the residual gap is the least
eigenvalue of `A_VV`.  The audit uses the safe finite envelope
`(1/2)min(coarse,residual)` because the two pieces are energy-orthogonal but
not assumed variance-orthogonal.

The primary passes `4267/4267` over `1030` conditional rows and `80` profiles;
independent `2114/2114`, hostile `6/6`, integrated `38/38`, and Lean R406
pass.  The full-gap range is `[0.6310329497027756, 6.229495058532403]`, the
Schur coarse range is `[0.634590321876555, 18.727067154255124]`, the residual
range is `[2.0000155411351734, 30.07649788337455]`, and the corrected finite
lower envelope is `[0.3172951609382775, 3.232260013170645]`.  All `1030` rows
show a strict naive-Ritz-over-full separation, so the uncorrected restriction
cannot be used as a lower bound.

This is a finite variational interface only.  It proves no cutoff/volume/
source/exhaustion uniformity, phase selection, common core, common alpha,
OS/KMS/GNS gap, continuum, C6, Sector-A or Pre-A closure.  The next gate is
an analytic common-core lower bound for both the Schur and residual forms,
followed by controlled phase-boundary identification and R-399 shell transfer.
