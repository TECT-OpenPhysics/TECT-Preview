# R-392 scope note — QCMI shell-telescoping boundary budget

R-392 / EXP-001235 extends R-391 by decomposing core--buffer--environment
information into successive QCMI shell increments.  On 12 volume/cutoff
systems and 44 base tripartitions, the primary lane passed 800/800 checks, the
independent lane 6/6, the integrated verifier 21/21, and Lean R392 compiled.
There are 264 shell rows with both orientations, both core widths and all
declared beta values.

The cumulative QCMI range is
`4.991889248628922e-07` to `0.009400499834535836`; no increment or cumulative
row is negative beyond tolerance.  The maximum l1 budget is
`0.009400499834535836`, and the largest chain-rule residual is
`1.7763568394002505e-15`.  The second shell maximum is
`0.0003382922777377395` for core width 1 and
`0.0003364013516424791` for core width 2, below the respective first-shell
maxima.  A third shell for the one-site core reaches
`1.7918838214114885e-05`.

The product-of-one-site-marginals hostile mutation has maximum increment
`1.7763568394002505e-15`, versus `0.009270624713825448` for the interacting
representative, so the mutation is caught.  This is a finite shell-accounting
identity and stress profile, not a uniform boundary theorem.

The explicit boundary remains: no uniform shell summability, Gibbs complement
bound, cutoff/source/volume/shape control, beta/eta independence, invariant
common form core, domain/Cook/common-alpha transfer, OS/KMS/GNS reconstruction,
gap, continuum, C6, Sector-A or Pre-A result follows.  C6 remains T1 ACTIVE
CONDITIONAL with `C6-BCC-PREMISE-BLOCKED` open.
