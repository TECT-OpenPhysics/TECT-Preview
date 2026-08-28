# R-393 scope note — high-cutoff QCMI shell stress

R-393 / EXP-001236 extends R-392 by testing the QCMI shell budget on a higher
oscillator-cutoff grid.  The primary lane passed 921/921 checks, the
independent lane 6/6, the integrated verifier 23/23, and Lean R393 compiled.
There are 13 volume/cutoff systems, 54 base partitions and 304 shell rows,
with both orientations, both core widths where admissible and all four beta
values.

The cumulative QCMI range is `4.991889248628922e-07` to
`0.009400499834535836`; the maximum l1 budget is
`0.009400499834535836`; and the largest chain-rule residual is
`1.7763568394002505e-15`.  The volume-three ladder reaches oscillator
dimension ten.  Seventy-two cutoff profiles are retained.  The maximum
adjacent-cutoff ratio is `32.000137578349594`, with 62 profiles showing an
adjacent increase above one.  This records that low-cutoff suppression cannot
be extrapolated to a cutoff-independent bound.  Several beta-one profiles
settle or decrease at the higher dimensions, motivating—but not proving—a
two-stage high-cutoff plateau plus explicit spectral-tail estimate.

The product-state hostile mutation remains caught: the interacting
`V=5,d=4,beta=2` representative reaches `0.009270624713825448`, while the
product state reaches `1.7763568394002505e-15`.

The boundary is explicit: no cutoff-independent shell summability, Gibbs
complement bound, source/volume/shape uniformity, beta/eta independence,
invariant common form core, domain/Cook/common-alpha transfer, OS/KMS/GNS
reconstruction, gap, continuum, C6, Sector-A or Pre-A result follows.  C6
remains T1 ACTIVE CONDITIONAL with `C6-BCC-PREMISE-BLOCKED` open.
