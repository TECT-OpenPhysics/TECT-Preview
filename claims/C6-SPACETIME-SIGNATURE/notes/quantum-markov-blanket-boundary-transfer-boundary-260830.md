# R-391 scope note — quantum-Markov blanket boundary transfer

R-391 / EXP-001234 records a finite core--buffer--environment diagnostic for
the local-marginal spectral-window route.  On 12 volume/cutoff systems, 62
tripartitions, 248 QCMI rows and 392 profile rows, the primary lane passed
1186/1186 checks, the independent lane passed 6/6 aggregate checks, the
integrated verifier passed 24/24, and Lean R391 compiled.

The QCMI range was
`1.5854872970066936e-11` to `0.009400499834534948`, with no negative row.  A
one-site-to-two-site buffer reduced the sampled maximum from
`0.009400499834534948` to `0.0003382922777386277` for a one-site core and from
`0.00931987074841345` to `0.0003364013516455877` for a two-site core.  The
largest recoverability scale was `0.13711673737757143`; the finite Petz trace
distance reached `0.024659341100353113`.  The local spectral complement still
reached tail mass `0.8377841748929882`.

The product-of-one-site-marginals hostile mutation collapsed QCMI to
`1.7763568394002505e-15` while the interacting representative reached
`0.009288543552039563`, so the mutation was caught.  This validates the finite
boundary diagnostic, not a theorem about the thermodynamic state.

The boundary is explicit: no cutoff- or volume-uniform buffer tail, Gibbs
complement estimate, beta/eta independence, source/shape uniformity, invariant
common form-core, domain/Cook/common-alpha transfer, OS/KMS/GNS reconstruction,
gap, continuum, C6, Sector-A or Pre-A result follows.  C6 remains T1 ACTIVE
CONDITIONAL with `C6-BCC-PREMISE-BLOCKED` open.
