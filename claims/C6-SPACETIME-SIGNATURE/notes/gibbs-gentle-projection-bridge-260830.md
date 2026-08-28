# R-395 scope note — finite Gibbs gentle spectral-complement bridge

R-395 / EXP-001238 connects the finite R-394 energy tail to a state-level
disturbance budget.  For every declared local Gibbs reduction and positive
energy projector, it computes the raw tail `tau=Tr(rho Q)` and the full trace
norm `||rho-P rho P||_1`, then checks the gentle envelope `2 sqrt(tau)` and its
Markov composition `2 sqrt(Tr(rho K)/E)`.

The primary lane passes 16,440/16,440 assertions, the independent lane 6/6,
the integrated verifier 22/22, and Lean R395 compiles.  There are 13 systems,
158 core layouts and 3,160 rows.  Tail values range from 0 to
0.857090394095672; trace disturbances range from
2.220446049250313e-16 to 0.8589478229401646.  All three inequality violation
counts are zero.  The maximum adjacent-cutoff disturbance ratio is
4.2093805087121146, so the finite bridge is not a uniform limit statement.

The hostile factor-one mutation is caught at V=5, d=4, width=2, beta=2 and
E=4: the observed disturbance is 0.029711359234405613, the genuine bound is
0.04694627015634729, and the mutated bound is 0.023473135234173644.

The result is claim-nonbearing and T0.  It supplies a composable finite input
for a future dimension-safe QCMI/Petz continuity theorem, but does not itself
close that theorem, a cutoff-independent moment bound, shell summability,
common core, Cook/common-alpha, OS/KMS/GNS, gap, continuum, C6, Sector A or
Pre-A.
