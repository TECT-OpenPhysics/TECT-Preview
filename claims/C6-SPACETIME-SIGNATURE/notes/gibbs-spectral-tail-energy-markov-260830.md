# R-394 scope note — finite Gibbs spectral-tail energy Markov audit

R-394 / EXP-001237 extends R-393 by shifting each local core Hamiltonian by
its finite spectral minimum and testing positive-energy Markov bounds for the
Gibbs spectral complement.  The primary lane passed 13,281/13,281 checks, the
independent lane 6/6, the integrated verifier 22/22, and Lean R394 compiled.
There are 13 volume/cutoff systems, 158 core layouts, 3,160 rows and 240
cutoff profiles, with both orientations, both core widths and all four beta
values.

The mass tail satisfies
`tail <= Tr(rho K)/E` and the K-weighted tail satisfies
`weighted_tail <= Tr(rho K^2)/E` on every finite row, with zero violations.
The mass-tail maximum is `0.857090394095672`, the weighted-tail maximum is
`4.223723806110137`, and the largest first and second moments are
`4.247282023186985` and `29.47317200298245`.  Adjacent cutoff ratios reach
`16.93594199558396` for mass and `10.577916988017394` for the weighted tail.
The fixed energy windows therefore expose cutoff-dependent moment growth even
though the finite inequalities themselves are exact.

The hostile zero-moment mutation is caught at `V=5,d=4,beta=2`: the selected
tail is `0.19203834045679757` and the mutated bound is zero.  The boundary is
explicit: no cutoff-independent moment estimate, Gibbs complement theorem,
QCMI shell modulus, source/volume/shape uniformity, beta/eta independence,
invariant common form core, domain/Cook/common-alpha transfer, OS/KMS/GNS
reconstruction, gap, continuum, C6, Sector-A or Pre-A result follows.  C6
remains T1 ACTIVE CONDITIONAL with `C6-BCC-PREMISE-BLOCKED` open.
