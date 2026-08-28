# R-396 scope note — finite recoverability-first projected Petz transport

R-396 / EXP-001239 fixes the projected low-energy reference on each declared
finite `A-B-C` tripartition and transports its Petz recovery error back to the
unprojected Gibbs reduction.  The map is built once from the projected `BC`
and `B` marginals.  Contractivity and the triangle inequality give an explicit
finite budget with both the ABC and AB displacements.

The primary lane passes 5,961/5,961 assertions, the non-importing independent
lane 6/6, the hostile lane 3/3 and the integrated verifier 23/23; Lean R396
compiles.  There are 12 systems, 62 tripartitions and 992 rows.  The maximum
projected recovery error is `0.0246593411003531`, transported error
`0.0260340558191261`, triangle budget `1.67739253805716`, and adjacent-cutoff
transport ratio `6.91143733666218`.  All finite violation counts are zero.

The hostile omission of both displacement terms is caught: transported error
`0.00553662870328261` exceeds the mutated budget `0.00448048440142432` while
remaining below the genuine budget `0.945339672005153`.

This is a T0 claim-nonbearing finite interface.  It avoids treating trace
distance as a dimension-safe QCMI continuity theorem and leaves cutoff/source/
volume/shape uniformity, Gibbs moments, shell summability, common core,
Cook/common-alpha, OS/KMS/GNS, gap, continuum, C6, Sector A and Pre-A open.
