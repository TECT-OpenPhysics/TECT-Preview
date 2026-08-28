# R-388 state-weighted kinetic resolvent corridor boundary

R-388 / EXP-001231 is a claim-nonbearing finite checkpoint extending the
R-387 kinetic isolation.  It evaluates
`K=[B,[T,(i eta I-q_s)^(-1)]]` on the V=2 edge at oscillator cutoffs
`3,4,5,6,8,10,12,16,20,24`, both sites, both resolvent imaginaries, both
adjoints and beta values `1/4,1/2,1,2`.  The two-sided Gibbs seminorm is
`N_beta(X)^2=Tr(rho_beta X^*X)+Tr(rho_beta XX^*)`.

The primary lane passes 409/409 assertions, the independent non-importing
lane passes 404/404, the integrated verifier passes 44/44 and Lean R388
compiles.  There are 80 seed rows and 320 weighted rows.  The raw operator
norm grows by a factor `616.8263791895753` from d=3 to d=24, reaching
`769.7929363619684`.  The maximum weighted value is `24.60012282810548`.
For the sampled late-cutoff ratios, the rows with beta `1/2,1,2` and eta `1`
are `0.6231820763515571`, `0.6728818039994496` and `0.8705457144035674`,
while beta `1/4`, eta `1/2` and beta `1/4`, eta `1` give growth ratios
`2.015532296066202` and `1.50229981401046`.  The independent maximum numeric
difference is `7.958078640513122e-13`.

The hostile momentum-resolvent mutation has minimum residual
`1.0355377554099876` (threshold `1.0e-7`); the correct coordinate commutator
has maximum residual `3.785481597218718e-14`.  Lean checks only the abstract
Jacobi and kinetic-coordinate commutator reductions.

This finite corridor does not prove operator-norm uniformity, beta or eta
independence, cutoff/source/volume/shape uniformity, a phase-local BKM or
graph estimate, boundary-shell l1 summability, domain embedding, direct D or
delta-D Cook convergence, common alpha, OS/KMS/GNS reconstruction, a gap,
continuum, C6, Sector-A or Pre-A.  No negative result, tier change or PDF is
issued.
